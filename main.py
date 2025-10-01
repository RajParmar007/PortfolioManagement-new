from agents.data_ingestion_agent import get_stock_data, get_market_news, get_reddit_posts
from agents.sentiment_analyst_agent import sentiment_analysis
from agents.company_shortlisting_agent import shortlist_sector
from agents.technical_analyst_agent import technical_indicators

import os, re
import pandas as pd
import json, time
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


DATA_DIR = "data"
CACHE_EXPIRY_HOURS = 24


# --- UTILS ---

def save_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    #print(f"[INFO] Saved data to {path}")
    return path

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        #print(f"[INFO] Loaded cached data from {path}")
        return data
    return None










# --- MAIN WORKFLOW ---

if __name__ == "__main__":
    shortlist = shortlist_sector("Technology", top_n=15)
    companies = json.loads(json.dumps(shortlist, indent=2))

    top_companies = [c['symbol'] for c in companies][:3]
    print(f"[INFO] Top 3 company selected: {top_companies}\n")

    ingestion_data = {}
    for ticker in top_companies:


        # Call underlying functions
        # stock_data = get_stock_data.func(ticker)
        # if stock_data.startswith("{"):
        #     stock_data = json.loads(stock_data)

        print(f"[INFO] Fetching data for {ticker}...\n")

        # --- Caching logic for stock data ---
        stock_data = load_json(f"{ticker}_stock_data.json")
        if not stock_data:
            print(f"[INFO] No cache for {ticker} stock data. Calling API...")
            # Call underlying function
            stock_data_raw = get_stock_data.func(ticker)
            if stock_data_raw.startswith("{"):
                stock_data = json.loads(stock_data_raw)
            else:
                stock_data = {} # or handle error appropriately
            save_json(f"{ticker}_stock_data.json", stock_data)



        news_data = get_market_news.func(ticker)
        reddit_data = get_reddit_posts.func(ticker)

        # Print live
        print(f"\n=== NEWS for {ticker} ===")
        print(news_data if news_data else "No news found")

        print(f"\n=== REDDIT for {ticker} ===")
        print(reddit_data if reddit_data else "No reddit posts found")

        ingestion_data[ticker] = {
            "stock": stock_data,
            "news": news_data,
            "reddit": reddit_data,
        }
        save_json(f"{ticker}_stock_data.json", stock_data)
    # print("\n=== FINAL INGESTION DATA ===")
    # print(json.dumps(ingestion_data, indent=2))




    # --- TECHNICAL ANALYSIS ---
    technical_results = {}
    for ticker, data in ingestion_data.items():
        print(f"[INFO] Running technical analysis for {ticker}...")
        stock_data = data['stock']
        # Fix timestamps
        stock_data_fixed = {}
        for ts, values in stock_data.items():
            dt = pd.to_datetime(int(ts)//1000, unit='s')
            stock_data_fixed[str(dt.date())] = values
        
        tech_input = {"ohlc": stock_data_fixed}
        tech_result = technical_indicators.invoke(input=tech_input)
        technical_results[ticker] = tech_result
        save_json(f"{ticker}_technical.json", tech_result)
    # print("\n[INFO] Technical analysis completed.\n")
    # print(json.dumps(technical_results, indent=2))




    # --- SENTIMENT ANALYSIS ---
    sentiment_results = {}
    for ticker, data in ingestion_data.items():
        print(f"[INFO] Running sentiment analysis for {ticker}...")
        news_items = []
        for line in data['news'].strip().split("\n"):
            if ' - ' in line:
                title, url = line.rsplit(' - ', 1)
                news_items.append({"title": title.strip(), "url": url.strip()})
        
    # Process reddit data into a list of dictionaries
        reddit_posts = []
        if isinstance(data['reddit'], list):
            reddit_posts = [{"title": post.strip()} for post in data['reddit'] if isinstance(post, str) and post.strip()]

        sentiment_input = {"input": {"ticker": ticker, "news": news_items, "reddit": reddit_posts}}
        sentiment_result = sentiment_analysis.invoke(input=sentiment_input)
        sentiment_results[ticker] = sentiment_result
        save_json(f"{ticker}_sentiment.json", sentiment_result)
        # print("\n[INFO] Sentiment analysis completed.\n")
        # print(json.dumps(sentiment_results, indent=2))


    # --- PREDICTION ANALYSIS ---
    from agents.prediction_agent import get_stock_prediction
    prediction_results = {}
    for ticker in top_companies:
        print(f"[INFO] Running prediction analysis for {ticker}...")
        prediction_result = get_stock_prediction.func(ticker)
        prediction_results[ticker] = prediction_result
        save_json(f"{ticker}_prediction.json", prediction_result)


    # Create a dictionary of dictionaries to hold all the results for each company
    final_results = {}
    for ticker in top_companies: 
        final_results[ticker] = {
            "technical_analysis" : technical_results.get(ticker, {}),
            "sentiment_analysis" : sentiment_results.get(ticker, {}),   
            "prediction_analysis" : prediction_results.get(ticker, {}),
            
        }

    




    # --- PORTFOLIO MANAGEMENT / RECOMMENDATION ---
    from agents.portfolio_manager_agent import give_stock_recommendation
    recommendation = give_stock_recommendation.invoke({"final_results": final_results})

    print(final_results)

    print("\n=== FINAL RECOMMENDATION ===")
    print(recommendation)



# 2. Print the result
    print(recommendation.content)

    # # Printing only the AI output
    # if "Error in give_stock_recommendation" in recommendation:
    #     print(recommendation)
    # else:
    #     # Extracting only the relevant part using AIMessage format
    #     chat_message = ChatGoogleGenerativeAI._convert_to_message(recommendation)
    #     if isinstance(chat_message, HumanMessage):
    #         print(chat_message.content)



        