"""
Backtesting Framework for Portfolio Management System
Tests how the system would have performed on historical data
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the parent directory to the path to import your agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing agents (without modifying them)
from agents.technical_analyst_agent import technical_indicators
from agents.sentiment_analyst_agent import sentiment_analysis
from agents.prediction_agent import get_stock_prediction
from agents.portfolio_manager_agent import give_stock_recommendation

# Import our historical data retrieval functions
from historical_data_retrieval import (
    get_historical_stock_data,
    get_historical_market_news,
    get_historical_reddit_posts
)

# Import optimized LLM agent
from optimized_portfolio_agent import create_llm_portfolio_manager_optimized

class PortfolioBacktester:
    """
    Backtesting framework for the portfolio management system
    """
    
    def __init__(self, test_tickers: List[str] = None):
        self.test_tickers = test_tickers or ["AAPL", "AMZN", "ADBE"]
        self.results = {}
        
    def run_backtest(self, start_date: str, end_date: str, save_results: bool = True, method: str = "rule_based", weights: Dict[str, float] = None):
        """
        Run a complete backtest for the specified date range
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            save_results: Whether to save results to files
            method: "rule_based", "optimized_llm", or "original_llm"
            weights: Optional weights for rule-based method {"technical": 0.4, "sentiment": 0.3, "prediction": 0.3}
        """
        print(f"🚀 Starting backtest for {self.test_tickers}")
        print(f"📅 Date range: {start_date} to {end_date}")
        print(f"🤖 Method: {method}")
        if weights:
            print(f"⚖️  Weights: Technical={weights.get('technical', 0):.1f}, Sentiment={weights.get('sentiment', 0):.1f}, Prediction={weights.get('prediction', 0):.1f}")
        print("=" * 60)
        
        # Step 1: Retrieve historical data for all tickers
        historical_data = self._retrieve_historical_data(start_date, end_date)
        
        # Step 2: Run analysis agents for each ticker
        analysis_results = self._run_analysis_agents(historical_data)
        
        # Step 3: Run portfolio manager
        portfolio_recommendation = self._run_portfolio_manager(analysis_results, method, weights)
        
        # Step 4: Calculate actual performance (if we have future data)
        actual_performance = self._calculate_actual_performance(start_date, end_date)
        
        # Step 5: Compile final results
        backtest_results = {
            "backtest_info": {
                "start_date": start_date,
                "end_date": end_date,
                "tickers": self.test_tickers,
                "method": method,
                "run_timestamp": datetime.now().isoformat()
            },
            "historical_data": historical_data,
            "analysis_results": analysis_results,
            "portfolio_recommendation": portfolio_recommendation,
            "actual_performance": actual_performance
        }
        
        # Step 6: Save results if requested
        if save_results:
            self._save_backtest_results(backtest_results, start_date, end_date)
        
        # Step 7: Print summary
        self._print_backtest_summary(backtest_results)
        
        return backtest_results
    
    def _retrieve_historical_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Retrieve historical stock, news, and Reddit data"""
        print("📊 Retrieving historical data...")
        
        historical_data = {}
        
        for ticker in self.test_tickers:
            print(f"  Fetching data for {ticker}...")
            
            # Get stock data
            stock_data = get_historical_stock_data(ticker, start_date, end_date)
            
            # Get news data
            news_data = get_historical_market_news(ticker, start_date, end_date)
            
            # Get Reddit data
            reddit_data = get_historical_reddit_posts(ticker, start_date, end_date)
            
            historical_data[ticker] = {
                "stock": stock_data,
                "news": news_data,
                "reddit": reddit_data
            }
            
            print(f"    ✅ {ticker} data retrieved")
        
        return historical_data
    
    def _run_analysis_agents(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run technical, sentiment, and prediction analysis for each ticker"""
        print("\n🔍 Running analysis agents...")
        
        analysis_results = {}
        
        for ticker, data in historical_data.items():
            print(f"  Analyzing {ticker}...")
            
            ticker_results = {}
            
            # Technical Analysis
            try:
                if data["stock"].startswith("{"):
                    stock_data = json.loads(data["stock"])
                    # Fix timestamps for technical analysis
                    stock_data_fixed = {}
                    for ts, values in stock_data.items():
                        dt = pd.to_datetime(int(ts)//1000, unit='s')
                        stock_data_fixed[str(dt.date())] = values
                    
                    tech_input = {"ohlc": stock_data_fixed}
                    tech_result = technical_indicators.invoke(input=tech_input)
                    ticker_results["technical_analysis"] = tech_result
                    print(f"    ✅ Technical analysis completed")
                else:
                    ticker_results["technical_analysis"] = {"error": data["stock"]}
                    print(f"    ❌ Technical analysis failed: {data['stock'][:100]}...")
            except Exception as e:
                ticker_results["technical_analysis"] = {"error": str(e)}
                print(f"    ❌ Technical analysis error: {str(e)}")
            
            # Sentiment Analysis
            try:
                # Process news data into the format expected by sentiment agent
                news_items = []
                if isinstance(data['news'], str) and not data['news'].startswith("Error"):
                    for line in data['news'].strip().split("\n"):
                        if ' - ' in line:
                            title, url = line.rsplit(' - ', 1)
                            news_items.append({"title": title.strip(), "url": url.strip()})
                
                # Process reddit data
                reddit_posts = []
                if isinstance(data['reddit'], list):
                    reddit_posts = [{"title": post.get("title", "")} for post in data['reddit'] if isinstance(post, dict)]
                elif isinstance(data['reddit'], str) and not data['reddit'].startswith("Error"):
                    # If it's a string, treat as simple titles
                    reddit_posts = [{"title": data['reddit']}]
                
                sentiment_input = {"input": {"ticker": ticker, "news": news_items, "reddit": reddit_posts}}
                sentiment_result = sentiment_analysis.invoke(input=sentiment_input)
                ticker_results["sentiment_analysis"] = sentiment_result
                print(f"    ✅ Sentiment analysis completed")
            except Exception as e:
                ticker_results["sentiment_analysis"] = {"error": str(e)}
                print(f"    ❌ Sentiment analysis error: {str(e)}")
            
            # Prediction Analysis
            try:
                # First, we need to save the stock data in the format expected by prediction agent
                if data["stock"].startswith("{"):
                    # Create a temporary file for the prediction agent
                    temp_file_path = f"testing_framework/temp_{ticker}_stock_data.json"
                    with open(temp_file_path, 'w') as f:
                        f.write(data["stock"])
                    
                    # Temporarily modify the prediction agent's data path (copy the function)
                    prediction_result = self._get_stock_prediction_backtest(ticker, temp_file_path)
                    ticker_results["prediction_analysis"] = prediction_result
                    
                    # Clean up temp file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    
                    print(f"    ✅ Prediction analysis completed")
                else:
                    ticker_results["prediction_analysis"] = {"error": data["stock"]}
                    print(f"    ❌ Prediction analysis failed: no valid stock data")
            except Exception as e:
                ticker_results["prediction_analysis"] = {"error": str(e)}
                print(f"    ❌ Prediction analysis error: {str(e)}")
            
            analysis_results[ticker] = ticker_results
        
        return analysis_results
    
    def _get_stock_prediction_backtest(self, ticker: str, temp_data_path: str) -> str:
        """
        Modified version of get_stock_prediction that uses our temporary data file
        This is a copy of your prediction agent logic with modified data path
        """
        try:
            import torch
            import torch.nn as nn
            import pickle
            import numpy as np
            import pandas as pd
            import json
            
            # Model cache
            MODELS_CACHE = {}
            SCALERS_CACHE = {}
            
            # LSTM Model Architecture (copied from your prediction_agent.py)
            class BalancedLSTM(nn.Module):
                def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
                    super(BalancedLSTM, self).__init__()
                    self.hidden_size = hidden_size
                    self.num_layers = num_layers
                    self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                                        batch_first=True, dropout=dropout if num_layers > 1 else 0)
                    self.dropout = nn.Dropout(dropout)
                    self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
                    self.relu = nn.ReLU()
                    self.fc2 = nn.Linear(hidden_size // 2, output_size)

                def forward(self, x):
                    h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                    c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                    out, _ = self.lstm(x, (h0, c0))
                    out = self.dropout(out[:, -1, :])
                    out = self.fc1(out)
                    out = self.relu(out)
                    out = self.fc2(out)
                    return out
            
            device = torch.device('cpu')
            
            # Load Model and Scalers
            if ticker not in MODELS_CACHE:
                MODEL_PATH = f'external_utils/{ticker}_balanced_lstm.pth'
                SCALER_PATH = f'external_utils/{ticker}_balanced_scalers.pkl'
                
                if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
                    return f"Error: No prediction model available for {ticker}"
                
                # Load Model
                model_data = torch.load(MODEL_PATH, map_location=device)
                model_config = model_data['model_config']
                model_state_dict = model_data['model_state_dict']
                
                model = BalancedLSTM(
                    input_size=model_config['input_size'], hidden_size=model_config['hidden_size'],
                    num_layers=model_config['num_layers'], output_size=model_config['output_size'],
                    dropout=model_config['dropout']
                )
                model.load_state_dict(model_state_dict)
                model.to(device)
                model.eval()
                MODELS_CACHE[ticker] = model

                # Load Scalers
                with open(SCALER_PATH, 'rb') as f:
                    SCALERS_CACHE[ticker] = pickle.load(f)
            
            model = MODELS_CACHE[ticker]
            scalers = SCALERS_CACHE[ticker]
            
            X_mean, X_std = scalers['X_mean'], scalers['X_std']
            y_mean, y_std = scalers['y_mean'], scalers['y_std']
            features, time_steps = scalers['features'], scalers['time_steps']

            # Load and Prepare Data from our temporary JSON file
            with open(temp_data_path, 'r') as f:
                stock_data = json.load(f)

            data = pd.DataFrame.from_dict(stock_data, orient='index')
            data.index = pd.to_datetime(data.index.to_series().astype(float), unit='ms')
            data = data.apply(pd.to_numeric, errors='coerce')
            data.sort_index(inplace=True)
            data.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low', 
                'volume': 'Volume', 'close': 'Close'
            }, inplace=True)
            
            data = data.tail(50).copy()
            data_features = data[features].copy()
            data_features.dropna(inplace=True)

            if len(data_features) < time_steps:
                return f"Error: Not enough data for {ticker} to form a {time_steps}-day sequence."

            # Isolate, Scale, and Predict
            last_sequence_df = data_features.tail(time_steps)
            scaled_sequence = (last_sequence_df.values - X_mean) / X_std
            input_tensor = torch.tensor(scaled_sequence, dtype=torch.float32).unsqueeze(0).to(device)

            with torch.no_grad():
                scaled_prediction = model(input_tensor)

            # Inverse Transform and Format Results
            predicted_return = scaled_prediction.item() * y_std + y_mean
            last_close_price = data['Close'].iloc[-1]
            predicted_price = last_close_price * (1 + predicted_return)
            price_change = predicted_price - last_close_price
            
            result = (
                f"Prediction for {ticker}:\n"
                f"  - Last Closing Price: ${last_close_price:.2f}\n"
                f"  - Predicted Return for Next Day: {predicted_return * 100:+.2f}%\n"
                f"  - Predicted Price Change: ${price_change:+.2f}\n"
                f"  - Predicted Next Day Close Price: ${predicted_price:.2f}"
            )
            return result

        except Exception as e:
            return f"Error in prediction for {ticker}: {str(e)}"
    
    def _run_portfolio_manager(self, analysis_results: Dict[str, Any], method: str = "rule_based", weights: Dict[str, float] = None) -> Any:
        """Run the portfolio manager with all analysis results"""
        if method == "rule_based":
            weight_str = f" (weights: {weights})" if weights else ""
            print(f"\n💼 Running rule-based portfolio manager{weight_str}...")
            return self._run_rule_based_portfolio_manager(analysis_results, weights)
        elif method == "optimized_llm":
            print("\n💼 Running optimized LLM portfolio manager...")
            return self._run_optimized_llm_portfolio_manager(analysis_results)
        elif method == "original_llm":
            print("\n💼 Running original LLM portfolio manager...")
            return self._run_original_llm_portfolio_manager(analysis_results)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'rule_based', 'optimized_llm', or 'original_llm'")
    
    def _run_rule_based_portfolio_manager(self, analysis_results: Dict[str, Any], weights: Dict[str, float] = None) -> Dict[str, Any]:
        """Fast rule-based portfolio manager with configurable weights"""
        try:
            # Default weights (current best performing)
            if weights is None:
                weights = {"technical": 0.4, "sentiment": 0.3, "prediction": 0.3}
            
            recommendations = {}
            
            for ticker in self.test_tickers:
                data = analysis_results.get(ticker, {})
                score = 0
                reasoning = []
                
                # Technical Analysis Weight
                tech = data.get('technical_analysis', {})
                if isinstance(tech, dict) and not tech.get('error'):
                    tech_signal = tech.get('simple_signal', 'hold')
                    if tech_signal == 'buy':
                        score += weights["technical"]
                        reasoning.append(f"Technical: BUY signal (+{weights['technical']})")
                    elif tech_signal == 'sell':
                        score -= weights["technical"]
                        reasoning.append(f"Technical: SELL signal (-{weights['technical']})")
                    else:
                        reasoning.append("Technical: HOLD signal (0)")
                else:
                    reasoning.append("Technical: No data")
                
                # Sentiment Analysis Weight
                sentiment = data.get('sentiment_analysis', {})
                if isinstance(sentiment, dict) and not sentiment.get('error'):
                    sentiment_rec = sentiment.get('recommendation', 'HOLD')
                    sentiment_score = sentiment.get('overall_score', 0)
                    
                    if sentiment_rec == 'INVEST':
                        score += weights["sentiment"]
                        reasoning.append(f"Sentiment: POSITIVE (+{weights['sentiment']}) ({sentiment_score:.2f})")
                    elif sentiment_rec == 'AVOID':
                        score -= weights["sentiment"]
                        reasoning.append(f"Sentiment: NEGATIVE (-{weights['sentiment']}) ({sentiment_score:.2f})")
                    else:
                        reasoning.append(f"Sentiment: NEUTRAL (0) ({sentiment_score:.2f})")
                else:
                    reasoning.append("Sentiment: No data")
                
                # Prediction Analysis Weight
                prediction = data.get('prediction_analysis', {})
                if isinstance(prediction, str) and "Predicted Return" in prediction:
                    # Extract predicted return percentage
                    import re
                    match = re.search(r'Predicted Return.*?([+-]?\d+\.?\d*)%', prediction)
                    if match:
                        pred_return = float(match.group(1))
                        if pred_return > 2:
                            score += weights["prediction"]
                            reasoning.append(f"Prediction: BULLISH (+{weights['prediction']}) (+{pred_return}%)")
                        elif pred_return < -2:
                            score -= weights["prediction"]
                            reasoning.append(f"Prediction: BEARISH (-{weights['prediction']}) ({pred_return}%)")
                        else:
                            reasoning.append(f"Prediction: NEUTRAL (0) ({pred_return}%)")
                    else:
                        reasoning.append("Prediction: Could not parse")
                else:
                    reasoning.append("Prediction: No data")
                
                # Ultra-selective thresholds for Sharpe ≥ 1.0
                abs_score = abs(score)
                
                # Only trade on extremely strong signals
                if score > 0.7:  # Very strong buy (all signals align)
                    recommendation = "BUY"
                    position_size = 1.0  # Full position for very strong signals
                elif score < -0.7:  # Very strong sell
                    recommendation = "SELL"
                    position_size = 1.0
                elif score > 0.5:  # Strong buy
                    recommendation = "BUY"
                    position_size = 0.7  # Reduced position
                elif score < -0.5:  # Strong sell
                    recommendation = "SELL"
                    position_size = 0.7
                else:
                    recommendation = "HOLD"  # Much more conservative
                    position_size = 0
                
                recommendations[ticker] = {
                    "recommendation": recommendation,
                    "score": round(score, 2),
                    "position_size": position_size if 'position_size' in locals() else 1.0,
                    "reasoning": reasoning
                }
            
            # Format similar to LLM output
            summary = f"Rule-Based Portfolio Analysis:\n\n"
            for ticker, rec in recommendations.items():
                summary += f"{ticker}: {rec['recommendation']} (Score: {rec['score']})\n"
                for reason in rec['reasoning']:
                    summary += f"  - {reason}\n"
                summary += "\n"
            
            print("✅ Rule-based recommendation generated")
            
            return {
                "recommendation": summary,
                "detailed_recommendations": recommendations,
                "method": "rule_based"
            }
            
        except Exception as e:
            error_msg = f"Error in rule-based portfolio manager: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def _run_optimized_llm_portfolio_manager(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Optimized LLM-based portfolio manager with focused prompt"""
        try:
            # Format results for optimized LLM agent
            formatted_results = {}
            for ticker in self.test_tickers:
                formatted_results[ticker] = {
                    "technical_analysis": analysis_results.get(ticker, {}).get("technical_analysis", {}),
                    "sentiment_analysis": analysis_results.get(ticker, {}).get("sentiment_analysis", {}),
                    "prediction_analysis": analysis_results.get(ticker, {}).get("prediction_analysis", {}),
                }
            
            # Call optimized LLM portfolio manager
            result = create_llm_portfolio_manager_optimized(formatted_results)
            print("✅ Optimized LLM recommendation generated")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in optimized LLM portfolio manager: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def _run_original_llm_portfolio_manager(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Original LLM-based portfolio manager"""
        try:
            # Format results for portfolio manager (same format as your main.py)
            final_results = {}
            for ticker in self.test_tickers:
                final_results[ticker] = {
                    "technical_analysis": analysis_results.get(ticker, {}).get("technical_analysis", {}),
                    "sentiment_analysis": analysis_results.get(ticker, {}).get("sentiment_analysis", {}),
                    "prediction_analysis": analysis_results.get(ticker, {}).get("prediction_analysis", {}),
                }
            
            # Call portfolio manager
            recommendation = give_stock_recommendation.invoke({"final_results": final_results})
            print("✅ Original LLM recommendation generated")
            
            return {
                "recommendation": recommendation.content if hasattr(recommendation, 'content') else str(recommendation),
                "input_data": final_results,
                "method": "original_llm"
            }
            
        except Exception as e:
            error_msg = f"Error in original LLM portfolio manager: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def _calculate_actual_performance(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Calculate actual stock performance for comparison"""
        print("\n📈 Calculating actual performance...")
        
        try:
            # Calculate future performance (e.g., 1 month after end_date)
            future_start = datetime.strptime(end_date, '%Y-%m-%d')
            future_end = future_start + timedelta(days=30)
            future_end_str = future_end.strftime('%Y-%m-%d')
            
            performance = {}
            
            for ticker in self.test_tickers:
                try:
                    # Get stock data for the future period
                    future_data = get_historical_stock_data(ticker, end_date, future_end_str)
                    
                    if future_data.startswith("{"):
                        stock_data = json.loads(future_data)
                        
                        # Get first and last prices (FIXED: correct order)
                        timestamps = sorted(stock_data.keys())
                        if len(timestamps) >= 2:
                            start_price = stock_data[timestamps[0]]['close']   # Earliest price (start)
                            end_price = stock_data[timestamps[-1]]['close']   # Latest price (end)
                            
                            price_change = end_price - start_price
                            percent_change = (price_change / start_price) * 100
                            
                            performance[ticker] = {
                                "start_price": start_price,
                                "end_price": end_price,
                                "price_change": price_change,
                                "percent_change": percent_change,
                                "period": f"{end_date} to {future_end_str}"
                            }
                        else:
                            performance[ticker] = {"error": "Insufficient future data"}
                    else:
                        performance[ticker] = {"error": future_data}
                        
                except Exception as e:
                    performance[ticker] = {"error": str(e)}
            
            print("✅ Actual performance calculated")
            return performance
            
        except Exception as e:
            print(f"❌ Error calculating performance: {str(e)}")
            return {"error": str(e)}
    
    def _save_backtest_results(self, results: Dict[str, Any], start_date: str, end_date: str):
        """Save backtest results to files"""
        print("\n💾 Saving backtest results...")
        
        # Create results directory
        results_dir = "testing_framework/backtest_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_{start_date}_to_{end_date}_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)
        
        # Save results
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"✅ Results saved to {filepath}")
    
    def _print_backtest_summary(self, results: Dict[str, Any]):
        """Print a summary of backtest results"""
        print("\n" + "="*60)
        print("📊 BACKTEST SUMMARY")
        print("="*60)
        
        # Basic info
        info = results["backtest_info"]
        print(f"📅 Period: {info['start_date']} to {info['end_date']}")
        print(f"📈 Tickers: {', '.join(info['tickers'])}")
        print(f"🕐 Run Time: {info['run_timestamp']}")
        
        # Portfolio recommendation
        print(f"\n💼 PORTFOLIO RECOMMENDATION:")
        if "recommendation" in results["portfolio_recommendation"]:
            recommendation = results["portfolio_recommendation"]["recommendation"]
            print(f"{recommendation}")
        else:
            print("❌ No recommendation generated")
        
        # Actual performance comparison
        print(f"\n📈 ACTUAL PERFORMANCE (30 days after):")
        for ticker, perf in results["actual_performance"].items():
            if "error" not in perf:
                print(f"  {ticker}: {perf['percent_change']:+.2f}% (${perf['price_change']:+.2f})")
            else:
                print(f"  {ticker}: {perf['error']}")
        
        print("="*60)

def generate_backtest_date_ranges(num_backtests: int = 10, months_back: int = 12):
    """Generate date ranges for multiple backtests"""
    date_ranges = []
    
    for i in range(num_backtests):
        # Each backtest covers 3 months, starting from different points in the past
        days_back = 30 + (i * 30)  # Start from 1 month ago, then 2 months, etc.
        
        end_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back + 90)).strftime('%Y-%m-%d')  # 3 months of data
        
        date_ranges.append((start_date, end_date))
    
    return date_ranges

def run_multiple_backtests(num_backtests: int = 10, method: str = "rule_based"):
    """Run multiple backtests with specified method"""
    method_name = method.replace("_", " ").title()
    print(f"🚀 Starting {num_backtests} {method_name} Backtests")
    print("=" * 80)
    
    # Initialize backtester
    backtester = PortfolioBacktester(["AAPL", "AMZN", "ADBE"])
    
    # Generate date ranges
    date_ranges = generate_backtest_date_ranges(num_backtests)
    
    all_results = []
    successful_backtests = 0
    
    for i, (start_date, end_date) in enumerate(date_ranges, 1):
        print(f"\n{'='*20} BACKTEST {i}/{num_backtests} {'='*20}")
        
        try:
            # Run backtest (don't save individual results to avoid clutter)
            result = backtester.run_backtest(start_date, end_date, save_results=False, method=method)
            all_results.append(result)
            successful_backtests += 1
            
        except Exception as e:
            print(f"❌ Backtest {i} failed: {str(e)}")
            continue
    
    # Print overall summary
    print_overall_summary(all_results, successful_backtests, num_backtests)
    
    # Save consolidated results
    save_consolidated_results(all_results, method)
    
    return all_results

def print_overall_summary(all_results: List[Dict], successful: int, total: int):
    """Print summary of all backtests"""
    print(f"\n{'='*80}")
    print(f"📊 OVERALL BACKTEST SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successful backtests: {successful}/{total}")
    
    if not all_results:
        print("❌ No successful backtests to analyze")
        return
    
    # Analyze recommendations
    buy_count = sell_count = hold_count = 0
    total_recommendations = 0
    
    for result in all_results:
        portfolio_rec = result.get("portfolio_recommendation", {})
        if "detailed_recommendations" in portfolio_rec:
            for ticker, rec in portfolio_rec["detailed_recommendations"].items():
                recommendation = rec.get("recommendation", "HOLD")
                if recommendation == "BUY":
                    buy_count += 1
                elif recommendation == "SELL":
                    sell_count += 1
                else:
                    hold_count += 1
                total_recommendations += 1
    
    if total_recommendations > 0:
        print(f"\n📈 RECOMMENDATION DISTRIBUTION:")
        print(f"  BUY:  {buy_count:2d} ({buy_count/total_recommendations*100:.1f}%)")
        print(f"  SELL: {sell_count:2d} ({sell_count/total_recommendations*100:.1f}%)")
        print(f"  HOLD: {hold_count:2d} ({hold_count/total_recommendations*100:.1f}%)")
    
    # Analyze actual performance where available
    performance_data = []
    for result in all_results:
        actual_perf = result.get("actual_performance", {})
        for ticker, perf in actual_perf.items():
            if isinstance(perf, dict) and "percent_change" in perf:
                performance_data.append(perf["percent_change"])
    
    if performance_data:
        avg_performance = sum(performance_data) / len(performance_data)
        print(f"\n📊 ACTUAL PERFORMANCE ANALYSIS:")
        print(f"  Average return: {avg_performance:+.2f}%")
        print(f"  Best return: {max(performance_data):+.2f}%")
        print(f"  Worst return: {min(performance_data):+.2f}%")
        print(f"  Positive returns: {sum(1 for p in performance_data if p > 0)}/{len(performance_data)}")

def save_consolidated_results(all_results: List[Dict], method: str):
    """Save all backtest results to a single file"""
    results_dir = "testing_framework/backtest_results"
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"consolidated_{method}_backtests_{timestamp}.json"
    filepath = os.path.join(results_dir, filename)
    
    consolidated = {
        "summary": {
            "total_backtests": len(all_results),
            "method": method,
            "tickers": ["AAPL", "AMZN", "ADBE"],
            "timestamp": datetime.now().isoformat()
        },
        "individual_results": all_results
    }
    
    with open(filepath, 'w') as f:
        json.dump(consolidated, f, indent=2, default=str)
    
    print(f"\n💾 Consolidated results saved to: {filepath}")

def run_sample_backtest():
    """Run a single sample backtest"""
    # Initialize backtester
    backtester = PortfolioBacktester(["AAPL", "AMZN", "ADBE"])
    
    # Run backtest for 3 months ago
    end_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    # Run the backtest
    results = backtester.run_backtest(start_date, end_date, method="rule_based")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting Portfolio Management Backtests")
    
    # Run 10 optimized LLM backtests
    results = run_multiple_backtests(num_backtests=3, method="optimized_llm")  # Start with 3 for testing
    
    print("✅ All backtests completed!")
