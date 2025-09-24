from langchain.tools import tool
import os
import requests
import pandas as pd
import praw
from newsapi import NewsApiClient
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")


# ---------- STOCK DATA ----------
@tool("get_stock_data", return_direct=False)
def get_stock_data(ticker: str) -> str:
    """
    Fetches daily stock data for the given ticker (last 3 years).
    Uses Alpha Vantage TIME_SERIES_DAILY with full output size, then slices 3 years.
    """
    try:
        if not ALPHA_VANTAGE_API_KEY:
            return "Error: ALPHA_VANTAGE_API_KEY not set in environment."

        url = (
            f"https://www.alphavantage.co/query?"
            f"function=TIME_SERIES_DAILY&symbol={ticker}"
            f"&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()

        if "Time Series (Daily)" not in data:
            return f"Error fetching data for {ticker}: {data.get('Note') or data.get('Error Message') or 'Unknown error'}"

        ts_data = data["Time Series (Daily)"]

        # Convert to DataFrame
        df = pd.DataFrame(ts_data).T
        df.index = pd.to_datetime(df.index)
        df.columns = ["open", "high", "low", "close", "volume"]
        df = df.astype(float)
        df = df.sort_index(ascending=False)  # latest first

        # Keep ~3 years (≈ 750 trading days)
        df = df.head(750)

        return df.to_json(orient="index")

    except Exception as e:
        return f"Error fetching stock data: {str(e)}"


# ---------- NEWS ----------
@tool("get_market_news", return_direct=False)
def get_market_news(query: str) -> str:
    """
    Fetch the most relevant business/finance news about a company or sector.
    Uses NewsAPI with filters for relevance and recency.
    """
    try:
        if not NEWS_API_KEY:
            return "Error: NEWS_API_KEY not set in environment."

        newsapi = NewsApiClient(api_key=NEWS_API_KEY)

        articles = newsapi.get_everything(q=query, language="en", sort_by="publishedAt")
        return "\n".join([f"{a['title']} - {a['url']}" for a in articles['articles'][:10]])

        # articles = newsapi.get_everything(
        #     q=f'"{query}" AND (stock OR finance OR market)',
        #     language="en",
        #     sort_by="relevancy",
        #     from_param=pd.Timestamp.now() - pd.Timedelta(days=30),  # last 30 days
        #     domains="bloomberg.com,ft.com,reuters.com,cnbc.com,wsj.com"  # filter reputable
        # )

   
    except Exception as e:
        return f"Error fetching news: {e}"


# ---------- REDDIT ----------
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

@tool("get_reddit_posts", return_direct=False)
def get_reddit_posts(keyword: str) -> str:
    """
    Fetch top Reddit posts from r/stocks, r/investing, r/wallstreetbets 
    relevant to a keyword (last 1 year, sorted by relevance).
    Returns title, score, and link for each post.
    """
    try:
        results = []
        subreddits = ["stocks", "investing", "wallstreetbets"]

        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            for post in subreddit.search(keyword, sort="relevance", limit=10):
                results.append({
                    "subreddit": sub,
                    "title": post.title,
                    "score": post.score,
                    "url": f"https://www.reddit.com{post.permalink}"
                    
                })

        if not results:
            return f"No relevant Reddit posts found for '{keyword}'"

        return results

    except Exception as e:
        return f"Error fetching Reddit posts: {str(e)}"




# if __name__ == "__main__":
#     query = "Get me AAPL stock data, latest news, and related Reddit discussions"
#     agent.run(query)




#Agent testing


# from company_shortlisting_agent import shortlist_sector
# import json

# if __name__ == "__main__":
#     shortlist = shortlist_sector("Technology", top_n=15)
#     companies = json.loads(json.dumps(shortlist, indent=2))

#     top_companies = [c['symbol'] for c in companies][:1]
#     print(f"[INFO] Top 1 company selected: {top_companies}\n")

#     ingestion_data = {}
#     for ticker in top_companies:
#         print(f"[INFO] Fetching data for {ticker}...\n")

#         # Call underlying functions
#         stock_data = get_stock_data.func(ticker)
#         if stock_data.startswith("{"):
#             stock_data = json.loads(stock_data)

#         news_data = get_market_news.func(ticker)
#         reddit_data = get_reddit_posts.func(ticker)

#         # Print live
#         print(f"\n=== NEWS for {ticker} ===")
#         print(news_data if news_data else "No news found")

#         print(f"\n=== REDDIT for {ticker} ===")
#         print(reddit_data if reddit_data else "No reddit posts found")

#         ingestion_data[ticker] = {
#             "stock": stock_data,
#             "news": news_data,
#             "reddit": reddit_data,
#         }

#     print("\n=== FINAL INGESTION DATA ===")
#     print(json.dumps(ingestion_data, indent=2))



