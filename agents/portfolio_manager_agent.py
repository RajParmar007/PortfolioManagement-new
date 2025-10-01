from langchain_core.tools import tool
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain.tools import tool
import json, re
import joblib
from typing import Any, Dict, List
from llms import llm


#Refining LLM output to give reasoning for buy/sell/hold recommendation
@tool("give_stock_recommendation", return_direct=False)
def give_stock_recommendation(final_results: dict) -> str:
    """
    Given stock technical analysis data, sentiment scores, and stock prediction data, give a buy/sell/hold recommendation with reasoning.
    Analysis should provide a brief summary of all the different analyses done and then give a final recommendation based on those analyses.
    """
    try: 
        # Invoke the llm to analyze the final results and give a recommendation
        prompt = f"""You are a financial expert. Based on the following data for various companies, provide a recommendation (buy/sell/hold) for each company along with a brief reasoning of each analyses."""
        for ticker in final_results: 
            prompt += f"\n\nTicker: {ticker}\nTechnical Analysis: {json.dumps(final_results[ticker]['technical_analysis'])}\nSentiment Analysis: {json.dumps(final_results[ticker]['sentiment_analysis'])}\nPrediction Analysis: {json.dumps(final_results[ticker]['prediction_analysis'])}\nRecommendation:"
        response = llm.invoke(prompt)
        return response
    except Exception as e:
        return f"Error in give_stock_recommendation: {str(e)}"



        