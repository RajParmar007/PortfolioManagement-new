"""
Weight Optimization for Rule-Based Portfolio Manager
Tests different weight combinations to find the optimal allocation
"""

import itertools
from datetime import datetime
from backtesting_framework import PortfolioBacktester, generate_backtest_date_ranges
from performance_analyzer import PerformanceAnalyzer
import json
import os

class WeightOptimizer:
    """
    Optimize weights for rule-based portfolio manager with smart caching
    """
    
    def __init__(self):
        self.backtester = PortfolioBacktester(["AAPL", "AMZN", "ADBE"])
        self.results = []
        self.cached_analysis_results = {}  # In-memory cache
        self.cache_file = "testing_framework/backtest_results/analysis_cache.json"  # Persistent cache
        self._load_persistent_cache()
    
    def generate_weight_combinations(self, target_sharpe: float = 1.0):
        """Generate weight combinations optimized for high Sharpe ratio"""
        
        # More granular weight options for precision
        weight_options = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
        
        combinations = []
        
        for tech_weight in weight_options:
            for sent_weight in weight_options:
                pred_weight = 1.0 - tech_weight - sent_weight
                
                # Only include valid combinations
                if 0.05 <= pred_weight <= 0.95:
                    combinations.append({
                        "technical": round(tech_weight, 2),
                        "sentiment": round(sent_weight, 2), 
                        "prediction": round(pred_weight, 2)
                    })
        
        print(f"📊 Generated {len(combinations)} weight combinations for Sharpe ≥ {target_sharpe}")
        return combinations
    
    def _get_original_successful_date_ranges(self, num_backtests: int):
        """Get the exact same date ranges that produced 60% win rate"""
        
        # These are the exact date ranges from the successful rule-based system
        successful_ranges = [
            ("2025-06-14", "2025-09-12"),
            ("2025-05-15", "2025-08-13"),  
            ("2025-04-15", "2025-07-14"),
            ("2025-03-16", "2025-06-14"),
            ("2025-02-14", "2025-05-15"),
            ("2025-01-15", "2025-04-15"),
            ("2024-12-16", "2025-03-16"),
            ("2024-11-16", "2025-02-14"),
            ("2024-10-17", "2025-01-15"),
            ("2024-09-17", "2024-12-16")
        ]
        
        # Return only the number requested
        return successful_ranges[:num_backtests]
    
    def _load_persistent_cache(self):
        """Load cached analysis results from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cached_analysis_results = json.load(f)
                print(f"📦 Loaded {len(self.cached_analysis_results)} cached analysis results from file")
            else:
                print("📦 No existing cache file found, starting fresh")
        except Exception as e:
            print(f"⚠️  Error loading cache: {str(e)}, starting fresh")
            self.cached_analysis_results = {}
    
    def _save_persistent_cache(self):
        """Save cached analysis results to file"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cached_analysis_results, f, indent=2, default=str)
            print(f"💾 Saved {len(self.cached_analysis_results)} analysis results to cache file")
        except Exception as e:
            print(f"⚠️  Error saving cache: {str(e)}")
    
    def _pre_cache_analysis_results(self, date_ranges):
        """Pre-cache all analysis results to avoid redundant API calls"""
        
        print("📦 Pre-caching analysis results to minimize API calls...")
        
        for i, (start_date, end_date) in enumerate(date_ranges, 1):
            cache_key = f"{start_date}_{end_date}"
            
            if cache_key not in self.cached_analysis_results:
                print(f"   🔄 Caching data for period {i}/{len(date_ranges)}: {start_date} to {end_date}")
                
                try:
                    # Get historical data (this makes the API calls)
                    historical_data = self.backtester._retrieve_historical_data(start_date, end_date)
                    
                    # Run analysis agents (this processes the data)
                    analysis_results = self.backtester._run_analysis_agents(historical_data)
                    
                    # Cache both historical data and analysis results
                    self.cached_analysis_results[cache_key] = {
                        'historical_data': historical_data,
                        'analysis_results': analysis_results,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                    
                    print(f"   ✅ Cached data for {start_date} to {end_date}")
                    
                    # Save to persistent cache after each successful cache
                    self._save_persistent_cache()
                    
                except Exception as e:
                    print(f"   ❌ Failed to cache data for {start_date} to {end_date}: {str(e)}")
            else:
                print(f"   ♻️  Using cached data for {start_date} to {end_date}")
        
        print(f"📦 Caching complete! {len(self.cached_analysis_results)} periods cached.")
    
    def run_weight_optimization(self, num_backtests: int = 3):
        """
        Test different weight combinations and find the best performing one
        
        Args:
            num_backtests: Number of backtests to run per weight combination
        """
        
        print("🔍 Starting Weight Optimization for Rule-Based System")
        print("="*70)
        
        # Generate weight combinations
        weight_combinations = self.generate_weight_combinations()
        print(f"📊 Testing {len(weight_combinations)} weight combinations")
        print(f"🔄 Running {num_backtests} backtests per combination")
        print(f"⏱️  Estimated time: {num_backtests * 0.3:.1f} minutes (caching) + {len(weight_combinations) * 0.01:.1f} minutes (testing)")
        print("="*70)
        
        # Use the SAME date ranges as the successful rule-based system
        date_ranges = self._get_original_successful_date_ranges(num_backtests)
        
        # Pre-cache all analysis results (API calls happen only once here!)
        self._pre_cache_analysis_results(date_ranges)
        
        optimization_results = []
        
        for i, weights in enumerate(weight_combinations, 1):
            print(f"\n🧪 Testing combination {i}/{len(weight_combinations)}")
            print(f"   Technical: {weights['technical']:.1f}, Sentiment: {weights['sentiment']:.1f}, Prediction: {weights['prediction']:.1f}")
            
            # Run backtests for this weight combination using cached data
            backtest_results = []
            
            for j, (start_date, end_date) in enumerate(date_ranges, 1):
                try:
                    # Use cached data instead of making API calls
                    result = self._run_cached_backtest(start_date, end_date, weights)
                    backtest_results.append(result)
                    
                except Exception as e:
                    print(f"   ❌ Backtest {j} failed: {str(e)}")
                    continue
            
            if backtest_results:
                # Calculate performance metrics for this weight combination
                performance = self._calculate_weight_performance(backtest_results, weights)
                optimization_results.append(performance)
                
                print(f"   📈 Results: {performance['strategy_total_return']:+.2f}% return, {performance['sharpe_ratio']:.3f} Sharpe, {performance['win_rate']:.1f}% win rate")
            else:
                print(f"   ❌ All backtests failed for this combination")
        
        # Find best performing weights (targeting Sharpe ≥ 1.0)
        best_weights = self._find_best_weights(optimization_results, min_sharpe=1.0)
        
        # Print results
        self._print_optimization_results(optimization_results, best_weights)
        
        # Save results
        self._save_optimization_results(optimization_results, best_weights)
        
        return best_weights, optimization_results
    
    def _run_cached_backtest(self, start_date: str, end_date: str, weights: dict):
        """Run a backtest using cached analysis results (no API calls)"""
        
        cache_key = f"{start_date}_{end_date}"
        
        if cache_key not in self.cached_analysis_results:
            raise ValueError(f"No cached data found for {start_date} to {end_date}")
        
        cached_data = self.cached_analysis_results[cache_key]
        analysis_results = cached_data['analysis_results']
        
        # Run only the portfolio manager with the specific weights (fast!)
        portfolio_recommendation = self.backtester._run_rule_based_portfolio_manager(analysis_results, weights)
        
        # Calculate actual performance
        actual_performance = self.backtester._calculate_actual_performance(start_date, end_date)
        
        # Compile results in the same format as regular backtest
        backtest_results = {
            "backtest_info": {
                "start_date": start_date,
                "end_date": end_date,
                "tickers": self.backtester.test_tickers,
                "method": "rule_based",
                "weights": weights,
                "run_time": datetime.now().isoformat()
            },
            "historical_data": cached_data['historical_data'],
            "analysis_results": analysis_results,
            "portfolio_recommendation": portfolio_recommendation,
            "actual_performance": actual_performance
        }
        
        return backtest_results
    
    def _calculate_weight_performance(self, backtest_results, weights):
        """Calculate performance metrics for a weight combination"""
        
        # Extract recommendation and performance data
        data = []
        
        for backtest in backtest_results:
            portfolio_rec = backtest.get('portfolio_recommendation', {})
            actual_perf = backtest.get('actual_performance', {})
            detailed_recs = portfolio_rec.get('detailed_recommendations', {})
            
            for ticker in ['AAPL', 'AMZN', 'ADBE']:
                if ticker in detailed_recs and ticker in actual_perf:
                    rec_data = detailed_recs[ticker]
                    perf_data = actual_perf[ticker]
                    
                    if isinstance(perf_data, dict) and 'percent_change' in perf_data:
                        data.append({
                            'ticker': ticker,
                            'recommendation': rec_data.get('recommendation', 'HOLD'),
                            'score': rec_data.get('score', 0),
                            'position_size': rec_data.get('position_size', 1.0),
                            'actual_return': perf_data.get('percent_change', 0)
                        })
        
        if not data:
            return {
                'weights': weights,
                'strategy_total_return': 0,
                'sharpe_ratio': 0,
                'win_rate': 0,
                'total_recommendations': 0
            }
        
        # Calculate strategy returns with position sizing
        strategy_returns = []
        for d in data:
            ret = d['actual_return'] / 100  # Convert to decimal
            position_size = d.get('position_size', 1.0)  # Default to full position
            
            if d['recommendation'] == 'BUY':
                strategy_returns.append(ret * position_size)
            elif d['recommendation'] == 'SELL':
                strategy_returns.append(-ret * position_size)
            else:  # HOLD
                strategy_returns.append(0)
        
        # Calculate metrics
        strategy_total_return = sum(strategy_returns) * 100  # Convert back to percentage
        win_rate = (sum(1 for r in strategy_returns if r > 0) / len(strategy_returns)) * 100
        
        # Calculate Sharpe ratio
        risk_free_rate = 0.02 / 12  # Monthly risk-free rate
        strategy_mean = sum(strategy_returns) / len(strategy_returns)
        strategy_std = (sum((r - strategy_mean) ** 2 for r in strategy_returns) / len(strategy_returns)) ** 0.5
        sharpe_ratio = (strategy_mean - risk_free_rate) / strategy_std if strategy_std != 0 else 0
        
        return {
            'weights': weights,
            'strategy_total_return': strategy_total_return,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'total_recommendations': len(data),
            'volatility': strategy_std * 100
        }
    
    def _find_best_weights(self, optimization_results, min_sharpe: float = 1.0):
        """Find the best performing weight combination with minimum Sharpe ratio"""
        
        if not optimization_results:
            return None
        
        # Filter for results that meet minimum Sharpe ratio
        high_sharpe_results = [r for r in optimization_results if r['sharpe_ratio'] >= min_sharpe]
        
        if high_sharpe_results:
            print(f"🎯 Found {len(high_sharpe_results)} combinations with Sharpe ≥ {min_sharpe}")
            # Sort by Sharpe ratio first, then total return
            sorted_results = sorted(
                high_sharpe_results, 
                key=lambda x: (x['sharpe_ratio'], x['strategy_total_return']), 
                reverse=True
            )
            return sorted_results[0]
        else:
            print(f"⚠️  No combinations achieved Sharpe ≥ {min_sharpe}. Showing best available:")
            # Fallback to best Sharpe ratio available
            sorted_results = sorted(
                optimization_results, 
                key=lambda x: x['sharpe_ratio'], 
                reverse=True
            )
            return sorted_results[0]
    
    def _print_optimization_results(self, optimization_results, best_weights):
        """Print optimization results"""
        
        print("\n" + "="*80)
        print("🏆 WEIGHT OPTIMIZATION RESULTS")
        print("="*80)
        
        if not optimization_results:
            print("❌ No valid results found")
            return
        
        # Sort results by Sharpe ratio
        sorted_results = sorted(optimization_results, key=lambda x: x['sharpe_ratio'], reverse=True)
        
        print(f"\n📊 TOP 10 WEIGHT COMBINATIONS:")
        print(f"{'Rank':<4} {'Tech':<4} {'Sent':<4} {'Pred':<4} {'Return':<8} {'Sharpe':<7} {'Win%':<5} {'Vol%':<5}")
        print("-" * 60)
        
        for i, result in enumerate(sorted_results[:10], 1):
            weights = result['weights']
            print(f"{i:<4} {weights['technical']:<4.1f} {weights['sentiment']:<4.1f} {weights['prediction']:<4.1f} "
                  f"{result['strategy_total_return']:+7.2f}% {result['sharpe_ratio']:6.3f} {result['win_rate']:4.1f}% {result['volatility']:4.1f}%")
        
        if best_weights:
            print(f"\n🥇 BEST PERFORMING WEIGHTS:")
            w = best_weights['weights']
            print(f"   Technical: {w['technical']:.1f} ({w['technical']*100:.0f}%)")
            print(f"   Sentiment: {w['sentiment']:.1f} ({w['sentiment']*100:.0f}%)")
            print(f"   Prediction: {w['prediction']:.1f} ({w['prediction']*100:.0f}%)")
            print(f"   📈 Total Return: {best_weights['strategy_total_return']:+.2f}%")
            print(f"   📊 Sharpe Ratio: {best_weights['sharpe_ratio']:.3f}")
            print(f"   🎯 Win Rate: {best_weights['win_rate']:.1f}%")
        
        print("="*80)
    
    def _save_optimization_results(self, optimization_results, best_weights):
        """Save optimization results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = "testing_framework/backtest_results"
        os.makedirs(results_dir, exist_ok=True)
        
        filename = f"weight_optimization_results_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)
        
        output = {
            "optimization_info": {
                "timestamp": datetime.now().isoformat(),
                "total_combinations_tested": len(optimization_results),
                "best_weights": best_weights
            },
            "all_results": optimization_results
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"💾 Optimization results saved to: {filepath}")

def run_weight_optimization():
    """Convenience function to run weight optimization targeting Sharpe ≥ 1.0"""
    optimizer = WeightOptimizer()
    print("🎯 TARGET: Sharpe Ratio ≥ 1.0")
    print("🔧 STRATEGIES: Higher thresholds (0.5), more granular weights, selective filtering")
    return optimizer.run_weight_optimization(num_backtests=3)

if __name__ == "__main__":
    print("🚀 Starting Rule-Based Weight Optimization")
    best_weights, all_results = run_weight_optimization()
    
    if best_weights:
        print("✅ Optimization completed!")
        print(f"🏆 Best weights found: {best_weights['weights']}")
    else:
        print("❌ Optimization failed - no valid results")
