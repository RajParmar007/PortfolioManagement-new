"""
Optimized Portfolio Manager Agent for Backtesting
Streamlined version that provides only recommendations with minimal tokens
"""

import sys
import os
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llms import llm

class OptimizedPortfolioAgent:
    """
    Streamlined portfolio manager focused on quick, accurate recommendations
    """
    
    def __init__(self):
        self.llm = llm
        
    def _calculate_rule_based_scores(self, analysis_results: Dict[str, Any]) -> Dict[str, float]:
        # Calculate rule-based scores programmatically with SMA crossover emphasis
        
        scores = {}
        weights = {"technical": 0.8, "sentiment": 0.0, "prediction": 0.2}  # Maximum SMA emphasis, no sentiment
        
        for ticker, data in analysis_results.items():
            score = 0
            
            # Technical Analysis (80% weight - MAXIMUM DOMINANCE)
            tech = data.get('technical_analysis', {})
            if isinstance(tech, dict) and not tech.get('error'):
                tech_signal = tech.get('simple_signal', 'hold')
                if tech_signal == 'buy':
                    score += weights["technical"]
                elif tech_signal == 'sell':
                    score -= weights["technical"]
            
            # Prediction Analysis (20% weight)
            prediction = data.get('prediction_analysis', {})
            if isinstance(prediction, str) and "Predicted Return" in prediction:
                import re
                match = re.search(r'Predicted Return.*?([+-]?\d+\.?\d*)%', prediction)
                if match:
                    pred_return = float(match.group(1))
                    if pred_return > 2:
                        score += weights["prediction"]
                    elif pred_return < -2:
                        score -= weights["prediction"]
            
            scores[ticker] = round(score, 2)
        
        return scores
    
    def _create_hybrid_prompt(self, analysis_results: Dict[str, Any], rule_based_scores: Dict[str, float]) -> str:
        """Create prompt that shows rule-based scores and asks for LLM enhancement"""
        
        prompt = f"""You are an elite AI portfolio manager. I've calculated the rule-based scores that achieved +63% returns. Your job is to ENHANCE these scores with your advanced reasoning to beat that performance.

RULE-BASED SCORES (your starting point):
"""
        
        for ticker, score in rule_based_scores.items():
            decision = "BUY" if score > 0.3 else "SELL" if score < -0.3 else "HOLD"
            prompt += f"{ticker}: {score:+.2f} → {decision}\n"
        
        prompt += f"""
YOUR ENHANCEMENT MISSION:
1. **Start with these proven scores** - they work!
2. **Apply your intelligence** to adjust scores based on:
   - Pattern recognition across signals
   - Market context and timing
   - Risk-reward optimization
   - Signal quality and confidence

3. **Enhancement guidelines**:
   - Adjust scores by ±0.1 to ±0.3 based on your analysis
   - Be aggressive where you see clear opportunities
   - Be conservative where you detect hidden risks

4. **Final decisions**:
   - Enhanced Score > +0.3 = BUY
   - Enhanced Score < -0.3 = SELL
   - Enhanced Score -0.3 to +0.3 = HOLD

RESPOND FORMAT: TICKER: ENHANCED_SCORE → DECISION (reasoning)

ANALYSIS DATA:
"""
        
        # Add the detailed analysis data
        for ticker, data in analysis_results.items():
            prompt += f"\n{ticker} (Rule Score: {rule_based_scores[ticker]:+.2f}):\n"
            
            # Add condensed analysis info
            tech = data.get('technical_analysis', {})
            if isinstance(tech, dict) and not tech.get('error'):
                signal = tech.get('simple_signal', 'hold')
                rsi = tech.get('rsi', 50)
                prompt += f"  Technical: {signal.upper()}, RSI={rsi:.0f}\n"
            
            # Sentiment analysis removed (0% weight)
            
            prediction = data.get('prediction_analysis', {})
            if isinstance(prediction, str) and "Predicted Return" in prediction:
                import re
                match = re.search(r'Predicted Return.*?([+-]?\d+\.?\d*)%', prediction)
                if match:
                    pred_return = float(match.group(1))
                    prompt += f"  Prediction: {pred_return:+.1f}%\n"
        
        return prompt
    
    def _parse_hybrid_response(self, response: str, rule_based_scores: Dict[str, float], tickers: list) -> Dict[str, Dict[str, Any]]:
        """Parse LLM response and create final recommendations"""
        
        recommendations = {}
        
        for ticker in tickers:
            # Start with rule-based as fallback
            rule_score = rule_based_scores.get(ticker, 0)
            enhanced_score = rule_score
            confidence = 0.6
            
            # Try to extract LLM enhancement
            lines = response.split('\n')
            for line in lines:
                if ticker in line and ':' in line:
                    try:
                        # Extract enhanced score
                        import re
                        score_match = re.search(r'([+-]?\d+\.?\d*)', line)
                        if score_match:
                            enhanced_score = float(score_match.group(1))
                        
                        # Extract confidence if present
                        conf_match = re.search(r'confidence[:\s]*([0-9.]+)', line, re.IGNORECASE)
                        if conf_match:
                            confidence = float(conf_match.group(1))
                            confidence = max(0.1, min(1.0, confidence))
                    except:
                        pass
                    break
            
            # Make final decision
            if enhanced_score > 0.3:
                recommendation = "BUY"
                position_size = 0.8
            elif enhanced_score < -0.3:
                recommendation = "SELL"
                position_size = 0.8
            else:
                recommendation = "HOLD"
                position_size = 0.0
            
            recommendations[ticker] = {
                "recommendation": recommendation,
                "confidence": confidence,
                "position_size": position_size,
                "rule_based_score": rule_score,
                "enhanced_score": enhanced_score,
                "reasoning": f"Rule: {rule_score:+.2f} → Enhanced: {enhanced_score:+.2f}"
            }
        
        return recommendations
    
    def _create_optimized_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Create an optimized, sophisticated prompt with advanced decision logic"""
        
        prompt = f"""You are an elite AI portfolio manager with advanced reasoning capabilities. Your goal is to OUTPERFORM the rule-based system that achieved +63% returns and 0.328 Sharpe ratio.

ADVANCED REASONING FRAMEWORK (TECHNICAL + PREDICTION ONLY):
You have access to technical and prediction analysis only (sentiment removed):
1. **Pattern Recognition**: Identify complex market patterns across technical and prediction data
2. **Contextual Analysis**: Consider interactions between technical indicators and LSTM predictions
3. **Risk-Reward Optimization**: Balance potential returns against downside risk using technical signals
4. **Market Timing**: Use LSTM predictions for optimal entry/exit timing

INTELLIGENT SMA-BASED AI SYSTEM:
Base Strategy: SMA Crossover (proven winner) + Intelligent Enhancements
TECHNICAL ANALYSIS IS FOUNDATION:
- SMA Crossover: PRIMARY signal (5-day vs 20-day) - use as base
- RSI: CONFIRMATION signal (oversold < 35, overbought > 65)
- MACD: SUPPORTING signal (histogram confirmation)
- Prediction: CONFIDENCE BOOST only (magnitude, not direction)
Adjust dynamically based on:
- SMA signal strength and consistency
- RSI confirmation levels
- Prediction confidence magnitude
- Market conditions favoring SMA strategies

AGGRESSIVE DECISION FRAMEWORK (Beat the 63% returns):
- BUY (confidence: 0.6-0.9): ANY positive signal combination OR single strong signal
- SELL (confidence: 0.6-0.9): ANY negative signal combination OR risk management
- HOLD (confidence: 0.3-0.5): ONLY when truly neutral (avoid excessive holding)

SMA-BASED DECISION PROCESS:
1. **Start with SMA Signal** (Base/Foundation)
2. **Add RSI Confirmation** (Enhancement)
3. **Add Prediction Confidence** (Enhancement)
4. **Calculate Final Signal Strength**
5. **Make Position Sizing Decision**

TECHNICAL ENHANCEMENT STRATEGY:
- SMA_5 > SMA_20: BASE BUY signal (use SMA direction as primary)
- RSI < 35: ENHANCE BUY signal (oversold confirmation)
- RSI > 65: ENHANCE SELL signal (overbought confirmation)
- Strong Prediction Magnitude: BOOST confidence in SMA direction
- Weak Prediction Magnitude: REDUCE confidence in SMA direction

KEY ADVANTAGES OVER RULES:
1. **Nuanced Analysis**: Detect subtle patterns rules miss
2. **Context Awareness**: Consider market conditions and signal interactions  
3. **Dynamic Adaptation**: Adjust strategy based on signal quality
4. **Risk Intelligence**: Better risk-adjusted decision making

SMA-ENHANCED AI STRATEGY (BUILD ON PROVEN SMA):
- Use SMA_5 vs SMA_20 as PRIMARY directional signal (like winning SMA strategy)
- RSI < 35: ENHANCE SMA BUY signals (oversold confirmation)
- RSI > 65: ENHANCE SMA SELL signals (overbought confirmation)
- Strong prediction magnitude: BOOST confidence in SMA direction
- Multiple confirmations: HIGHER confidence and larger position sizes
- Single weak signal: LOWER confidence and smaller position sizes

DECISION HIERARCHY:
1. SMA Direction → Base signal (strongest)
2. RSI Confirmation → Enhancement (moderate)
3. Prediction Magnitude → Confidence boost (weakest)
4. Final Signal Strength → Position sizing decision

YOUR MISSION: Beat +63% returns and 0.328 Sharpe ratio by emphasizing SMA crossover signals.

RESPOND FORMAT: TICKER: RECOMMENDATION (confidence: X.X)

ANALYSIS DATA:
"""
        
        for ticker, data in analysis_results.items():
            prompt += f"\n{ticker}:\n"
            
            # Enhanced Technical Analysis with market context
            tech = data.get('technical_analysis', {})
            if isinstance(tech, dict) and not tech.get('error'):
                signal = tech.get('simple_signal', 'hold')
                rsi = tech.get('rsi', 50)
                sma_5 = tech.get('sma', {}).get(5, 0)
                sma_20 = tech.get('sma', {}).get(20, 0)
                macd_hist = tech.get('macd', {}).get('hist', 0)
                returns = tech.get('returns_lookback_pct', 0)
                volatility = tech.get('volatility_20d', 0) * 100
                
                # Advanced pattern analysis for LLM
                trend_strength = abs((sma_5 - sma_20) / sma_20 * 100) if sma_20 > 0 else 0
                rsi_extreme = "OVERSOLD_EXTREME" if rsi < 25 else "OVERBOUGHT_EXTREME" if rsi > 75 else "OVERSOLD" if rsi < 35 else "OVERBOUGHT" if rsi > 65 else "NEUTRAL"
                momentum_quality = "ACCELERATING" if abs(returns) > 7 else "STRONG" if abs(returns) > 4 else "MODERATE" if abs(returns) > 1.5 else "WEAK"
                
                # Risk assessment
                risk_level = "HIGH" if volatility > 3 else "MODERATE" if volatility > 1.5 else "LOW"
                
                prompt += f"  📈 TECHNICAL ANALYSIS:\n"
                prompt += f"    Signal: {signal.upper()} | RSI: {rsi:.0f} ({rsi_extreme})\n"
                prompt += f"    Trend Strength: {trend_strength:.1f}% | Momentum: {momentum_quality} ({returns:+.1f}%)\n"
                prompt += f"    MACD: {'BULLISH' if macd_hist > 0 else 'BEARISH'} | Risk Level: {risk_level} ({volatility:.1f}%)\n"
            else:
                prompt += f"  📈 TECHNICAL: NO_DATA\n"
            
            # Enhanced Sentiment Analysis Summary (REMOVED - 0% weight)
            # Sentiment analysis completely removed due to API unreliability
            
            # Enhanced Prediction Analysis Summary
            prediction = data.get('prediction_analysis', {})
            if isinstance(prediction, str) and "Predicted Return" in prediction:
                # Extract predicted return and price info
                import re
                return_match = re.search(r'Predicted Return.*?([+-]?\d+\.?\d*)%', prediction)
                price_match = re.search(r'Last Closing Price.*?\$(\d+\.?\d*)', prediction)
                
                if return_match:
                    pred_return = float(return_match.group(1))
                    last_price = float(price_match.group(1)) if price_match else 0
                    
                    # Advanced prediction analysis
                    magnitude = abs(pred_return)
                    direction = "BULLISH" if pred_return > 0 else "BEARISH"
                    conviction = "VERY_HIGH" if magnitude > 5 else "HIGH" if magnitude > 3 else "MODERATE" if magnitude > 1.5 else "LOW"
                    risk_reward = "EXCELLENT" if magnitude > 4 else "GOOD" if magnitude > 2.5 else "FAIR" if magnitude > 1 else "POOR"
                    
                    prompt += f"  🔮 PREDICTION ANALYSIS:\n"
                    prompt += f"    Direction: {direction} | Return: {pred_return:+.1f}% | Conviction: {conviction}\n"
                    prompt += f"    Risk/Reward: {risk_reward} | Current Price: ${last_price:.2f}\n"
                else:
                    prompt += f"  🔮 PREDICTION: UNCLEAR\n"
            else:
                prompt += f"  🔮 PREDICTION: NO_DATA\n"
        
        prompt += f"""
CRITICAL: Calculate the EXACT score using the rule-based formula, then add your LLM intelligence on top:

STEP 1 - START WITH SMA BASE (Foundation Signal):
For each ticker, get SMA direction as the primary signal

STEP 2 - ADD RSI ENHANCEMENT:
- If SMA = BUY and RSI < 35: Add +0.15 to signal
- If SMA = SELL and RSI > 65: Add -0.15 to signal

STEP 3 - ADD PREDICTION CONFIDENCE BOOST:
- Strong prediction magnitude (>3%): Add +0.05 to signal
- Moderate prediction magnitude (>2%): Add +0.03 to signal

STEP 4 - CALCULATE FINAL SIGNAL STRENGTH:
- Combine all enhancements with base SMA signal
- Higher signal strength = higher confidence and position size

STEP 5 - MAKE SMA-ENHANCED DECISION:
- Signal > +0.3 = BUY (use SMA direction)
- Signal < -0.3 = SELL (use SMA direction)
- Signal -0.3 to +0.3 = HOLD

RECOMMENDATIONS (show your score calculation):"""
        
        return prompt
    
    def _parse_llm_response(self, response: str, tickers: list) -> Dict[str, Dict[str, Any]]:
        """Parse the LLM response into structured recommendations"""
        
        recommendations = {}
        
        # Initialize with default values
        for ticker in tickers:
            recommendations[ticker] = {
                "recommendation": "HOLD",
                "confidence": 0.5,
                "reasoning": "Default due to parsing error"
            }
        
        # Parse the response
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                # Try to extract ticker and recommendation
                parts = line.split(':')
                if len(parts) >= 2:
                    potential_ticker = parts[0].strip().upper()
                    
                    # Check if this is one of our tickers
                    if potential_ticker in tickers:
                        recommendation_part = parts[1].strip()
                        
                        # Extract recommendation (including STRONG variants)
                        recommendation = "HOLD"  # default
                        position_size = 0.0  # default
                        
                        # More intelligent parsing for better LLM flexibility
                        upper_part = recommendation_part.upper()
                        
                        if "STRONG BUY" in upper_part or "VERY BULLISH" in upper_part:
                            recommendation = "BUY"
                            position_size = 1.0
                        elif "STRONG SELL" in upper_part or "VERY BEARISH" in upper_part:
                            recommendation = "SELL"
                            position_size = 1.0
                        elif "BUY" in upper_part or "BULLISH" in upper_part:
                            recommendation = "BUY"
                            position_size = 0.8  # Increased from 0.7 for better performance
                        elif "SELL" in upper_part or "BEARISH" in upper_part:
                            recommendation = "SELL"
                            position_size = 0.8  # Increased from 0.7 for better performance
                        elif "HOLD" in upper_part or "NEUTRAL" in upper_part:
                            recommendation = "HOLD"
                            position_size = 0.0
                        
                        # Extract confidence if present with better parsing
                        confidence = 0.5  # default
                        import re
                        conf_match = re.search(r'confidence[:\s]*([0-9.]+)', recommendation_part, re.IGNORECASE)
                        if conf_match:
                            try:
                                confidence = float(conf_match.group(1))
                                confidence = max(0.1, min(1.0, confidence))  # Clamp between 0.1 and 1.0
                            except ValueError:
                                confidence = 0.5
                        
                        # If no confidence found, infer from recommendation strength
                        elif "STRONG" in recommendation_part.upper() or "VERY" in recommendation_part.upper():
                            confidence = 0.8
                        elif "MODERATE" in recommendation_part.upper():
                            confidence = 0.6
                        elif "WEAK" in recommendation_part.upper():
                            confidence = 0.3
                        
                        recommendations[potential_ticker] = {
                            "recommendation": recommendation,
                            "confidence": confidence,
                            "position_size": position_size,
                            "reasoning": recommendation_part
                        }
        
        return recommendations

def test_optimized_agent():
    """Test the optimized agent with sample data"""
    
    # Sample analysis results
    sample_data = {
        "AAPL": {
            "technical_analysis": {
                "simple_signal": "buy",
                "rsi": 65,
                "sma": {"5": 150, "20": 145}
            },
            "sentiment_analysis": {
                "recommendation": "INVEST",
                "overall_score": 0.3
            },
            "prediction_analysis": "Predicted Return for Next Day: +2.5%"
        },
        "AMZN": {
            "technical_analysis": {
                "simple_signal": "sell",
                "rsi": 35,
                "sma": {"5": 140, "20": 145}
            },
            "sentiment_analysis": {
                "recommendation": "AVOID",
                "overall_score": -0.2
            },
            "prediction_analysis": "Predicted Return for Next Day: -1.8%"
        }
    }
    
    agent = OptimizedPortfolioAgent()
    result = agent.get_recommendation(sample_data)
    
    print("🧪 Testing Optimized Portfolio Agent")
    print("="*50)
    print(f"Method: {result.get('method')}")
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Recommendations:")
        for ticker, rec in result['recommendations'].items():
            print(f"  {ticker}: {rec['recommendation']} (confidence: {rec['confidence']:.2f})")
    
    print(f"\n📝 Raw Response:")
    print(result.get('raw_response', 'No response'))
    
    return result

# Integration with existing backtesting framework
def create_llm_portfolio_manager_optimized(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create hybrid LLM portfolio manager that starts with rule-based scoring then enhances with LLM
    """
    
    try:
        agent = OptimizedPortfolioAgent()
        
        # STEP 1: Calculate rule-based scores programmatically
        rule_based_scores = agent._calculate_rule_based_scores(analysis_results)
        
        # STEP 2: Create enhanced prompt with rule-based scores
        prompt = agent._create_hybrid_prompt(analysis_results, rule_based_scores)
        
        # STEP 3: Get LLM enhancement
        response = llm.invoke(prompt)
        
        # STEP 4: Parse response and combine with rule-based foundation
        recommendations = agent._parse_hybrid_response(response.content, rule_based_scores, list(analysis_results.keys()))
        
        # STEP 5: Format for backtesting framework
        summary = "Hybrid LLM Portfolio Analysis (Rule-based + AI Enhancement):\n\n"
        detailed_recommendations = {}
        
        for ticker, rec in recommendations.items():
            recommendation = rec['recommendation']
            confidence = rec['confidence']
            position_size = rec.get('position_size', 1.0)
            rule_score = rec.get('rule_based_score', 0)
            enhanced_score = rec.get('enhanced_score', rule_score)
            
            # Convert to backtesting framework format
            if recommendation == "BUY":
                base_score = confidence * 0.8 if confidence > 0.7 else confidence * 0.6
                score = base_score * position_size
            elif recommendation == "SELL":
                base_score = confidence * 0.8 if confidence > 0.7 else confidence * 0.6
                score = -base_score * position_size
            else:  # HOLD
                score = 0
            
            detailed_recommendations[ticker] = {
                "recommendation": recommendation,
                "score": score,
                "confidence": confidence,
                "position_size": position_size,
                "reasoning": [f"Rule: {rule_score:+.2f} → Enhanced: {enhanced_score:+.2f} (confidence: {confidence:.2f})"]
            }
            
            summary += f"{ticker}: {recommendation} (confidence: {confidence:.2f})\n"
        
        return {
            "recommendation": summary,
            "detailed_recommendations": detailed_recommendations,
            "method": "optimized_llm",
            "rule_based_scores": rule_based_scores,
            "raw_llm_response": response.content
        }
        
    except Exception as e:
        return {
            "method": "optimized_llm",
            "error": str(e),
            "recommendations": {ticker: {"recommendation": "HOLD", "confidence": 0.5} 
                             for ticker in analysis_results.keys()}
        }

if __name__ == "__main__":
    # Test the optimized agent
    test_optimized_agent()
