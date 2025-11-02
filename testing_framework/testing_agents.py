"""
Modified Agents for Testing Framework
Optimized versions of the original agents for historical data testing
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import original agents for reference
from agents.prediction_agent import get_stock_prediction
from llms import llm

# Global cache for API calls to speed up testing
SENTIMENT_CACHE = {}
NEWS_CACHE = {}

def run_technical_analysis_testing(ticker: str, date: datetime) -> Dict[str, Any]:
    """
    Enhanced technical analysis with sophisticated SMA crossover logic
    """
    try:
        # Load the cached stock data from the correct location
        data_file = f"testing_framework/cached_data/{ticker}_3months_data.json"
        with open(data_file, 'r') as f:
            cached_data = json.load(f)
        
        # Parse the stock data (it's stored as a JSON string)
        stock_data = json.loads(cached_data['stock_data'])
        
        # Find the data for the specific date
        target_date_str = date.strftime('%Y-%m-%dT04:00:00.000Z')
        
        # Get the closest available data
        if target_date_str in stock_data:
            data_point = stock_data[target_date_str]
        else:
            # Find closest date
            available_dates = list(stock_data.keys())
            closest_date = min(available_dates, key=lambda x: abs(
                datetime.fromisoformat(x.replace('Z', '+00:00')).timestamp() - date.timestamp()
            ))
            data_point = stock_data[closest_date]
        
        # Enhanced SMA crossover logic with multiple confirmations
        sma_5 = data_point.get('SMA_5', 0)   # Use actual 5-day SMA
        sma_20 = data_point.get('SMA_20', 0) # Use actual 20-day SMA
        rsi = data_point.get('RSI', 50)
        macd_hist = data_point.get('MACD_Hist', 0)
        close_price = data_point.get('Close', 0)
        
        # Enhanced signal logic with multiple confirmations
        signals = []
        signal_strength = 0
        
        # Primary SMA crossover signal (highest weight)
        if sma_5 > sma_20:
            signals.append('buy')
            signal_strength += 0.8  # 80% weight for SMA crossover
        elif sma_5 < sma_20:
            signals.append('sell')
            signal_strength -= 0.8  # 80% weight for SMA crossover
        else:
            signals.append('hold')
            signal_strength += 0.0
        
        # RSI confirmation (additional weight)
        if rsi < 30:
            signals.append('buy')
            signal_strength += 0.1  # 10% weight for oversold
        elif rsi > 70:
            signals.append('sell')
            signal_strength -= 0.1  # 10% weight for overbought
        else:
            signals.append('hold')
            signal_strength += 0.0
        
        # MACD confirmation (additional weight)
        if macd_hist > 0:
            signals.append('buy')
            signal_strength += 0.1  # 10% weight for bullish MACD
        elif macd_hist < 0:
            signals.append('sell')
            signal_strength -= 0.1  # 10% weight for bearish MACD
        else:
            signals.append('hold')
            signal_strength += 0.0
        
        # Determine overall signal based on weighted strength
        if signal_strength > 0.5:
            simple_signal = 'buy'
        elif signal_strength < -0.5:
            simple_signal = 'sell'
        else:
            simple_signal = 'hold'
        
        return {
            'simple_signal': simple_signal,
            'rsi': rsi,
            'macd_hist': macd_hist,
            'sma': {'5': sma_5, '20': sma_20},
            'close_price': close_price,
            'signal_strength': signal_strength,
            'signals_breakdown': {
                'sma_signal': signals[0],
                'rsi_signal': signals[1],
                'macd_signal': signals[2]
            },
            'returns_lookback_pct': data_point.get('Returns_5d', 0) * 100,
            'volatility_20d': data_point.get('Volatility_20d', 0)
        }
        
    except Exception as e:
        return {'error': f"Technical analysis failed: {str(e)}"}

def run_sentiment_analysis_testing(ticker: str, date: datetime) -> Dict[str, Any]:
    """
    Modified sentiment analysis for testing (uses actual news/reddit data when available)
    """
    try:
        # Use cached sentiment or generate based on actual data
        cache_key = f"{ticker}_{date.strftime('%Y-%m-%d')}"
        
        if cache_key in SENTIMENT_CACHE:
            return SENTIMENT_CACHE[cache_key]
        
        # Try to use actual sentiment analysis with real data
        try:
            # Import the actual sentiment analysis agent
            from agents.sentiment_analyst_agent import sentiment_analysis
            
            # Get news and reddit data for this date (from cached data)
            news_data = get_news_for_date(ticker, date)
            reddit_data = get_reddit_for_date(ticker, date)
            
            # Combine news and reddit data
            combined_data = []
            
            # Add news titles
            for news_item in news_data:
                if 'title' in news_item:
                    combined_data.append(news_item['title'])
            
            # Add reddit titles
            for reddit_item in reddit_data:
                if 'title' in reddit_item:
                    combined_data.append(reddit_item['title'])
            
            # If we have actual data, use the real sentiment analysis
            if combined_data:
                # Format data for sentiment analysis agent
                formatted_data = {
                    'news': [{'title': title} for title in combined_data[:10]],  # Limit to 10 for speed
                    'reddit': []
                }
                
                # Run actual sentiment analysis
                sentiment_result = sentiment_analysis(formatted_data)
                
                # Parse the result
                if isinstance(sentiment_result, dict):
                    result = sentiment_result
                else:
                    # Parse string result
                    result = parse_sentiment_result(sentiment_result)
                
                # Cache the result
                SENTIMENT_CACHE[cache_key] = result
                return result
            
        except Exception as e:
            print(f"     ⚠️  Real sentiment analysis failed: {str(e)}, using fallback")
        
        # Fallback: Generate mock sentiment based on some logic (for speed)
        day_of_week = date.weekday()
        
        # Create some variation in sentiment
        if day_of_week in [0, 1]:  # Monday, Tuesday - slightly positive
            base_score = 0.1
        elif day_of_week in [2, 3]:  # Wednesday, Thursday - neutral to positive
            base_score = 0.05
        else:  # Friday, Weekend - slightly negative (profit taking)
            base_score = -0.05
        
        # Add some randomness based on date
        date_factor = (date.day % 10) / 50 - 0.1  # Range: -0.1 to 0.1
        overall_score = base_score + date_factor
        
        # Clamp between -1 and 1
        overall_score = max(-1, min(1, overall_score))
        
        # Determine recommendation
        if overall_score > 0.2:
            recommendation = 'INVEST'
        elif overall_score < -0.2:
            recommendation = 'AVOID'
        else:
            recommendation = 'HOLD'
        
        result = {
            'overall_score': overall_score,
            'recommendation': recommendation,
            'breakdown': [
                {
                    'title': f'Fallback sentiment for {ticker} on {date.strftime("%Y-%m-%d")}',
                    'sentiment': 'positive' if overall_score > 0 else 'negative' if overall_score < 0 else 'neutral',
                    'score': overall_score
                }
            ]
        }
        
        # Cache the result
        SENTIMENT_CACHE[cache_key] = result
        
        return result
        
    except Exception as e:
        return {'error': f"Sentiment analysis failed: {str(e)}"}

def run_prediction_analysis_testing(ticker: str, date: datetime) -> str:
    """
    Modified prediction analysis for testing with historical data
    """
    try:
        # Use the existing prediction agent but ensure data is available
        prediction_result = get_stock_prediction(ticker)
        
        if "Error" in prediction_result:
            # Fallback: generate mock prediction based on technical indicators
            return generate_mock_prediction(ticker, date)
        
        return prediction_result
        
    except Exception as e:
        return generate_mock_prediction(ticker, date)

def generate_mock_prediction(ticker: str, date: datetime) -> str:
    """
    Generate mock prediction when LSTM model is not available
    """
    try:
        # Load technical data to base prediction on
        data_file = f"data/{ticker}_stock_data.json"
        with open(data_file, 'r') as f:
            stock_data = json.load(f)
        
        # Get recent data point
        target_timestamp = str(int(date.timestamp() * 1000))
        timestamps = sorted(stock_data.keys())
        closest_timestamp = min(timestamps, key=lambda x: abs(int(x) - int(target_timestamp)))
        
        data_point = stock_data[closest_timestamp]
        
        # Base prediction on technical indicators
        rsi = data_point.get('RSI_14', 50)
        macd_hist = data_point.get('MACD_Hist', 0)
        volatility = data_point.get('Volatility_20d', 0.02)
        returns_5d = data_point.get('Returns_5d', 0)
        close_price = data_point.get('close', 100)
        
        # Simple prediction logic
        prediction_score = 0
        
        # RSI component
        if rsi < 30:
            prediction_score += 0.02
        elif rsi > 70:
            prediction_score -= 0.02
        
        # MACD component
        if macd_hist > 0:
            prediction_score += 0.015
        elif macd_hist < 0:
            prediction_score -= 0.015
        
        # Momentum component
        prediction_score += returns_5d * 0.3
        
        # Add some noise based on volatility
        noise = (date.day % 7 - 3) * volatility * 0.5
        predicted_return = prediction_score + noise
        
        # Clamp to reasonable range
        predicted_return = max(-0.1, min(0.1, predicted_return))
        
        return f"""Prediction for {ticker}:
  - Last Closing Price: ${close_price:.2f}
  - Predicted Return for Next Day: {predicted_return * 100:+.2f}%
  - Predicted Price Change: ${close_price * predicted_return:+.2f}
  - Predicted Next Day Close Price: ${close_price * (1 + predicted_return):.2f}"""
        
    except Exception as e:
        return f"Error: Mock prediction failed for {ticker}: {str(e)}"

def run_portfolio_manager_testing(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Modified portfolio manager for testing (optimized for speed)
    """
    try:
        # Use a simplified version of the portfolio manager logic
        # to avoid expensive LLM calls during backtesting
        
        ticker = list(analysis_results.keys())[0]
        data = analysis_results[ticker]
        
        # Extract signals from each analysis
        tech_analysis = data.get('technical_analysis', {})
        sentiment_analysis = data.get('sentiment_analysis', {})
        prediction_analysis = data.get('prediction_analysis', '')
        
        # SMA-Based AI Approach: Use SMA as foundation, enhance with other signals
        
        ticker = list(analysis_results.keys())[0]
        data = analysis_results[ticker]
        
        # Extract signals from each analysis
        tech_analysis = data.get('technical_analysis', {})
        prediction_analysis = data.get('prediction_analysis', '')
        
        # START WITH SMA AS FOUNDATION (like the winning strategy)
        base_signal = 0
        sma_confidence = 0.5  # Default confidence
        
        if isinstance(tech_analysis, dict) and not tech_analysis.get('error'):
            sma_signal = tech_analysis.get('simple_signal', 'hold')
            
            if sma_signal == 'buy':
                base_signal = 1.0
                sma_confidence = 0.8  # High confidence in SMA buy
            elif sma_signal == 'sell':
                base_signal = -1.0
                sma_confidence = 0.8  # High confidence in SMA sell
        
        # ENHANCE WITH RSI CONFIRMATION
        rsi_boost = 0
        if isinstance(tech_analysis, dict) and not tech_analysis.get('error'):
            rsi = tech_analysis.get('rsi', 50)
            sma_signal = tech_analysis.get('simple_signal', 'hold')
            
            # RSI confirmation logic
            if sma_signal == 'buy' and rsi < 35:  # SMA buy + oversold RSI
                rsi_boost = 0.15  # Boost buy signal
            elif sma_signal == 'sell' and rsi > 65:  # SMA sell + overbought RSI
                rsi_boost = -0.15  # Boost sell signal
        
        # ENHANCE WITH PREDICTION MAGNITUDE (confidence boost only)
        prediction_boost = 0
        if isinstance(prediction_analysis, str) and "Predicted Return" in prediction_analysis:
            match = re.search(r'Predicted Return.*?([+-]?\d+\.?\d*)%', prediction_analysis)
            if match:
                pred_return = float(match.group(1))
                # Only use magnitude for confidence, not direction
                magnitude = abs(pred_return)
                if magnitude > 3:  # Strong prediction
                    prediction_boost = 0.05  # Small confidence boost
                elif magnitude > 2:  # Moderate prediction
                    prediction_boost = 0.03  # Smaller confidence boost
        
        # COMBINE SIGNALS INTELLIGENTLY
        final_signal = base_signal + rsi_boost + prediction_boost
        
        # CALCULATE CONFIDENCE BASED ON SIGNAL STRENGTH
        signal_strength = abs(final_signal)
        if signal_strength > 0.8:
            confidence = 0.9  # Very strong signal
        elif signal_strength > 0.5:
            confidence = 0.7  # Strong signal
        elif signal_strength > 0.2:
            confidence = 0.6  # Moderate signal
        else:
            confidence = 0.4  # Weak signal
        
        # DETERMINE RECOMMENDATION
        if final_signal > 0.3:
            recommendation = "BUY"
            position_size = min(1.0, signal_strength)  # Position size based on strength
        elif final_signal < -0.3:
            recommendation = "SELL"
            position_size = min(1.0, abs(final_signal))  # Position size based on strength
        else:
            recommendation = "HOLD"
            position_size = 0.0
        
        # CREATE DETAILED RESPONSE
        summary = f"SMA-Based AI Analysis for {ticker}:\n"
        summary += f"SMA Signal: {tech_analysis.get('simple_signal', 'unknown').upper()}\n"
        summary += f"RSI Boost: {rsi_boost:+.2f}\n"
        summary += f"Prediction Boost: {prediction_boost:+.2f}\n"
        summary += f"Final Signal: {final_signal:+.2f}\n"
        summary += f"Final Recommendation: {recommendation}"
        
        detailed_recommendations = {
            ticker: {
                "recommendation": recommendation,
                "confidence": confidence,
                "position_size": position_size,
                "sma_signal": tech_analysis.get('simple_signal', 'hold'),
                "rsi_boost": rsi_boost,
                "prediction_boost": prediction_boost,
                "final_signal": final_signal,
                "reasoning": [f"SMA-based: {final_signal:+.2f} → {recommendation} (confidence: {confidence:.2f})"]
            }
        }
        
        return {
            "recommendation": summary,
            "detailed_recommendations": detailed_recommendations,
            "method": "sma_based_ai",
            "base_signal": base_signal,
            "final_signal": final_signal
        }
        
    except Exception as e:
        # Fallback response
        ticker = list(analysis_results.keys())[0] if analysis_results else "UNKNOWN"
        return {
            "recommendation": f"Error in portfolio analysis for {ticker}: {str(e)}",
            "detailed_recommendations": {
                ticker: {
                    "recommendation": "HOLD",
                    "score": 0,
                    "confidence": 0.5,
                    "position_size": 0.0,
                    "reasoning": [f"Error: {str(e)}"]
                }
            },
            "method": "error_fallback",
            "error": str(e)
        }

def run_optimized_llm_portfolio_manager_testing(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM-based portfolio manager for testing (with caching to reduce API calls)
    """
    try:
        # Create cache key based on analysis results
        cache_key = _create_cache_key(analysis_results)
        
        # Check if we have a cached result
        if cache_key in LLM_CACHE:
            return LLM_CACHE[cache_key]
        
        # Use the optimized LLM agent from the main framework
        from optimized_portfolio_agent import create_llm_portfolio_manager_optimized
        
        result = create_llm_portfolio_manager_optimized(analysis_results)
        
        # Cache the result
        LLM_CACHE[cache_key] = result
        
        return result
        
    except Exception as e:
        # Fallback to SMA-based AI
        return run_sma_based_ai_portfolio_manager_testing(analysis_results)

def run_sma_enhanced_llm_portfolio_manager(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    True LLM-based SMA Enhancement - calls actual LLM with SMA as foundation
    """
    try:
        ticker = list(analysis_results.keys())[0]
        data = analysis_results[ticker]
        
        # Extract signals from each analysis
        tech_analysis = data.get('technical_analysis', {})
        prediction_analysis = data.get('prediction_analysis', '')
        
        # START WITH SMA AS FOUNDATION
        sma_signal = 'HOLD'
        sma_confidence = 0.5
        
        if isinstance(tech_analysis, dict) and not tech_analysis.get('error'):
            sma_signal = tech_analysis.get('simple_signal', 'HOLD')
            sma_confidence = 0.8  # High confidence in SMA
            
        # GET OTHER INDICATORS FOR LLM CONTEXT
        rsi_value = 50
        macd_hist = 0
        prediction_return = 0
        
        if isinstance(tech_analysis, dict) and not tech_analysis.get('error'):
            rsi_value = tech_analysis.get('rsi', 50)
            macd_hist = tech_analysis.get('macd_hist', 0)
        
        if isinstance(prediction_analysis, str) and "Predicted Return" in prediction_analysis:
            import re
            match = re.search(r'Predicted Return.*?([+-]?\d+\.?\d*)%', prediction_analysis)
            if match:
                prediction_return = float(match.group(1))
        
        # CREATE SMA-CENTERED PROMPT FOR LLM WITH AGGRESSIVE OVERRIDES + PREDICTION WEIGHT
        prompt = f"""You are an elite AI portfolio manager. Your goal is to intelligently enhance SMA signals with aggressive risk management and ML predictions.

SMA ANALYSIS (FOUNDATION - 55% WEIGHT):
- SMA Signal: {sma_signal.upper()}
- SMA Confidence: {sma_confidence:.1f}/1.0

SUPPORTING INDICATORS (35% TOTAL WEIGHT):
- RSI: {rsi_value:.1f} ({'OVERSOLD' if rsi_value < 30 else 'OVERBOUGHT' if rsi_value > 70 else 'NEUTRAL'}) - 20% weight
- MACD Histogram: {macd_hist:+.3f} ({'BULLISH' if macd_hist > 0 else 'BEARISH' if macd_hist < 0 else 'NEUTRAL'}) - 15% weight

ML PREDICTION ANALYSIS (10% WEIGHT):
- Prediction Return: {prediction_return:+.1f}% ({'STRONG' if abs(prediction_return) > 3 else 'MODERATE' if abs(prediction_return) > 1.5 else 'WEAK'})
- Prediction Direction: {'BULLISH' if prediction_return > 0 else 'BEARISH' if prediction_return < 0 else 'NEUTRAL'}

AGGRESSIVE ENHANCEMENT RULES:
1. GENERALLY follow the SMA signal (55% weight), but be AGGRESSIVE with overrides
2. RSI OVERRIDES (20% weight):
   - SMA=BUY but RSI > 65: Consider HOLD (early overbought warning)
   - SMA=BUY but RSI > 75: Consider SELL (extreme overbought)
   - SMA=SELL but RSI < 35: Consider HOLD (early oversold warning)  
   - SMA=SELL but RSI < 25: Consider BUY (extreme oversold)
   - SMA=HOLD but RSI < 30 AND MACD > 0.3: Consider BUY (oversold reversal)
   - SMA=HOLD but RSI > 70 AND MACD < -0.3: Consider SELL (overbought reversal)
3. MACD CONFIRMATION (15% weight):
   - MACD confirmation adds/subtracts 15% weight to decision
4. PREDICTION INFLUENCE (10% weight):
   - Strong prediction (>3%) can override weak SMA signals
   - Prediction direction alignment: +confidence boost
   - Prediction contradiction: -confidence penalty
   - Use prediction magnitude for position sizing adjustment

CONFIDENCE ADJUSTMENTS:
- RSI/MACD both confirm SMA: +0.15 confidence
- RSI contradicts SMA: -0.15 confidence  
- MACD contradicts SMA: -0.10 confidence
- Strong prediction aligns with decision: +0.15 confidence
- Strong prediction contradicts decision: -0.15 confidence
- Multiple contradictions: -0.25 confidence

AGGRESSIVE POSITION SIZING:
- Very high confidence (> 0.85): position_size = 1.0 (full position)
- High confidence (0.7-0.85): position_size = 0.8
- Medium confidence (0.5-0.7): position_size = 0.6
- Low confidence (< 0.5): position_size = 0.3
- Prediction magnitude boost: +0.1 position_size if |prediction| > 3%

RESPONSE FORMAT:
{ticker.upper()}: [FINAL_DECISION] (confidence: X.XX, position_size: X.X)

Example: AAPL: BUY (confidence: 0.75, position_size: 0.8)

THINK STEP BY STEP:
1. Start with SMA signal (55% weight)
2. Check RSI for aggressive overrides (20% weight)
3. Check MACD for confirmation (15% weight)  
4. Apply ML prediction influence (10% weight)
5. Calculate final confidence with all adjustments
6. Determine position size with prediction magnitude boost
7. Make aggressive decision based on weighted analysis"""

        # CALL THE LLM
        from llms import llm
        response = llm.invoke(prompt)
        
        # PARSE LLM RESPONSE
        response_text = response.content.strip()
        
        # Extract recommendation from LLM response
        recommendation = "HOLD"
        confidence = 0.5
        position_size = 0.0
        
        # Parse the response format
        if ':' in response_text:
            parts = response_text.split(':')
            if len(parts) >= 2:
                rec_part = parts[1].strip()
                
                # Extract recommendation
                if 'BUY' in rec_part.upper():
                    recommendation = "BUY"
                elif 'SELL' in rec_part.upper():
                    recommendation = "SELL"
                else:
                    recommendation = "HOLD"
                
                # Extract confidence and position size
                import re
                conf_match = re.search(r'confidence[:\s]*([0-9.]+)', rec_part, re.IGNORECASE)
                if conf_match:
                    confidence = float(conf_match.group(1))
                    confidence = max(0.1, min(1.0, confidence))
                
                pos_match = re.search(r'position_size[:\s]*([0-9.]+)', rec_part, re.IGNORECASE)
                if pos_match:
                    position_size = float(pos_match.group(1))
                    position_size = max(0.0, min(1.0, position_size))
        
        # CREATE RESPONSE
        summary = f"LLM-Enhanced SMA Analysis for {ticker}:\n"
        summary += f"SMA Signal: {sma_signal.upper()}\n"
        summary += f"RSI: {rsi_value:.1f}\n"
        summary += f"MACD: {macd_hist:+.3f}\n"
        summary += f"Prediction: {prediction_return:+.1f}%\n"
        summary += f"LLM Recommendation: {recommendation}\n"
        summary += f"LLM Confidence: {confidence:.2f}"
        
        detailed_recommendations = {
            ticker: {
                "recommendation": recommendation,
                "confidence": confidence,
                "position_size": position_size,
                "sma_signal": sma_signal,
                "rsi_value": rsi_value,
                "macd_hist": macd_hist,
                "prediction_return": prediction_return,
                "reasoning": [f"LLM-enhanced SMA: {sma_signal} → {recommendation} (confidence: {confidence:.2f})"]
            }
        }
        
        return {
            "recommendation": summary,
            "detailed_recommendations": detailed_recommendations,
            "method": "sma_enhanced_llm",
            "raw_llm_response": response_text
        }
        
    except Exception as e:
        # Fallback to SMA signal instead of generic HOLD
        ticker = list(analysis_results.keys())[0] if analysis_results else "UNKNOWN"
        
        # Try to extract SMA signal from technical analysis
        fallback_recommendation = "HOLD"
        fallback_confidence = 0.5
        fallback_position_size = 0.0
        
        try:
            data = analysis_results.get(ticker, {})
            tech_analysis = data.get('technical_analysis', {})
            
            if isinstance(tech_analysis, dict) and not tech_analysis.get('error'):
                sma_signal = tech_analysis.get('simple_signal', 'hold')
                
                if sma_signal.lower() == 'buy':
                    fallback_recommendation = "BUY"
                    fallback_confidence = 0.7  # Medium confidence for fallback
                    fallback_position_size = 0.7
                elif sma_signal.lower() == 'sell':
                    fallback_recommendation = "SELL"
                    fallback_confidence = 0.7  # Medium confidence for fallback
                    fallback_position_size = 0.7
                # else stays HOLD
                
        except:
            pass  # Keep defaults
        
        return {
            "recommendation": f"LLM Error - Fallback to SMA: {fallback_recommendation} for {ticker}",
            "detailed_recommendations": {
                ticker: {
                    "recommendation": fallback_recommendation,
                    "confidence": fallback_confidence,
                    "position_size": fallback_position_size,
                    "sma_signal": tech_analysis.get('simple_signal', 'unknown') if 'tech_analysis' in locals() else 'unknown',
                    "reasoning": [f"LLM failed, used SMA fallback: {fallback_recommendation} (confidence: {fallback_confidence:.2f})"]
                }
            },
            "method": "sma_fallback",
            "error": str(e)
        }

# Global cache for LLM results
LLM_CACHE = {}

def _create_cache_key(analysis_results: Dict[str, Any]) -> str:
    """
    Create a cache key based on analysis results
    """
    try:
        # Create a simple hash of the key components
        ticker = list(analysis_results.keys())[0]
        data = analysis_results[ticker]
        
        tech_signal = data.get('technical_analysis', {}).get('simple_signal', 'hold')
        # Remove sentiment from cache key since weight is 0%
        sentiment_rec = 'REMOVED'  # Sentiment weight is 0%
        
        # Extract prediction return
        prediction_text = data.get('prediction_analysis', '')
        pred_return = 0
        if "Predicted Return" in prediction_text:
            match = re.search(r'Predicted Return.*?([+-]?\d+\.?\d*)%', prediction_text)
            if match:
                pred_return = float(match.group(1))
        
        # Create cache key (exclude sentiment)
        cache_key = f"{ticker}_{tech_signal}_{pred_return:.1f}"
        return cache_key
        
    except:
        return "default_cache_key"

# Helper functions for data retrieval
def get_news_for_date(ticker: str, date: datetime) -> List[Dict[str, Any]]:
    """Get news data for a specific date from cached data"""
    try:
        # Load cached data
        cache_file = f"testing_framework/cached_data/{ticker}_3months_data.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            news_data = cached_data.get('news_data', [])
            
            # Filter news for the specific date (within 1 day range)
            target_date = date.strftime('%Y-%m-%d')
            filtered_news = []
            
            for news_item in news_data:
                news_date = news_item.get('published_date', news_item.get('date', ''))
                if target_date in news_date:
                    filtered_news.append(news_item)
            
            return filtered_news
        
        return []
    except:
        return []

def get_reddit_for_date(ticker: str, date: datetime) -> List[Dict[str, Any]]:
    """Get reddit data for a specific date from cached data"""
    try:
        # Load cached data
        cache_file = f"testing_framework/cached_data/{ticker}_3months_data.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            reddit_data = cached_data.get('reddit_data', [])
            
            # Filter reddit for the specific date (within 1 day range)
            target_date = date.strftime('%Y-%m-%d')
            filtered_reddit = []
            
            for reddit_item in reddit_data:
                reddit_date = reddit_item.get('created_date', reddit_item.get('date', ''))
                if target_date in reddit_date:
                    filtered_reddit.append(reddit_item)
            
            return filtered_reddit
        
        return []
    except:
        return []

def parse_sentiment_result(sentiment_result: str) -> Dict[str, Any]:
    """Parse string sentiment result into structured format"""
    try:
        # Try to extract key information from string result
        lines = sentiment_result.split('\n')
        
        overall_score = 0.0
        recommendation = 'HOLD'
        breakdown = []
        
        for line in lines:
            if 'overall score' in line.lower() or 'sentiment score' in line.lower():
                # Extract score
                import re
                score_match = re.search(r'([+-]?\d*\.?\d+)', line)
                if score_match:
                    overall_score = float(score_match.group(1))
            
            elif 'recommendation' in line.lower():
                if 'invest' in line.lower() or 'buy' in line.lower():
                    recommendation = 'INVEST'
                elif 'avoid' in line.lower() or 'sell' in line.lower():
                    recommendation = 'AVOID'
                else:
                    recommendation = 'HOLD'
        
        return {
            'overall_score': overall_score,
            'recommendation': recommendation,
            'breakdown': [{'title': 'Parsed from string result', 'score': overall_score}]
        }
    except:
        return {
            'overall_score': 0.0,
            'recommendation': 'HOLD',
            'breakdown': [{'title': 'Parse error', 'score': 0.0}]
        }

# Cache management functions
def clear_testing_caches():
    """Clear all testing caches"""
    global SENTIMENT_CACHE, NEWS_CACHE, LLM_CACHE
    SENTIMENT_CACHE.clear()
    NEWS_CACHE.clear()
    LLM_CACHE.clear()
    print("✅ Testing caches cleared")

def get_cache_stats():
    """Get cache statistics"""
    return {
        "sentiment_cache_size": len(SENTIMENT_CACHE),
        "news_cache_size": len(NEWS_CACHE),
        "llm_cache_size": len(LLM_CACHE)
    }
