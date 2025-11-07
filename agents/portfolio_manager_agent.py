from typing import Dict, Any, Tuple
import json
import re
from llms import llm
from langchain.tools import tool

# Weights for decision framework
WEIGHTS = {
    'sma': 0.55,    # Foundation signal (5 vs 20-day SMA)
    'rsi': 0.20,    # Risk management
    'macd': 0.15,   # Trend confirmation
    'ml': 0.10      # Predictive enhancement
}

def _extract_prediction_return(prediction_str: str) -> float:
    """
    Extract the predicted return percentage from the prediction agent's string output.
    
    Args:
        prediction_str: String output from prediction agent
        
    Returns:
        float: Predicted return as a percentage (e.g., 2.5 for +2.5%)
    """
    try:
        # Look for pattern like "Predicted Return for Next Day: +2.50%"
        match = re.search(r'Predicted Return.*?:\s*([+-]?\d+\.\d+)%', prediction_str)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return 0.0

def _calculate_confidence(tech_analysis: Dict[str, Any], prediction: Any) -> Tuple[str, float, float]:
    """
    Calculate final decision, confidence, and position size based on weighted indicators.
    
    Args:
        tech_analysis: Dictionary containing technical indicators
        prediction: String or dict containing ML prediction data
        
    Returns:
        tuple: (decision, confidence, position_size)
    """
    # Initialize base values
    decision = 'hold'
    confidence = 0.7  # Start with neutral confidence
    
    # Extract technical indicators
    sma_signal = tech_analysis.get('simple_signal', 'hold').lower()
    rsi = tech_analysis.get('rsi')
    macd_hist = tech_analysis.get('macd', {}).get('hist', 0)
    
    # Get ML prediction if available
    ml_return = 0
    if isinstance(prediction, str):
        ml_return = _extract_prediction_return(prediction)
    elif isinstance(prediction, dict) and 'prediction' in prediction:
        ml_return = prediction['prediction']
    
    # Base decision on SMA signal (55% weight)
    if sma_signal == 'buy':
        decision = 'buy'
        confidence += 0.2 * WEIGHTS['sma']
    elif sma_signal == 'sell':
        decision = 'sell'
        confidence += 0.2 * WEIGHTS['sma']
    
    # Apply RSI overrides (20% weight)
    if rsi is not None:
        if decision == 'buy' and rsi > 75:  # Extreme overbought
            decision = 'sell'
            confidence += 0.3 * WEIGHTS['rsi']
        elif decision == 'buy' and rsi > 65:  # Approaching overbought
            decision = 'hold'
            confidence -= 0.15 * WEIGHTS['rsi']
        elif decision == 'sell' and rsi < 25:  # Extreme oversold
            decision = 'buy'
            confidence += 0.3 * WEIGHTS['rsi']
        elif decision == 'sell' and rsi < 35:  # Approaching oversold
            decision = 'hold'
            confidence -= 0.15 * WEIGHTS['rsi']
    
    # MACD confirmation (15% weight)
    if (decision == 'buy' and macd_hist > 0) or (decision == 'sell' and macd_hist < 0):
        confidence += 0.2 * WEIGHTS['macd']
    else:
        confidence -= 0.1 * WEIGHTS['macd']
    
    # ML prediction influence (10% weight)
    if abs(ml_return) > 3:  # Strong prediction
        if (ml_return > 0 and decision == 'buy') or (ml_return < 0 and decision == 'sell'):
            confidence += 0.15 * WEIGHTS['ml']
        else:
            confidence -= 0.15 * WEIGHTS['ml']
    
    # Calculate position size based on confidence
    if confidence > 0.85:
        position_size = 1.0
    elif confidence > 0.7:
        position_size = 0.8
    elif confidence > 0.5:
        position_size = 0.6
    else:
        position_size = 0.3
    
    # Ensure confidence is within bounds
    confidence = max(0.0, min(1.0, confidence))
    
    return decision, confidence, position_size

@tool("give_stock_recommendation", return_direct=False)
def give_stock_recommendation(final_results: Dict[str, Any]) -> str:
    """
    Analyze stock data using a weighted decision framework and provide recommendations.
    
    The decision is based on:
    - SMA Crossover (55% weight)
    - RSI Levels (20% weight)
    - MACD Confirmation (15% weight)
    - ML Predictions (10% weight)
    
    Args:
        final_results: Dictionary containing analysis results for each ticker
        
    Returns:
        str: Formatted recommendation with reasoning
    """
    try:
        recommendations = []
        
        for ticker, data in final_results.items():
            tech_analysis = data.get('technical_analysis', {})
            prediction = data.get('prediction_analysis', {})
            news_data = data.get('news_data', [])
            
            # Get the weighted decision
            decision, confidence, position_size = _calculate_confidence(tech_analysis, prediction)
            
            # Extract ML prediction value for display
            ml_pred_value = 'N/A'
            if isinstance(prediction, str):
                ml_return = _extract_prediction_return(prediction)
                if ml_return != 0:
                    ml_pred_value = f"{ml_return:+.2f}"
            elif isinstance(prediction, dict) and 'prediction' in prediction:
                ml_pred_value = f"{prediction['prediction']:+.2f}"
            
            # Format the recommendation
            rec = {
                'ticker': ticker,
                'decision': decision.upper(),
                'confidence': round(confidence, 2),
                'position_size': position_size,
                'reasoning': {
                    'sma_signal': tech_analysis.get('simple_signal', 'N/A'),
                    'rsi': tech_analysis.get('rsi', 'N/A'),
                    'macd_hist': tech_analysis.get('macd', {}).get('hist', 'N/A'),
                    'ml_prediction': ml_pred_value
                },
                'news': news_data
            }
            recommendations.append(rec)
        
        # Build LLM prompt with weighted framework
        prompt = """You are an elite AI portfolio manager providing detailed investment recommendations.

WEIGHTED DECISION FRAMEWORK:
- SMA Crossover (5 vs 20-day): 55% weight (Foundation signal)
- RSI Levels: 20% weight (Risk management with aggressive overrides)
- MACD Histogram: 15% weight (Trend confirmation)
- ML Prediction: 10% weight (Predictive enhancement)

RSI OVERRIDE RULES:
- RSI > 75: Extreme overbought → Force SELL
- RSI > 65: Approaching overbought → Force HOLD
- RSI < 25: Extreme oversold → Force BUY
- RSI < 35: Approaching oversold → Potential buying opportunity

For each stock, provide a comprehensive analysis in this format:

================================================================================
TICKER: [TICKER]
================================================================================

📊 RECOMMENDATION: [BUY/SELL/HOLD]
   Confidence Level: [X]%
   Suggested Position Size: [X.X]x

📈 TECHNICAL ANALYSIS BREAKDOWN:
--------------------------------------------------------------------------------

1. SMA CROSSOVER SIGNAL (Foundation - 55% Weight):
   [Explain the signal and what it means for trend]

2. RSI ANALYSIS (Risk Management - 20% Weight):
   [Explain RSI value and any overrides applied]

3. MACD CONFIRMATION (Trend Timing - 15% Weight):
   [Explain MACD histogram and momentum]

4. ML PREDICTION (Predictive Enhancement - 10% Weight):
   [Explain the ML prediction and its strength]

💡 DECISION REASONING:
--------------------------------------------------------------------------------
[Provide detailed reasoning synthesizing all indicators, explaining why this recommendation makes sense given the weighted framework, do not explicitly mention the weights provided here.]

📰 RECENT NEWS HEADLINES:
--------------------------------------------------------------------------------
[List the news headlines provided]


Now analyze the following stocks:

"""
        
        for rec in recommendations:
            ticker = rec['ticker']
            decision = rec['decision']
            confidence = rec['confidence']
            position_size = rec['position_size']
            reasoning = rec['reasoning']
            news = rec['news']
            
            prompt += f"\n{'='*80}\n"
            prompt += f"TICKER: {ticker}\n"
            prompt += f"CALCULATED RECOMMENDATION: {decision} (Confidence: {confidence:.0%}, Position Size: {position_size:.1f}x)\n\n"
            prompt += f"TECHNICAL DATA:\n"
            prompt += f"- SMA Signal: {reasoning['sma_signal']}\n"
            prompt += f"- RSI: {reasoning['rsi']}\n"
            prompt += f"- MACD Histogram: {reasoning['macd_hist']}\n"
            prompt += f"- ML Prediction: {reasoning['ml_prediction']}%\n\n"
            
            if news and len(news) > 0:
                prompt += f"NEWS HEADLINES:\n"
                for i, news_item in enumerate(news[:5], 1):
                    prompt += f"{i}. {news_item['title']}\n"
                    prompt += f"   URL: {news_item['url']}\n"
                prompt += "\n"
            else:
                prompt += "NEWS: No recent news available\n\n"
        
        prompt += "\nProvide detailed, human-readable analysis for each stock following the format above. Be professional, insightful, and explain the reasoning clearly."
        
        # Invoke LLM
        response = llm.invoke(prompt)
        llm_text = response.content if hasattr(response, 'content') else str(response)
        
        # Return both structured data and LLM text
        return json.dumps({
            'structured_data': recommendations,
            'llm_analysis': llm_text
        })
        
    except Exception as e:
        return json.dumps({
            'structured_data': [],
            'llm_analysis': f"Error generating recommendations: {str(e)}"
        })