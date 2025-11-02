"""
Run LLM Backtests and Compare with Rule-based Results
Uses cached analysis data to avoid redundant API calls
"""

import time
import json
import os
from datetime import datetime
from backtesting_framework import PortfolioBacktester
from method_comparison import compare_methods

def run_llm_backtests_and_compare(num_backtests: int = 3):
    """
    Run LLM backtests and automatically compare with existing rule-based results
    
    Args:
        num_backtests: Number of backtests to run (start with 3 for testing)
    """
    
    print("🚀 Starting LLM Backtesting and Comparison Pipeline")
    print("="*80)
    
    # Record start time
    start_time = time.time()
    
    print(f"⏱️  Estimated runtime: {num_backtests * 1} minutes")
    print(f"📊 Running {num_backtests} optimized LLM backtests...")
    print("="*80)
    
    try:
        # Use cached analysis results to avoid API calls
        llm_results = run_cached_llm_backtests(num_backtests=num_backtests)
        
        # Calculate actual runtime
        end_time = time.time()
        runtime_minutes = (end_time - start_time) / 60
        
        print(f"\n✅ LLM backtests completed in {runtime_minutes:.1f} minutes")
        print(f"⚡ Average time per backtest: {runtime_minutes/num_backtests:.1f} minutes")
        
        # Run comparison analysis
        print("\n" + "="*80)
        print("📊 RUNNING PERFORMANCE COMPARISON")
        print("="*80)
        
        comparison_results = compare_methods()
        
        if comparison_results:
            print(f"\n🎉 ANALYSIS COMPLETE!")
            print(f"📊 Comparison table saved to: {comparison_results['csv_path']}")
            print(f"📋 Detailed analysis saved to: {comparison_results['json_path']}")
            
            # Quick summary
            df = comparison_results['comparison_table']
            if len(df) >= 2:  # At least rule-based and LLM results
                print(f"\n🏆 QUICK COMPARISON SUMMARY:")
                for _, row in df.iterrows():
                    method = row['Method']
                    win_rate = row['Win Rate (%)']
                    accuracy = row['Overall Accuracy (%)']
                    returns = row['Strategy Total Return (%)']
                    sharpe = row['Sharpe Ratio']
                    
                    print(f"  {method}:")
                    print(f"    Win Rate: {win_rate}% | Accuracy: {accuracy}% | Returns: {returns:+.2f}% | Sharpe: {sharpe:.3f}")
        
        return {
            "llm_results": llm_results,
            "comparison_results": comparison_results,
            "runtime_minutes": runtime_minutes
        }
        
    except Exception as e:
        print(f"❌ Error during backtesting: {str(e)}")
        return None

def run_cached_llm_backtests(num_backtests: int = 3):
    """
    Run LLM backtests using cached analysis data from weight optimizer
    """
    
    cache_file = "testing_framework/backtest_results/analysis_cache.json"
    
    # Load cached analysis results
    if not os.path.exists(cache_file):
        print("❌ No cached analysis data found. Run weight optimizer first!")
        return None
    
    with open(cache_file, 'r') as f:
        cached_data = json.load(f)
    
    print(f"📦 Using cached analysis data ({len(cached_data)} periods available)")
    
    # Get the date ranges we need (same as weight optimizer)
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
    
    date_ranges = successful_ranges[:num_backtests]
    
    # Initialize backtester
    backtester = PortfolioBacktester(["AAPL", "AMZN", "ADBE"])
    
    all_results = []
    successful_backtests = 0
    
    for i, (start_date, end_date) in enumerate(date_ranges, 1):
        cache_key = f"{start_date}_{end_date}"
        
        if cache_key not in cached_data:
            print(f"⚠️  No cached data for {start_date} to {end_date}, skipping...")
            continue
            
        print(f"\n==================== BACKTEST {i}/{num_backtests} ====================")
        print(f"🚀 Starting backtest for ['AAPL', 'AMZN', 'ADBE']")
        print(f"📅 Date range: {start_date} to {end_date}")
        print(f"🤖 Method: optimized_llm (using cached data)")
        print("=" * 60)
        
        try:
            # Use cached analysis results
            cached_period = cached_data[cache_key]
            analysis_results = cached_period['analysis_results']
            
            print("📦 Using cached analysis results (no API calls)")
            
            # Run LLM portfolio manager with cached data
            portfolio_recommendation = backtester._run_optimized_llm_portfolio_manager(analysis_results)
            
            # Calculate actual performance
            actual_performance = backtester._calculate_actual_performance(start_date, end_date)
            
            # Compile results
            backtest_results = {
                "backtest_info": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "tickers": backtester.test_tickers,
                    "method": "optimized_llm",
                    "run_time": datetime.now().isoformat(),
                    "used_cache": True
                },
                "historical_data": cached_period['historical_data'],
                "analysis_results": analysis_results,
                "portfolio_recommendation": portfolio_recommendation,
                "actual_performance": actual_performance
            }
            
            all_results.append(backtest_results)
            successful_backtests += 1
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 BACKTEST SUMMARY")
            print("=" * 60)
            print(f"📅 Period: {start_date} to {end_date}")
            print(f"📈 Tickers: {', '.join(backtester.test_tickers)}")
            print(f"🕐 Run Time: {datetime.now().isoformat()}")
            
            print(f"\n💼 PORTFOLIO RECOMMENDATION:")
            if isinstance(portfolio_recommendation, dict) and 'recommendation' in portfolio_recommendation:
                print(portfolio_recommendation['recommendation'])
            
            print(f"\n📈 ACTUAL PERFORMANCE (30 days after):")
            for ticker, perf in actual_performance.items():
                if isinstance(perf, dict) and 'percent_change' in perf:
                    print(f"  {ticker}: {perf['percent_change']:+.2f}% (${perf['price_change']:+.2f})")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Backtest {i} failed: {str(e)}")
            continue
    
    # Save consolidated results
    if all_results:
        save_cached_llm_results(all_results)
    
    print(f"\n" + "=" * 60)
    print("📊 OVERALL BACKTEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful backtests: {successful_backtests}/{num_backtests}")
    
    return all_results

def save_cached_llm_results(all_results):
    """Save cached LLM backtest results"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = "testing_framework/backtest_results"
    os.makedirs(results_dir, exist_ok=True)
    
    filename = f"consolidated_optimized_llm_backtests_{timestamp}.json"
    filepath = os.path.join(results_dir, filename)
    
    consolidated_results = {
        "summary": {
            "total_backtests": len(all_results),
            "method": "optimized_llm",
            "tickers": ["AAPL", "AMZN", "ADBE"],
            "timestamp": datetime.now().isoformat(),
            "used_cache": True
        },
        "individual_results": all_results
    }
    
    with open(filepath, 'w') as f:
        json.dump(consolidated_results, f, indent=2, default=str)
    
    print(f"💾 Consolidated results saved to: {filepath}")

if __name__ == "__main__":
    # Run 3 LLM backtests first (for testing)
    results = run_llm_backtests_and_compare(num_backtests=3)
    
    if results:
        print(f"\n✅ Pipeline completed successfully!")
        print(f"⏱️  Total runtime: {results['runtime_minutes']:.1f} minutes")
    else:
        print(f"\n❌ Pipeline failed!")
