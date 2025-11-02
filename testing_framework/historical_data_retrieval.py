"""
Historical Data Retrieval for Testing Framework
Modified versions of get_stock_data and get_reddit_posts that work with specific date ranges
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import praw
from datetime import datetime, timedelta
from dotenv import load_dotenv
from newsapi import NewsApiClient

# Load environment variables
load_dotenv()

# API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

def calculate_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates a comprehensive set of technical analysis features from an OHLCV DataFrame.
    
    Args:
        df: A pandas DataFrame with 'open', 'high', 'low', 'close', 'volume' columns
            and a DatetimeIndex, sorted in chronological order (oldest to newest).
            
    Returns:
        The original DataFrame with all the feature columns added.
    """
    
    # -- Trend Indicators --
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # -- Momentum Indicators --
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=14 - 1, min_periods=14).mean()
    avg_loss = loss.ewm(com=14 - 1, min_periods=14).mean()
    rs = avg_gain / avg_loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    df['ROC_10'] = df['close'].pct_change(periods=10) * 100
    df['MOM_10'] = df['close'].diff(periods=10)

    # -- Volatility Indicators --
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.ewm(span=14, adjust=False).mean()
    
    std_20 = df['close'].rolling(window=20).std()
    df['BB_Upper'] = df['SMA_20'] + (std_20 * 2)
    df['BB_Lower'] = df['SMA_20'] - (std_20 * 2)
    df['BB_Position'] = (df['close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
    
    # -- Volume Indicators --
    df['Volume_Ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()

    # -- Other Derived Features --
    df['Returns_1d'] = df['close'].pct_change(periods=1)
    df['Returns_5d'] = df['close'].pct_change(periods=5)
    df['Volatility_20d'] = df['Returns_1d'].rolling(window=20).std()
    df['Close_to_SMA20'] = (df['close'] - df['SMA_20']) / df['SMA_20']
    df['Close_to_SMA50'] = (df['close'] - df['SMA_50']) / df['SMA_50']
    
    # Drop intermediate columns not requested in the final feature list
    df = df.drop(columns=['MACD_Signal'])
    
    return df

def get_historical_stock_data(ticker: str, start_date: str, end_date: str) -> str:
    """
    Fetches historical stock data for a specific date range using yfinance
    and formats it to match the Alpha Vantage format expected by your agents.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        
    Returns:
        JSON string in the same format as your original get_stock_data function
    """
    try:
        # 1. Fetch data using yfinance
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            return f"Error: No data found for {ticker} between {start_date} and {end_date}"
        
        # 2. Rename columns to match your format
        df.columns = df.columns.str.lower()
        df = df.rename(columns={'adj close': 'close'})  # yfinance uses 'Adj Close'
        
        # Ensure we have the required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                return f"Error: Missing required column '{col}' for {ticker}"
        
        # 3. Calculate technical features (matching your original function)
        df = df.sort_index(ascending=True)  # Ensure chronological order
        df = calculate_all_features(df)
        
        # 4. Convert to the timestamp format your agents expect
        # Convert datetime index to millisecond timestamps
        df.index = (df.index.astype('int64') // 10**6).astype(str)  # Convert to milliseconds
        
        # 5. Final processing to match your format
        df = df.sort_index(ascending=False)  # Latest first (matching your original)
        df = df.round(4)  # Round for cleaner output
        df = df.fillna("N/A")  # Handle NaN values
        
        return df.to_json(orient="index")
        
    except Exception as e:
        return f"Error fetching historical stock data for {ticker}: {str(e)}"

def get_historical_reddit_posts(keyword: str, start_date: str, end_date: str, limit_per_sub: int = 10) -> list:
    """
    Fetch historical Reddit posts from investment subreddits for a specific date range.
    
    Args:
        keyword: Search keyword (usually stock ticker)
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        limit_per_sub: Number of posts to fetch per subreddit
        
    Returns:
        List of dictionaries with post information, or error message
    """
    try:
        # Initialize Reddit client
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
        
        # Convert date strings to timestamps for filtering
        start_timestamp = datetime.strptime(start_date, '%Y-%m-%d').timestamp()
        end_timestamp = datetime.strptime(end_date, '%Y-%m-%d').timestamp() + 86400  # Add 24 hours
        
        results = []
        subreddits = ["stocks", "investing", "wallstreetbets"]
        
        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            
            # Search posts and filter by date
            for post in subreddit.search(keyword, sort="relevance", limit=limit_per_sub * 3):  # Get more to filter
                post_timestamp = post.created_utc
                
                # Filter by date range - STRICT filtering to prevent look-ahead bias
                if start_timestamp <= post_timestamp <= end_timestamp:
                    results.append({
                        "subreddit": sub,
                        "title": post.title,
                        "score": post.score,
                        "url": f"https://www.reddit.com{post.permalink}",
                        "created_date": datetime.fromtimestamp(post_timestamp).strftime('%Y-%m-%d')
                    })
                    
                    # Stop if we have enough posts for this subreddit
                    if len([r for r in results if r["subreddit"] == sub]) >= limit_per_sub:
                        break
        
        if not results:
            return f"No relevant Reddit posts found for '{keyword}' between {start_date} and {end_date}"
        
        return results
        
    except Exception as e:
        return f"Error fetching historical Reddit posts: {str(e)}"

def get_historical_market_news(query: str, start_date: str, end_date: str) -> str:
    """
    Fetch historical business/finance news for a specific date range.
    Falls back to mock data if NewsAPI historical access is limited.
    
    Args:
        query: Search query (usually stock ticker)
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        
    Returns:
        String with news headlines and URLs, same format as original function
    """
    try:
        if not NEWS_API_KEY:
            print(f"    📰 No NewsAPI key, using mock news for {query}")
            return generate_mock_historical_news(query, start_date, end_date)

        newsapi = NewsApiClient(api_key=NEWS_API_KEY)

        # Use NewsAPI's historical search with date range
        articles = newsapi.get_everything(
            q=query, 
            language="en", 
            sort_by="publishedAt",
            from_param=start_date,
            to=end_date
        )
        
        if not articles['articles']:
            print(f"    📰 No historical news found for {query}, using mock data")
            return generate_mock_historical_news(query, start_date, end_date)
        
        # Return in the same format as your original function
        return "\n".join([f"{a['title']} - {a['url']}" for a in articles['articles'][:10]])

    except Exception as e:
        error_msg = str(e)
        if "parameterInvalid" in error_msg or "too far in the past" in error_msg:
            print(f"    📰 NewsAPI historical limit reached for {query}, using mock data")
            return generate_mock_historical_news(query, start_date, end_date)
        else:
            return f"Error fetching historical news: {e}"

def generate_mock_historical_news(ticker: str, start_date: str, end_date: str) -> str:
    """
    Generate realistic mock news headlines for backtesting consistency
    """
    
    # Create date-appropriate mock news based on general market patterns
    mock_headlines = [
        f"{ticker} reports quarterly earnings results",
        f"{ticker} stock shows strong performance amid market volatility", 
        f"Analysts upgrade {ticker} price target following positive outlook",
        f"{ticker} announces strategic partnership expansion",
        f"Market watch: {ticker} trading volume increases significantly",
        f"{ticker} management provides updated guidance for investors",
        f"Institutional investors increase {ticker} holdings",
        f"{ticker} stock resilient despite broader market concerns",
        f"Technical analysis suggests {ticker} approaching key resistance level",
        f"{ticker} dividend announcement impacts investor sentiment"
    ]
    
    # Format as news headlines with mock URLs
    formatted_news = []
    for i, headline in enumerate(mock_headlines[:5]):  # Use 5 headlines
        url = f"https://example-financial-news.com/{ticker.lower()}-news-{i+1}"
        formatted_news.append(f"{headline} - {url}")
    
    return "\n".join(formatted_news)



if __name__ == "__main__":
    # Test the functions
    print("Testing historical data retrieval...")
    
    # Test stock data
    stock_data = get_historical_stock_data("AAPL", "2024-07-01", "2024-10-01")
    print(f"Stock data length: {len(stock_data) if isinstance(stock_data, str) else 'Error'}")
    
    # Test historical news
    historical_news = get_historical_market_news("AAPL", "2024-07-01", "2024-10-01")
    print(f"Historical news: {historical_news[:100]}..." if len(historical_news) > 100 else historical_news)
    
    # Test historical Reddit
    historical_reddit = get_historical_reddit_posts("AAPL", "2024-07-01", "2024-10-01")
    print(f"Historical Reddit posts: {len(historical_reddit) if isinstance(historical_reddit, list) else 'Error'}")
    

