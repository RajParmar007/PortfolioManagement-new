from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import sys
import os

# Add the current directory to Python path to import agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing agents
from agents.company_shortlisting_agent import shortlist_sector
from agents.data_ingestion_agent import get_stock_data, get_market_news, get_reddit_posts
from agents.sentiment_analyst_agent import sentiment_analysis
from agents.technical_analyst_agent import technical_indicators
from agents.prediction_agent import get_stock_prediction
from agents.portfolio_manager_agent import give_stock_recommendation

app = FastAPI(title="Multi-Agent Investment System API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility function to clean NaN/Inf values for JSON serialization
def clean_nan_values(obj):
    """Recursively replace NaN and Inf values with None for JSON serialization"""
    import math
    
    if isinstance(obj, dict):
        return {key: clean_nan_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj

# Pydantic models for request/response
class ShortlistRequest(BaseModel):
    sector: str
    top_n: int = 15

class SentimentAnalysisRequest(BaseModel):
    ticker: str
    news: List[Dict[str, Any]]
    reddit: List[Dict[str, Any]]

class TechnicalAnalysisRequest(BaseModel):
    ticker: str
    ohlc: Dict[str, Any]

class PortfolioRecommendationRequest(BaseModel):
    final_results: Dict[str, Any]

class InvestorProfile(BaseModel):
    risk_tolerance: str
    investment_horizon: str
    preferred_sectors: List[str]

class AnalyzeCompaniesRequest(BaseModel):
    tickers: List[str]
    investor_profile: InvestorProfile

@app.get("/")
async def root():
    return {"message": "Multi-Agent Investment System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Company Shortlisting Agent
@app.post("/agents/shortlist")
async def shortlist_companies(request: ShortlistRequest):
    try:
        result = shortlist_sector(request.sector, top_n=request.top_n)
        # Clean NaN values for JSON serialization
        cleaned_result = clean_nan_values(result)
        return {"status": "success", "data": cleaned_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shortlisting failed: {str(e)}")

# Data Ingestion Agents
@app.get("/agents/stock-data/{ticker}")
async def get_stock_data_endpoint(ticker: str):
    try:
        result = get_stock_data.func(ticker)
        if result.startswith("{"):
            result = json.loads(result)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock data retrieval failed: {str(e)}")

@app.get("/agents/news/{ticker}")
async def get_news_endpoint(ticker: str):
    try:
        result = get_market_news.func(ticker)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News retrieval failed: {str(e)}")

@app.get("/agents/reddit/{ticker}")
async def get_reddit_endpoint(ticker: str):
    try:
        result = get_reddit_posts.func(ticker)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit data retrieval failed: {str(e)}")

# Sentiment Analysis Agent
@app.post("/agents/sentiment-analysis")
async def run_sentiment_analysis(request: SentimentAnalysisRequest):
    try:
        sentiment_input = {
            "input": {
                "ticker": request.ticker,
                "news": request.news,
                "reddit": request.reddit
            }
        }
        result = sentiment_analysis.invoke(input=sentiment_input)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

# Technical Analysis Agent
@app.post("/agents/technical-analysis")
async def run_technical_analysis(request: TechnicalAnalysisRequest):
    try:
        tech_input = {"ohlc": request.ohlc}
        result = technical_indicators.invoke(input=tech_input)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Technical analysis failed: {str(e)}")

# Prediction Agent
@app.get("/agents/prediction/{ticker}")
async def run_prediction_analysis(ticker: str):
    try:
        result = get_stock_prediction.func(ticker)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction analysis failed: {str(e)}")

# Portfolio Manager Agent
@app.post("/agents/portfolio-recommendation")
async def get_portfolio_recommendation_endpoint(request: PortfolioRecommendationRequest):
    try:
        result = give_stock_recommendation.invoke({"final_results": request.final_results})
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio recommendation failed: {str(e)}")

# Analyze Selected Companies Workflow
@app.post("/agents/analyze-companies")
async def analyze_companies(request: AnalyzeCompaniesRequest):
    """
    Run complete analysis on user-selected companies.
    This maintains the exact LangChain flow from main.py.
    """
    try:
        import pandas as pd
        
        selected_tickers = request.tickers
        
        # Step 1: Data Ingestion
        ingestion_data = {}
        for ticker in selected_tickers:
            stock_data_raw = get_stock_data.func(ticker)
            if stock_data_raw.startswith("{"):
                stock_data = json.loads(stock_data_raw)
            else:
                stock_data = {}
            
            news_data = get_market_news.func(ticker)
            reddit_data = get_reddit_posts.func(ticker)
            
            ingestion_data[ticker] = {
                "stock": stock_data,
                "news": news_data,
                "reddit": reddit_data,
            }
        
        # Step 2: Technical Analysis
        technical_results = {}
        for ticker, data in ingestion_data.items():
            stock_data = data['stock']
            # Fix timestamps for technical analysis
            stock_data_fixed = {}
            for ts, values in stock_data.items():
                try:
                    dt = pd.to_datetime(int(ts)//1000, unit='s')
                    stock_data_fixed[str(dt.date())] = values
                except:
                    stock_data_fixed[ts] = values
            
            tech_input = {"ohlc": stock_data_fixed}
            tech_result = technical_indicators.invoke(input=tech_input)
            technical_results[ticker] = tech_result
        
        # Step 3: Sentiment Analysis
        sentiment_results = {}
        for ticker, data in ingestion_data.items():
            news_items = []
            if isinstance(data['news'], str):
                for line in data['news'].strip().split("\n"):
                    if ' - ' in line:
                        title, url = line.rsplit(' - ', 1)
                        news_items.append({"title": title.strip(), "url": url.strip()})
            
            reddit_posts = []
            if isinstance(data['reddit'], list):
                reddit_posts = [{"title": post.strip()} for post in data['reddit'] if isinstance(post, str) and post.strip()]
            
            sentiment_input = {"input": {"ticker": ticker, "news": news_items, "reddit": reddit_posts}}
            sentiment_result = sentiment_analysis.invoke(input=sentiment_input)
            sentiment_results[ticker] = sentiment_result
        
        # Step 4: Prediction Analysis
        prediction_results = {}
        for ticker in selected_tickers:
            prediction_result = get_stock_prediction.func(ticker)
            prediction_results[ticker] = prediction_result
        
        # Step 5: Combine Results
        final_results = {}
        for ticker in selected_tickers:
            # Extract news items for this ticker
            news_items = []
            if ticker in ingestion_data and 'news' in ingestion_data[ticker]:
                news_data = ingestion_data[ticker]['news']
                if isinstance(news_data, str):
                    for line in news_data.strip().split("\n"):
                        if ' - ' in line:
                            title, url = line.rsplit(' - ', 1)
                            news_items.append({"title": title.strip(), "url": url.strip()})
            
            final_results[ticker] = {
                "technical_analysis": technical_results.get(ticker, {}),
                "sentiment_analysis": sentiment_results.get(ticker, {}),
                "prediction_analysis": prediction_results.get(ticker, {}),
                "news_data": news_items
            }
        
        # Step 6: Portfolio Management / Recommendation
        recommendation = give_stock_recommendation.invoke({"final_results": final_results})
        
        # Clean all results for JSON serialization
        response_data = {
            "ingestion_data": ingestion_data,
            "technical_analysis": technical_results,
            "sentiment_analysis": sentiment_results,
            "prediction_analysis": prediction_results,
            "final_results": final_results,
            "recommendation": recommendation
        }
        
        cleaned_data = clean_nan_values(response_data)
        
        return {
            "status": "success",
            "data": cleaned_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
