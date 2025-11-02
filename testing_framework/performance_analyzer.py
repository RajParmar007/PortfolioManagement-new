"""
Performance Analysis Module for Portfolio Management Backtesting
Calculates accuracy, Sharpe ratio, returns, and other financial metrics
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import os

class PerformanceAnalyzer:
    """
    Analyzes the performance of portfolio management recommendations
    """
    
    def __init__(self, results_file_path: str):
        """
        Initialize with backtest results file
        
        Args:
            results_file_path: Path to the consolidated backtest results JSON file
        """
        self.results_file_path = results_file_path
        self.results = self._load_results()
        self.performance_metrics = {}
        
    def _load_results(self) -> Dict[str, Any]:
        """Load backtest results from JSON file"""
        try:
            with open(self.results_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading results file: {str(e)}")
    
    def calculate_all_metrics(self) -> Dict[str, Any]:
        """Calculate all performance metrics"""
        print("📊 Calculating comprehensive performance metrics...")
        
        # Extract recommendation and performance data
        recommendation_data = self._extract_recommendation_data()
        
        # Calculate various metrics
        metrics = {
            "basic_metrics": self._calculate_basic_metrics(recommendation_data),
            "accuracy_metrics": self._calculate_accuracy_metrics(recommendation_data),
            "return_metrics": self._calculate_return_metrics(recommendation_data),
            "risk_metrics": self._calculate_risk_metrics(recommendation_data),
            "portfolio_metrics": self._calculate_portfolio_metrics(recommendation_data),
            "detailed_analysis": self._detailed_ticker_analysis(recommendation_data)
        }
        
        self.performance_metrics = metrics
        return metrics
    
    def _extract_recommendation_data(self) -> List[Dict[str, Any]]:
        """Extract recommendation and actual performance data from results"""
        data = []
        
        for backtest in self.results.get('individual_results', []):
            backtest_info = backtest.get('backtest_info', {})
            portfolio_rec = backtest.get('portfolio_recommendation', {})
            actual_perf = backtest.get('actual_performance', {})
            
            # Extract detailed recommendations
            detailed_recs = portfolio_rec.get('detailed_recommendations', {})
            
            for ticker in ['AAPL', 'AMZN', 'ADBE']:
                if ticker in detailed_recs and ticker in actual_perf:
                    rec_data = detailed_recs[ticker]
                    perf_data = actual_perf[ticker]
                    
                    if isinstance(perf_data, dict) and 'percent_change' in perf_data:
                        data.append({
                            'date': backtest_info.get('start_date'),
                            'ticker': ticker,
                            'recommendation': rec_data.get('recommendation', 'HOLD'),
                            'score': rec_data.get('score', 0),
                            'reasoning': rec_data.get('reasoning', []),
                            'actual_return': perf_data.get('percent_change', 0),
                            'actual_price_change': perf_data.get('price_change', 0),
                            'start_price': perf_data.get('start_price', 0),
                            'end_price': perf_data.get('end_price', 0)
                        })
        
        return data
    
    def _calculate_basic_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic performance metrics"""
        if not data:
            return {"error": "No data available"}
        
        total_recommendations = len(data)
        buy_count = sum(1 for d in data if d['recommendation'] == 'BUY')
        sell_count = sum(1 for d in data if d['recommendation'] == 'SELL')
        hold_count = sum(1 for d in data if d['recommendation'] == 'HOLD')
        
        avg_return = np.mean([d['actual_return'] for d in data])
        total_return = sum([d['actual_return'] for d in data])
        
        return {
            "total_recommendations": total_recommendations,
            "buy_recommendations": buy_count,
            "sell_recommendations": sell_count,
            "hold_recommendations": hold_count,
            "buy_percentage": (buy_count / total_recommendations) * 100,
            "sell_percentage": (sell_count / total_recommendations) * 100,
            "hold_percentage": (hold_count / total_recommendations) * 100,
            "average_return": avg_return,
            "total_return": total_return,
            "positive_returns": sum(1 for d in data if d['actual_return'] > 0),
            "negative_returns": sum(1 for d in data if d['actual_return'] < 0),
            "win_rate": (sum(1 for d in data if d['actual_return'] > 0) / total_recommendations) * 100
        }
    
    def _calculate_accuracy_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate recommendation accuracy metrics"""
        if not data:
            return {"error": "No data available"}
        
        correct_predictions = 0
        total_predictions = 0
        
        buy_correct = 0
        buy_total = 0
        sell_correct = 0
        sell_total = 0
        hold_correct = 0
        hold_total = 0
        
        for d in data:
            recommendation = d['recommendation']
            actual_return = d['actual_return']
            
            total_predictions += 1
            
            # Define accuracy thresholds
            significant_positive = actual_return > 2  # >2% gain
            significant_negative = actual_return < -2  # >2% loss
            neutral = -2 <= actual_return <= 2  # Between -2% and +2%
            
            if recommendation == 'BUY':
                buy_total += 1
                if significant_positive:
                    correct_predictions += 1
                    buy_correct += 1
            elif recommendation == 'SELL':
                sell_total += 1
                if significant_negative:
                    correct_predictions += 1
                    sell_correct += 1
            elif recommendation == 'HOLD':
                hold_total += 1
                if neutral:
                    correct_predictions += 1
                    hold_correct += 1
        
        overall_accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        
        return {
            "overall_accuracy": overall_accuracy,
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions,
            "buy_accuracy": (buy_correct / buy_total) * 100 if buy_total > 0 else 0,
            "sell_accuracy": (sell_correct / sell_total) * 100 if sell_total > 0 else 0,
            "hold_accuracy": (hold_correct / hold_total) * 100 if hold_total > 0 else 0,
            "buy_correct": buy_correct,
            "buy_total": buy_total,
            "sell_correct": sell_correct,
            "sell_total": sell_total,
            "hold_correct": hold_correct,
            "hold_total": hold_total
        }
    
    def _calculate_return_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate return-based metrics"""
        if not data:
            return {"error": "No data available"}
        
        returns = [d['actual_return'] for d in data]
        
        # Strategy returns (following recommendations)
        strategy_returns = []
        for d in data:
            if d['recommendation'] == 'BUY':
                strategy_returns.append(d['actual_return'])
            elif d['recommendation'] == 'SELL':
                strategy_returns.append(-d['actual_return'])  # Profit from short selling
            else:  # HOLD
                strategy_returns.append(0)  # No position, no return
        
        # Buy-and-hold benchmark (always buy)
        benchmark_returns = returns
        
        return {
            "average_return": np.mean(returns),
            "median_return": np.median(returns),
            "std_return": np.std(returns),
            "min_return": np.min(returns),
            "max_return": np.max(returns),
            "strategy_average_return": np.mean(strategy_returns),
            "strategy_total_return": np.sum(strategy_returns),
            "benchmark_average_return": np.mean(benchmark_returns),
            "benchmark_total_return": np.sum(benchmark_returns),
            "excess_return": np.mean(strategy_returns) - np.mean(benchmark_returns),
            "cumulative_strategy_return": np.sum(strategy_returns),
            "cumulative_benchmark_return": np.sum(benchmark_returns),
            "outperformance": np.sum(strategy_returns) - np.sum(benchmark_returns)
        }
    
    def _calculate_risk_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate risk metrics including Sharpe ratio"""
        if not data:
            return {"error": "No data available"}
        
        returns = [d['actual_return'] / 100 for d in data]  # Convert to decimal
        
        # Strategy returns
        strategy_returns = []
        for d in data:
            ret = d['actual_return'] / 100  # Convert to decimal
            if d['recommendation'] == 'BUY':
                strategy_returns.append(ret)
            elif d['recommendation'] == 'SELL':
                strategy_returns.append(-ret)
            else:  # HOLD
                strategy_returns.append(0)
        
        # Risk-free rate (assume 2% annually, convert to monthly)
        risk_free_rate = 0.02 / 12  # Monthly risk-free rate
        
        # Calculate Sharpe ratio
        strategy_mean = np.mean(strategy_returns)
        strategy_std = np.std(strategy_returns)
        sharpe_ratio = (strategy_mean - risk_free_rate) / strategy_std if strategy_std != 0 else 0
        
        # Calculate maximum drawdown
        cumulative_returns = np.cumsum(strategy_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = cumulative_returns - running_max
        max_drawdown = np.min(drawdown)
        
        # Volatility (annualized)
        volatility = np.std(strategy_returns) * np.sqrt(12)  # Annualized monthly volatility
        
        return {
            "sharpe_ratio": sharpe_ratio,
            "volatility": volatility,
            "max_drawdown": max_drawdown,
            "strategy_std": strategy_std,
            "downside_deviation": np.std([r for r in strategy_returns if r < 0]),
            "upside_deviation": np.std([r for r in strategy_returns if r > 0]),
            "var_95": np.percentile(strategy_returns, 5),  # Value at Risk (95%)
            "cvar_95": np.mean([r for r in strategy_returns if r <= np.percentile(strategy_returns, 5)])  # Conditional VaR
        }
    
    def _calculate_portfolio_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio-level metrics"""
        if not data:
            return {"error": "No data available"}
        
        # Group by date to analyze portfolio performance
        portfolio_performance = {}
        
        for d in data:
            date = d['date']
            if date not in portfolio_performance:
                portfolio_performance[date] = {
                    'tickers': [],
                    'recommendations': [],
                    'returns': [],
                    'weights': []
                }
            
            portfolio_performance[date]['tickers'].append(d['ticker'])
            portfolio_performance[date]['recommendations'].append(d['recommendation'])
            portfolio_performance[date]['returns'].append(d['actual_return'])
            portfolio_performance[date]['weights'].append(1/3)  # Equal weight
        
        # Calculate portfolio returns for each date
        portfolio_returns = []
        for date, perf in portfolio_performance.items():
            # Equal-weighted portfolio return
            portfolio_return = np.average(perf['returns'], weights=perf['weights'])
            portfolio_returns.append(portfolio_return)
        
        return {
            "portfolio_average_return": np.mean(portfolio_returns),
            "portfolio_total_return": np.sum(portfolio_returns),
            "portfolio_volatility": np.std(portfolio_returns),
            "portfolio_sharpe": (np.mean(portfolio_returns) - 0.02/12) / np.std(portfolio_returns) if np.std(portfolio_returns) != 0 else 0,
            "best_portfolio_return": np.max(portfolio_returns),
            "worst_portfolio_return": np.min(portfolio_returns),
            "portfolio_win_rate": (sum(1 for r in portfolio_returns if r > 0) / len(portfolio_returns)) * 100
        }
    
    def _detailed_ticker_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detailed analysis by ticker"""
        ticker_analysis = {}
        
        for ticker in ['AAPL', 'AMZN', 'ADBE']:
            ticker_data = [d for d in data if d['ticker'] == ticker]
            
            if ticker_data:
                returns = [d['actual_return'] for d in ticker_data]
                recommendations = [d['recommendation'] for d in ticker_data]
                
                ticker_analysis[ticker] = {
                    "total_recommendations": len(ticker_data),
                    "average_return": np.mean(returns),
                    "total_return": np.sum(returns),
                    "volatility": np.std(returns),
                    "min_return": np.min(returns),
                    "max_return": np.max(returns),
                    "win_rate": (sum(1 for r in returns if r > 0) / len(returns)) * 100,
                    "buy_count": recommendations.count('BUY'),
                    "sell_count": recommendations.count('SELL'),
                    "hold_count": recommendations.count('HOLD')
                }
        
        return ticker_analysis
    
    def print_performance_report(self):
        """Print a comprehensive performance report"""
        if not self.performance_metrics:
            self.calculate_all_metrics()
        
        metrics = self.performance_metrics
        
        print("\n" + "="*80)
        print("📊 PORTFOLIO MANAGEMENT SYSTEM PERFORMANCE REPORT")
        print("="*80)
        
        # Basic Metrics
        basic = metrics['basic_metrics']
        print(f"\n📈 BASIC METRICS:")
        print(f"  Total Recommendations: {basic['total_recommendations']}")
        print(f"  BUY: {basic['buy_recommendations']} ({basic['buy_percentage']:.1f}%)")
        print(f"  SELL: {basic['sell_recommendations']} ({basic['sell_percentage']:.1f}%)")
        print(f"  HOLD: {basic['hold_recommendations']} ({basic['hold_percentage']:.1f}%)")
        print(f"  Win Rate: {basic['win_rate']:.1f}%")
        print(f"  Average Return: {basic['average_return']:+.2f}%")
        
        # Accuracy Metrics
        accuracy = metrics['accuracy_metrics']
        print(f"\n🎯 ACCURACY METRICS:")
        print(f"  Overall Accuracy: {accuracy['overall_accuracy']:.1f}%")
        print(f"  BUY Accuracy: {accuracy['buy_accuracy']:.1f}% ({accuracy['buy_correct']}/{accuracy['buy_total']})")
        print(f"  SELL Accuracy: {accuracy['sell_accuracy']:.1f}% ({accuracy['sell_correct']}/{accuracy['sell_total']})")
        print(f"  HOLD Accuracy: {accuracy['hold_accuracy']:.1f}% ({accuracy['hold_correct']}/{accuracy['hold_total']})")
        
        # Return Metrics
        returns = metrics['return_metrics']
        print(f"\n💰 RETURN METRICS:")
        print(f"  Strategy Total Return: {returns['strategy_total_return']:+.2f}%")
        print(f"  Benchmark Total Return: {returns['benchmark_total_return']:+.2f}%")
        print(f"  Outperformance: {returns['outperformance']:+.2f}%")
        print(f"  Average Strategy Return: {returns['strategy_average_return']:+.2f}%")
        
        # Risk Metrics
        risk = metrics['risk_metrics']
        print(f"\n⚠️  RISK METRICS:")
        print(f"  Sharpe Ratio: {risk['sharpe_ratio']:.3f}")
        print(f"  Volatility (Annualized): {risk['volatility']*100:.2f}%")
        print(f"  Maximum Drawdown: {risk['max_drawdown']*100:.2f}%")
        print(f"  Value at Risk (95%): {risk['var_95']*100:.2f}%")
        
        # Portfolio Metrics
        portfolio = metrics['portfolio_metrics']
        print(f"\n📊 PORTFOLIO METRICS:")
        print(f"  Portfolio Average Return: {portfolio['portfolio_average_return']:+.2f}%")
        print(f"  Portfolio Total Return: {portfolio['portfolio_total_return']:+.2f}%")
        print(f"  Portfolio Sharpe Ratio: {portfolio['portfolio_sharpe']:.3f}")
        print(f"  Portfolio Win Rate: {portfolio['portfolio_win_rate']:.1f}%")
        
        # Ticker Analysis
        detailed = metrics['detailed_analysis']
        print(f"\n🏢 TICKER ANALYSIS:")
        for ticker, analysis in detailed.items():
            print(f"  {ticker}:")
            print(f"    Average Return: {analysis['average_return']:+.2f}%")
            print(f"    Total Return: {analysis['total_return']:+.2f}%")
            print(f"    Win Rate: {analysis['win_rate']:.1f}%")
            print(f"    Volatility: {analysis['volatility']:.2f}%")
        
        print("="*80)
    
    def save_performance_report(self, output_file: str = None):
        """Save performance metrics to JSON file"""
        if not self.performance_metrics:
            self.calculate_all_metrics()
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"testing_framework/backtest_results/performance_analysis_{timestamp}.json"
        
        # Add metadata
        report = {
            "analysis_info": {
                "source_file": self.results_file_path,
                "analysis_timestamp": datetime.now().isoformat(),
                "total_backtests": len(self.results.get('individual_results', [])),
                "method": self.results.get('summary', {}).get('method', 'unknown')
            },
            "performance_metrics": self.performance_metrics
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Performance analysis saved to: {output_file}")
        return output_file

def analyze_backtest_performance(results_file_path: str):
    """Convenience function to analyze backtest performance"""
    analyzer = PerformanceAnalyzer(results_file_path)
    analyzer.calculate_all_metrics()
    analyzer.print_performance_report()
    analyzer.save_performance_report()
    return analyzer

if __name__ == "__main__":
    # Find the most recent backtest results file
    results_dir = "testing_framework/backtest_results"
    
    if os.path.exists(results_dir):
        files = [f for f in os.listdir(results_dir) if f.startswith("consolidated_") and f.endswith(".json")]
        
        if files:
            # Get the most recent file
            latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(results_dir, f)))
            results_file_path = os.path.join(results_dir, latest_file)
            
            print(f"🔍 Analyzing performance from: {latest_file}")
            analyzer = analyze_backtest_performance(results_file_path)
        else:
            print("❌ No backtest results files found. Run backtests first.")
    else:
        print("❌ Results directory not found. Run backtests first.")
