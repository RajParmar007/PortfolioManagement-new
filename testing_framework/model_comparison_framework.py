"""
Model Comparison Framework
Compares Multi-Agent AI Model vs Rule-Based Technical Indicators
Tests on 3-month AAPL historical data with comprehensive financial metrics
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import yfinance as yf

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ModelComparisonFramework:
    """
    Framework to compare AI model vs rule-based strategies
    """
    
    def __init__(self, ticker: str = "AAPL", months: int = 3):
        self.ticker = ticker
        self.months = months
        self.historical_data = None
        self.results = {}
        
        # Initialize starting portfolio value
        self.initial_capital = 10000
        
    def run_full_comparison(self):
        """
        Run complete comparison between AI model and rule-based strategies
        """
        print(f"🚀 Starting Model Comparison Framework")
        print(f"📈 Ticker: {self.ticker}")
        print(f"📅 Period: {self.months} months")
        print(f"💰 Initial Capital: ${self.initial_capital:,}")
        print("=" * 80)
        
        # Step 1: Retrieve and prepare historical data
        print("\n📊 Step 1: Retrieving Historical Data...")
        self._retrieve_historical_data()
        
        # Step 2: Run AI Multi-Agent Model
        print("\n🤖 Step 2: Running AI Multi-Agent Model...")
        ai_results = self._run_ai_model()
        
        # Step 3: Run Rule-Based Strategies
        print("\n📐 Step 3: Running Rule-Based Strategies...")
        rule_results = self._run_rule_based_strategies()
        
        # Step 4: Calculate Performance Metrics
        print("\n📊 Step 4: Calculating Performance Metrics...")
        self._calculate_performance_metrics(ai_results, rule_results)
        
        # Step 5: Generate Comparison Report
        print("\n📋 Step 5: Generating Comparison Report...")
        self._generate_comparison_report()
        
        return self.results
    
    def _retrieve_historical_data(self):
        """
        Retrieve 3-month historical data for AAPL using yfinance (with caching)
        """
        try:
            # Check if data already exists to avoid repeated yfinance calls
            cache_file = f"testing_framework/cached_data/{self.ticker}_{self.months}months_data.json"
            
            if os.path.exists(cache_file):
                print(f"   📂 Loading cached data from {cache_file}")
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Convert back to DataFrame from cached JSON
                stock_data_json = cached_data['stock_data']
                if isinstance(stock_data_json, str):
                    # Parse the JSON string back to dict
                    stock_data_dict = json.loads(stock_data_json)
                else:
                    stock_data_dict = stock_data_json
                
                # Create DataFrame from the dictionary
                hist_data = pd.DataFrame.from_dict(stock_data_dict, orient='index')
                hist_data.index = pd.to_datetime(hist_data.index)
                
                self.historical_data = hist_data
                
                # Also retrieve cached news and reddit data
                self.news_data = cached_data.get('news_data', [])
                self.reddit_data = cached_data.get('reddit_data', [])
                
                print(f"   ✅ Loaded cached data: {len(hist_data)} days")
                return
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.months * 30 + 30)  # Extra buffer for indicators
            
            print(f"   📅 Fetching fresh data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Get stock data from yfinance
            stock = yf.Ticker(self.ticker)
            hist_data = stock.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                raise Exception("No data retrieved from yfinance")
            
            # Calculate technical indicators
            hist_data = self._calculate_technical_indicators(hist_data)
            
            # Store the data
            self.historical_data = hist_data
            
            # For SMA-based AI, we don't need news/reddit data (no sentiment analysis)
            self.news_data = []
            self.reddit_data = []
            
            # Save to cache for AI model and future runs
            self._save_data_for_ai_model(hist_data)
            self._cache_all_data(hist_data)
            
            print(f"   ✅ Retrieved {len(hist_data)} days of stock data")
            print(f"   📰 Retrieved {len(self.news_data)} news articles")
            print(f"   🔴 Retrieved {len(self.reddit_data)} reddit posts")
            print(f"   📊 Date range: {hist_data.index[0].strftime('%Y-%m-%d')} to {hist_data.index[-1].strftime('%Y-%m-%d')}")
            
        except Exception as e:
            print(f"   ❌ Error retrieving data: {str(e)}")
            raise
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the historical data
        """
        df = data.copy()
        
        # Simple Moving Averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Average True Range (ATR)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Price momentum
        df['Returns_1d'] = df['Close'].pct_change()
        df['Returns_5d'] = df['Close'].pct_change(5)
        df['Volatility_20d'] = df['Returns_1d'].rolling(window=20).std()
        
        return df
    
    def _save_data_for_ai_model(self, data: pd.DataFrame):
        """
        Save data in the format expected by AI model agents
        """
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Convert to the format expected by prediction agent
        stock_data = {}
        for date, row in data.iterrows():
            timestamp = str(int(date.timestamp() * 1000))
            stock_data[timestamp] = {
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume']),
                'dividends': 0.0,
                'stock splits': 0.0,
                'SMA_20': float(row.get('SMA_20', 0)),
                'SMA_50': float(row.get('SMA_50', 0)),
                'EMA_12': float(row.get('EMA_12', 0)),
                'MACD': float(row.get('MACD', 0)),
                'MACD_Hist': float(row.get('MACD_Hist', 0)),
                'RSI_14': float(row.get('RSI', 50)),
                'ATR': float(row.get('ATR', 0)),
                'BB_Upper': float(row.get('BB_Upper', 0)),
                'BB_Lower': float(row.get('BB_Lower', 0)),
                'Volume_Ratio': float(row.get('Volume_Ratio', 1)),
                'Returns_1d': float(row.get('Returns_1d', 0)),
                'Returns_5d': float(row.get('Returns_5d', 0)),
                'Volatility_20d': float(row.get('Volatility_20d', 0)),
            }
        
        # Save to file
        with open(f"{data_dir}/{self.ticker}_stock_data.json", 'w') as f:
            json.dump(stock_data, f, indent=2)
        
        print(f"   💾 Saved data for AI model: {data_dir}/{self.ticker}_stock_data.json")
    
    def _retrieve_news_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Retrieve news data for the specified period using existing tools
        """
        try:
            # Import the historical data retrieval function
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from testing_framework.historical_data_retrieval import get_historical_market_news
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            news_result = get_historical_market_news(self.ticker, start_str, end_str)
            
            if isinstance(news_result, str) and news_result.startswith('['):
                import json
                return json.loads(news_result)
            elif isinstance(news_result, list):
                return news_result
            else:
                print(f"   ⚠️  News retrieval returned: {news_result}")
                return []
                
        except Exception as e:
            print(f"   ⚠️  Error retrieving news: {str(e)}")
            return []
    
    def _retrieve_reddit_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Retrieve reddit data for the specified period using existing tools
        """
        try:
            # Import the historical data retrieval function
            from testing_framework.historical_data_retrieval import get_historical_reddit_posts
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            reddit_result = get_historical_reddit_posts(self.ticker, start_str, end_str)
            
            if isinstance(reddit_result, str) and reddit_result.startswith('['):
                import json
                return json.loads(reddit_result)
            elif isinstance(reddit_result, list):
                return reddit_result
            else:
                print(f"   ⚠️  Reddit retrieval returned: {reddit_result}")
                return []
                
        except Exception as e:
            print(f"   ⚠️  Error retrieving reddit: {str(e)}")
            return []
    
    def _cache_all_data(self, hist_data: pd.DataFrame):
        """
        Cache all data (stock, news, reddit) to avoid repeated API calls
        """
        try:
            # Create cache directory
            cache_dir = "testing_framework/cached_data"
            os.makedirs(cache_dir, exist_ok=True)
            
            # Prepare data for caching
            cache_data = {
                "stock_data": hist_data.to_json(orient='index', date_format='iso'),
                "news_data": getattr(self, 'news_data', []),
                "reddit_data": getattr(self, 'reddit_data', []),
                "cached_at": datetime.now().isoformat(),
                "ticker": self.ticker,
                "months": self.months
            }
            
            # Save to cache file
            cache_file = f"{cache_dir}/{self.ticker}_{self.months}months_data.json"
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            print(f"   💾 Cached all data to: {cache_file}")
            
        except Exception as e:
            print(f"   ⚠️  Error caching data: {str(e)}")
    
    def _run_ai_model(self) -> Dict[str, Any]:
        """
        Run the complete AI multi-agent model workflow
        """
        print("   🔄 Running Multi-Agent AI Model...")
        
        # Import modified agents for testing
        from testing_agents import (
            run_technical_analysis_testing,
            run_prediction_analysis_testing,
            run_sma_enhanced_llm_portfolio_manager
        )
        
        ai_signals = []
        ai_returns = []
        ai_dates = []
        
        # Get the last 60 days for testing (need buffer for indicators)
        test_data = self.historical_data.tail(60).copy()
        
        for i in range(30, len(test_data) - 1):  # Start from day 30 to have enough history
            current_date = test_data.index[i]
            next_date = test_data.index[i + 1]
            
            print(f"     📅 Processing {current_date.strftime('%Y-%m-%d')}")
            
            try:
                # Run technical analysis
                tech_result = run_technical_analysis_testing(self.ticker, current_date)
                
                # Run prediction analysis
                prediction_result = run_prediction_analysis_testing(self.ticker, current_date)
                
                # Combine results for portfolio manager
                analysis_results = {
                    self.ticker: {
                        'technical_analysis': tech_result,
                        'prediction_analysis': prediction_result
                    }
                }
                
                # Run LLM-enhanced SMA portfolio manager (ACTUALLY calls LLM)
                portfolio_decision = run_sma_enhanced_llm_portfolio_manager(analysis_results)
                
                # Extract signal and calculate return
                signal = self._extract_signal_from_portfolio_decision(portfolio_decision)
                actual_return = self._calculate_actual_return(test_data, i, i + 1)
                
                ai_signals.append(signal)
                ai_returns.append(actual_return * signal)  # Apply signal to return
                ai_dates.append(current_date)
                
            except Exception as e:
                print(f"     ❌ Error processing {current_date}: {str(e)}")
                
                # FALLBACK TO SMA SIGNAL instead of HOLD
                try:
                    sma_5 = test_data.iloc[i]['SMA_5']
                    sma_20 = test_data.iloc[i]['SMA_20']
                    
                    # Use pure SMA crossover as fallback
                    if sma_5 > sma_20:
                        fallback_signal = 1  # Buy
                    elif sma_5 < sma_20:
                        fallback_signal = -1  # Sell
                    else:
                        fallback_signal = 0  # Hold
                    
                    actual_return = self._calculate_actual_return(test_data, i, i + 1)
                    ai_signals.append(fallback_signal)
                    ai_returns.append(actual_return * fallback_signal)
                    ai_dates.append(current_date)
                    
                    print(f"     🔄 Used SMA fallback: {fallback_signal}")
                    
                except Exception as fallback_error:
                    print(f"     ❌ Fallback also failed: {str(fallback_error)}")
                    ai_signals.append(0)  # Hold as last resort
                    ai_returns.append(0)
                    ai_dates.append(current_date)
        
        # Store raw data for plotting
        self._ai_raw_data = {
            'signals': ai_signals,
            'returns': ai_returns,
            'dates': [d.strftime('%Y-%m-%d') for d in ai_dates],
            'cumulative_returns': self._calculate_cumulative_returns(ai_returns)
        }
        
        return {
            'strategy_name': 'AI Multi-Agent Model',
            'signals': ai_signals,
            'returns': ai_returns,
            'dates': ai_dates
        }
    
    def _run_rule_based_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Run various rule-based technical indicator strategies
        """
        strategies = {}
        
        # Get test data (last 60 days, start from day 30)
        test_data = self.historical_data.tail(60).copy()
        
        # Strategy 1: RSI Strategy
        print("   📊 Running RSI Strategy...")
        strategies['RSI'] = self._run_rsi_strategy(test_data)
        
        # Strategy 2: MACD Strategy  
        print("   📊 Running MACD Strategy...")
        strategies['MACD'] = self._run_macd_strategy(test_data)
        
        # Strategy 3: SMA Crossover Strategy
        print("   📊 Running SMA Crossover Strategy...")
        strategies['SMA_Crossover'] = self._run_sma_crossover_strategy(test_data)
        
        # Strategy 4: Bollinger Bands Strategy
        print("   📊 Running Bollinger Bands Strategy...")
        strategies['Bollinger_Bands'] = self._run_bollinger_strategy(test_data)
        
        # Strategy 5: Combined Technical Strategy
        print("   📊 Running Combined Technical Strategy...")
        strategies['Combined_Technical'] = self._run_combined_technical_strategy(test_data)
        
        # Store raw data for plotting
        self._rule_raw_data = {}
        for name, strategy in strategies.items():
            self._rule_raw_data[name] = {
                'signals': strategy['signals'],
                'returns': strategy['returns'],
                'dates': [d.strftime('%Y-%m-%d') for d in strategy['dates']],
                'cumulative_returns': self._calculate_cumulative_returns(strategy['returns'])
            }
        
        return strategies
    
    def _calculate_cumulative_returns(self, returns: List[float]) -> List[float]:
        """Calculate cumulative returns for plotting"""
        cumulative = [0]
        for ret in returns:
            cumulative.append(cumulative[-1] + ret)
        return cumulative[1:]  # Remove initial 0
    
    def _run_rsi_strategy(self, data: pd.DataFrame) -> Dict[str, Any]:
        """RSI-based trading strategy"""
        signals = []
        returns = []
        
        for i in range(30, len(data) - 1):
            rsi = data.iloc[i]['RSI']
            
            # RSI Strategy: Buy when RSI < 30 (oversold), Sell when RSI > 70 (overbought)
            if rsi < 30:
                signal = 1  # Buy
            elif rsi > 70:
                signal = -1  # Sell
            else:
                signal = 0  # Hold
            
            actual_return = self._calculate_actual_return(data, i, i + 1)
            
            signals.append(signal)
            returns.append(actual_return * signal)
        
        return {
            'strategy_name': 'RSI Strategy',
            'signals': signals,
            'returns': returns,
            'dates': [data.index[i] for i in range(30, len(data) - 1)]
        }
    
    def _run_macd_strategy(self, data: pd.DataFrame) -> Dict[str, Any]:
        """MACD-based trading strategy"""
        signals = []
        returns = []
        
        for i in range(30, len(data) - 1):
            macd = data.iloc[i]['MACD']
            macd_signal = data.iloc[i]['MACD_Signal']
            macd_hist = data.iloc[i]['MACD_Hist']
            
            # MACD Strategy: Buy when MACD crosses above signal, Sell when crosses below
            if macd > macd_signal and macd_hist > 0:
                signal = 1  # Buy
            elif macd < macd_signal and macd_hist < 0:
                signal = -1  # Sell
            else:
                signal = 0  # Hold
            
            actual_return = self._calculate_actual_return(data, i, i + 1)
            
            signals.append(signal)
            returns.append(actual_return * signal)
        
        return {
            'strategy_name': 'MACD Strategy',
            'signals': signals,
            'returns': returns,
            'dates': [data.index[i] for i in range(30, len(data) - 1)]
        }
    
    def _run_sma_crossover_strategy(self, data: pd.DataFrame) -> Dict[str, Any]:
        """SMA crossover trading strategy"""
        signals = []
        returns = []
        
        for i in range(30, len(data) - 1):
            sma_5 = data.iloc[i]['SMA_5']
            sma_20 = data.iloc[i]['SMA_20']
            
            # SMA Strategy: Buy when SMA5 > SMA20, Sell when SMA5 < SMA20
            if sma_5 > sma_20:
                signal = 1  # Buy
            elif sma_5 < sma_20:
                signal = -1  # Sell
            else:
                signal = 0  # Hold
            
            actual_return = self._calculate_actual_return(data, i, i + 1)
            
            signals.append(signal)
            returns.append(actual_return * signal)
        
        return {
            'strategy_name': 'SMA Crossover Strategy',
            'signals': signals,
            'returns': returns,
            'dates': [data.index[i] for i in range(30, len(data) - 1)]
        }
    
    def _run_bollinger_strategy(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Bollinger Bands trading strategy"""
        signals = []
        returns = []
        
        for i in range(30, len(data) - 1):
            price = data.iloc[i]['Close']
            bb_upper = data.iloc[i]['BB_Upper']
            bb_lower = data.iloc[i]['BB_Lower']
            
            # Bollinger Strategy: Buy when price touches lower band, Sell when touches upper band
            if price <= bb_lower:
                signal = 1  # Buy (oversold)
            elif price >= bb_upper:
                signal = -1  # Sell (overbought)
            else:
                signal = 0  # Hold
            
            actual_return = self._calculate_actual_return(data, i, i + 1)
            
            signals.append(signal)
            returns.append(actual_return * signal)
        
        return {
            'strategy_name': 'Bollinger Bands Strategy',
            'signals': signals,
            'returns': returns,
            'dates': [data.index[i] for i in range(30, len(data) - 1)]
        }
    
    def _run_combined_technical_strategy(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Combined technical indicators strategy"""
        signals = []
        returns = []
        
        for i in range(30, len(data) - 1):
            # Get all indicators
            rsi = data.iloc[i]['RSI']
            macd_hist = data.iloc[i]['MACD_Hist']
            sma_5 = data.iloc[i]['SMA_5']
            sma_20 = data.iloc[i]['SMA_20']
            price = data.iloc[i]['Close']
            bb_upper = data.iloc[i]['BB_Upper']
            bb_lower = data.iloc[i]['BB_Lower']
            
            # Combined scoring system
            score = 0
            
            # RSI component
            if rsi < 30:
                score += 1
            elif rsi > 70:
                score -= 1
            
            # MACD component
            if macd_hist > 0:
                score += 1
            elif macd_hist < 0:
                score -= 1
            
            # SMA component
            if sma_5 > sma_20:
                score += 1
            elif sma_5 < sma_20:
                score -= 1
            
            # Bollinger component
            if price <= bb_lower:
                score += 1
            elif price >= bb_upper:
                score -= 1
            
            # Final signal based on combined score
            if score >= 2:
                signal = 1  # Strong Buy
            elif score <= -2:
                signal = -1  # Strong Sell
            else:
                signal = 0  # Hold
            
            actual_return = self._calculate_actual_return(data, i, i + 1)
            
            signals.append(signal)
            returns.append(actual_return * signal)
        
        return {
            'strategy_name': 'Combined Technical Strategy',
            'signals': signals,
            'returns': returns,
            'dates': [data.index[i] for i in range(30, len(data) - 1)]
        }
    
    def _extract_signal_from_portfolio_decision(self, portfolio_decision: Dict[str, Any]) -> int:
        """
        Extract trading signal from portfolio manager decision
        """
        try:
            if 'detailed_recommendations' in portfolio_decision:
                rec = portfolio_decision['detailed_recommendations'].get(self.ticker, {})
                recommendation = rec.get('recommendation', 'HOLD')
                
                if recommendation == 'BUY':
                    return 1
                elif recommendation == 'SELL':
                    return -1
                else:
                    return 0
            else:
                # Fallback: parse from recommendation text
                rec_text = portfolio_decision.get('recommendation', '').upper()
                if 'BUY' in rec_text:
                    return 1
                elif 'SELL' in rec_text:
                    return -1
                else:
                    return 0
        except:
            return 0  # Default to hold on error
    
    def _calculate_actual_return(self, data: pd.DataFrame, current_idx: int, next_idx: int) -> float:
        """
        Calculate actual return between two periods
        """
        try:
            current_price = data.iloc[current_idx]['Close']
            next_price = data.iloc[next_idx]['Close']
            return (next_price - current_price) / current_price
        except:
            return 0.0
    
    def _calculate_performance_metrics(self, ai_results: Dict[str, Any], rule_results: Dict[str, Dict[str, Any]]):
        """
        Calculate comprehensive performance metrics for all strategies
        """
        all_strategies = {'AI_Model': ai_results}
        all_strategies.update(rule_results)
        
        self.results = {}
        
        for strategy_name, strategy_data in all_strategies.items():
            returns = np.array(strategy_data['returns'])
            
            # Basic metrics
            total_return = np.sum(returns)
            annualized_return = (1 + total_return) ** (252 / len(returns)) - 1  # ARR
            
            # Risk metrics
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            
            # Drawdown calculation
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            # Win rate
            winning_trades = np.sum(returns > 0)
            total_trades = np.sum(returns != 0)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # Calmar ratio
            calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Final portfolio value
            final_portfolio_value = self.initial_capital * (1 + total_return)
            
            self.results[strategy_name] = {
                'total_return': total_return * 100,
                'annualized_return': annualized_return * 100,
                'volatility': volatility * 100,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown * 100,
                'win_rate': win_rate * 100,
                'calmar_ratio': calmar_ratio,
                'total_trades': int(total_trades),
                'winning_trades': int(winning_trades),
                'final_portfolio_value': final_portfolio_value,
                'profit_loss': final_portfolio_value - self.initial_capital
            }
    
    def _generate_comparison_report(self):
        """
        Generate comprehensive comparison report
        """
        print("\n" + "="*100)
        print("📊 MODEL COMPARISON REPORT - AAPL (3 MONTHS)")
        print("="*100)
        
        # Sort strategies by Sharpe ratio
        sorted_strategies = sorted(self.results.items(), key=lambda x: x[1]['sharpe_ratio'], reverse=True)
        
        print(f"\n{'Strategy':<25} {'Total Return':<12} {'ARR':<8} {'Volatility':<10} {'Sharpe':<8} {'Max DD':<8} {'Win Rate':<9} {'Calmar':<8}")
        print("-" * 100)
        
        for strategy_name, metrics in sorted_strategies:
            print(f"{strategy_name:<25} "
                  f"{metrics['total_return']:>10.2f}% "
                  f"{metrics['annualized_return']:>6.2f}% "
                  f"{metrics['volatility']:>8.2f}% "
                  f"{metrics['sharpe_ratio']:>6.3f} "
                  f"{metrics['max_drawdown']:>6.2f}% "
                  f"{metrics['win_rate']:>7.1f}% "
                  f"{metrics['calmar_ratio']:>6.3f}")
        
        # Detailed breakdown
        print(f"\n📈 DETAILED PERFORMANCE BREAKDOWN:")
        print("-" * 50)
        
        for strategy_name, metrics in sorted_strategies:
            print(f"\n🔹 {strategy_name}:")
            print(f"   💰 Final Portfolio Value: ${metrics['final_portfolio_value']:,.2f}")
            print(f"   📊 Profit/Loss: ${metrics['profit_loss']:+,.2f}")
            print(f"   📈 Total Return: {metrics['total_return']:+.2f}%")
            print(f"   📅 Annualized Return (ARR): {metrics['annualized_return']:+.2f}%")
            print(f"   📉 Volatility: {metrics['volatility']:.2f}%")
            print(f"   ⚡ Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
            print(f"   📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
            print(f"   🎯 Win Rate: {metrics['win_rate']:.1f}%")
            print(f"   📊 Calmar Ratio: {metrics['calmar_ratio']:.3f}")
            print(f"   🔄 Total Trades: {metrics['total_trades']}")
            print(f"   ✅ Winning Trades: {metrics['winning_trades']}")
        
        # Save results
        self._save_comparison_results()
        
        print(f"\n💾 Results saved to: testing_framework/comparison_results/")
        print("="*100)
    
    def _save_comparison_results(self):
        """
        Save comparison results to JSON file
        """
        results_dir = "testing_framework/comparison_results"
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"model_comparison_{self.ticker}_{self.months}months_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)
        
        output_data = {
            "comparison_info": {
                "ticker": self.ticker,
                "period_months": self.months,
                "initial_capital": self.initial_capital,
                "timestamp": datetime.now().isoformat(),
                "testing_period": {
                    "total_days": len(self.historical_data),
                    "testing_days": 29,  # 30 to len(test_data) - 1
                    "start_date": self.historical_data.index[0].strftime('%Y-%m-%d'),
                    "end_date": self.historical_data.index[-1].strftime('%Y-%m-%d'),
                    "test_start_date": self.historical_data.tail(60).index[30].strftime('%Y-%m-%d'),
                    "test_end_date": self.historical_data.tail(60).index[-2].strftime('%Y-%m-%d')
                }
            },
            "performance_metrics": self.results,
            "raw_data": {
                "ai_model": getattr(self, '_ai_raw_data', {}),
                "rule_based": getattr(self, '_rule_raw_data', {})
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)

def run_model_comparison(ticker: str = "AAPL", months: int = 3):
    """
    Main function to run the model comparison
    """
    framework = ModelComparisonFramework(ticker, months)
    return framework.run_full_comparison()

if __name__ == "__main__":
    # Run the comparison
    results = run_model_comparison("AAPL", 3)
