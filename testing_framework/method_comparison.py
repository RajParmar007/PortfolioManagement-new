"""
Method Comparison Tool
Compares performance between Rule-based, Optimized LLM, and Original LLM methods
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Dict, List, Any
from performance_analyzer import PerformanceAnalyzer

class MethodComparison:
    """
    Compare performance across different portfolio management methods
    """
    
    def __init__(self, results_dir: str = "testing_framework/backtest_results"):
        self.results_dir = results_dir
        self.comparison_data = {}
        
    def find_latest_results(self) -> Dict[str, str]:
        """Find the latest results files for each method"""
        
        if not os.path.exists(self.results_dir):
            return {}
        
        files = os.listdir(self.results_dir)
        latest_files = {}
        
        methods = ["rule_based", "optimized_llm", "original_llm"]
        
        for method in methods:
            method_files = [f for f in files if f.startswith(f"consolidated_{method}_backtests_")]
            if method_files:
                # Get the most recent file
                latest_file = max(method_files, key=lambda f: os.path.getctime(os.path.join(self.results_dir, f)))
                latest_files[method] = os.path.join(self.results_dir, latest_file)
        
        return latest_files
    
    def load_all_results(self, file_paths: Dict[str, str] = None) -> Dict[str, Any]:
        """Load results from all available methods"""
        
        if file_paths is None:
            file_paths = self.find_latest_results()
        
        all_results = {}
        
        for method, file_path in file_paths.items():
            try:
                print(f"📊 Loading {method} results from {os.path.basename(file_path)}")
                analyzer = PerformanceAnalyzer(file_path)
                metrics = analyzer.calculate_all_metrics()
                
                all_results[method] = {
                    "file_path": file_path,
                    "metrics": metrics,
                    "raw_data": analyzer.results
                }
                
            except Exception as e:
                print(f"❌ Error loading {method} results: {str(e)}")
                continue
        
        return all_results
    
    def create_comparison_table(self, all_results: Dict[str, Any]) -> pd.DataFrame:
        """Create a comprehensive comparison table"""
        
        comparison_data = []
        
        for method, data in all_results.items():
            metrics = data["metrics"]
            
            # Extract key metrics
            basic = metrics.get("basic_metrics", {})
            accuracy = metrics.get("accuracy_metrics", {})
            returns = metrics.get("return_metrics", {})
            risk = metrics.get("risk_metrics", {})
            portfolio = metrics.get("portfolio_metrics", {})
            
            row = {
                "Method": method.replace("_", " ").title(),
                
                # Basic Performance
                "Total Recommendations": basic.get("total_recommendations", 0),
                "Win Rate (%)": round(basic.get("win_rate", 0), 1),
                "Avg Return (%)": round(basic.get("average_return", 0), 2),
                
                # Accuracy
                "Overall Accuracy (%)": round(accuracy.get("overall_accuracy", 0), 1),
                "BUY Accuracy (%)": round(accuracy.get("buy_accuracy", 0), 1),
                "SELL Accuracy (%)": round(accuracy.get("sell_accuracy", 0), 1),
                
                # Returns
                "Strategy Total Return (%)": round(returns.get("strategy_total_return", 0), 2),
                "Benchmark Total Return (%)": round(returns.get("benchmark_total_return", 0), 2),
                "Outperformance (%)": round(returns.get("outperformance", 0), 2),
                
                # Risk Metrics
                "Sharpe Ratio": round(risk.get("sharpe_ratio", 0), 3),
                "Volatility (%)": round(risk.get("volatility", 0) * 100, 2),
                "Max Drawdown (%)": round(risk.get("max_drawdown", 0) * 100, 2),
                
                # Portfolio Metrics
                "Portfolio Total Return (%)": round(portfolio.get("portfolio_total_return", 0), 2),
                "Portfolio Win Rate (%)": round(portfolio.get("portfolio_win_rate", 0), 1),
                
                # Recommendation Distribution
                "BUY (%)": round(basic.get("buy_percentage", 0), 1),
                "SELL (%)": round(basic.get("sell_percentage", 0), 1),
                "HOLD (%)": round(basic.get("hold_percentage", 0), 1),
            }
            
            comparison_data.append(row)
        
        return pd.DataFrame(comparison_data)
    
    def print_comparison_report(self, comparison_df: pd.DataFrame):
        """Print a formatted comparison report"""
        
        print("\n" + "="*100)
        print("📊 PORTFOLIO MANAGEMENT METHODS COMPARISON")
        print("="*100)
        
        # Key Performance Metrics
        print("\n🎯 KEY PERFORMANCE METRICS:")
        key_metrics = ["Method", "Win Rate (%)", "Avg Return (%)", "Overall Accuracy (%)", "Sharpe Ratio"]
        print(comparison_df[key_metrics].to_string(index=False))
        
        # Return Metrics
        print("\n💰 RETURN METRICS:")
        return_metrics = ["Method", "Strategy Total Return (%)", "Outperformance (%)", "Portfolio Total Return (%)"]
        print(comparison_df[return_metrics].to_string(index=False))
        
        # Risk Metrics
        print("\n⚠️ RISK METRICS:")
        risk_metrics = ["Method", "Volatility (%)", "Max Drawdown (%)", "Sharpe Ratio"]
        print(comparison_df[risk_metrics].to_string(index=False))
        
        # Accuracy Breakdown
        print("\n🎯 ACCURACY BREAKDOWN:")
        accuracy_metrics = ["Method", "Overall Accuracy (%)", "BUY Accuracy (%)", "SELL Accuracy (%)"]
        print(comparison_df[accuracy_metrics].to_string(index=False))
        
        # Recommendation Distribution
        print("\n📈 RECOMMENDATION DISTRIBUTION:")
        rec_metrics = ["Method", "BUY (%)", "SELL (%)", "HOLD (%)"]
        print(comparison_df[rec_metrics].to_string(index=False))
        
        # Best Performer Analysis
        print("\n🏆 BEST PERFORMERS:")
        print(f"  Highest Win Rate: {comparison_df.loc[comparison_df['Win Rate (%)'].idxmax(), 'Method']} ({comparison_df['Win Rate (%)'].max():.1f}%)")
        print(f"  Best Returns: {comparison_df.loc[comparison_df['Strategy Total Return (%)'].idxmax(), 'Method']} ({comparison_df['Strategy Total Return (%)'].max():+.2f}%)")
        print(f"  Best Accuracy: {comparison_df.loc[comparison_df['Overall Accuracy (%)'].idxmax(), 'Method']} ({comparison_df['Overall Accuracy (%)'].max():.1f}%)")
        print(f"  Best Sharpe Ratio: {comparison_df.loc[comparison_df['Sharpe Ratio'].idxmax(), 'Method']} ({comparison_df['Sharpe Ratio'].max():.3f})")
        print(f"  Lowest Risk: {comparison_df.loc[comparison_df['Volatility (%)'].idxmin(), 'Method']} ({comparison_df['Volatility (%)'].min():.2f}% volatility)")
        
        print("="*100)
    
    def save_comparison_results(self, comparison_df: pd.DataFrame, all_results: Dict[str, Any]):
        """Save comparison results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save comparison table as CSV
        csv_path = os.path.join(self.results_dir, f"performance_comparison_{timestamp}.csv")
        comparison_df.to_csv(csv_path, index=False)
        
        # Save detailed comparison as JSON
        json_path = os.path.join(self.results_dir, f"detailed_comparison_{timestamp}.json")
        
        comparison_summary = {
            "comparison_info": {
                "timestamp": datetime.now().isoformat(),
                "methods_compared": list(all_results.keys()),
                "total_methods": len(all_results)
            },
            "summary_table": comparison_df.to_dict('records'),
            "detailed_metrics": {method: data["metrics"] for method, data in all_results.items()},
            "file_sources": {method: data["file_path"] for method, data in all_results.items()}
        }
        
        with open(json_path, 'w') as f:
            json.dump(comparison_summary, f, indent=2, default=str)
        
        print(f"\n💾 Comparison results saved:")
        print(f"  📊 Summary table: {csv_path}")
        print(f"  📋 Detailed analysis: {json_path}")
        
        return csv_path, json_path
    
    def run_full_comparison(self):
        """Run complete comparison analysis"""
        
        print("🔍 Starting method comparison analysis...")
        
        # Load all available results
        all_results = self.load_all_results()
        
        if not all_results:
            print("❌ No backtest results found. Run backtests first.")
            return None
        
        print(f"✅ Found results for {len(all_results)} methods: {list(all_results.keys())}")
        
        # Create comparison table
        comparison_df = self.create_comparison_table(all_results)
        
        # Print comparison report
        self.print_comparison_report(comparison_df)
        
        # Save results
        csv_path, json_path = self.save_comparison_results(comparison_df, all_results)
        
        return {
            "comparison_table": comparison_df,
            "detailed_results": all_results,
            "csv_path": csv_path,
            "json_path": json_path
        }

def compare_methods():
    """Convenience function to run method comparison"""
    comparator = MethodComparison()
    return comparator.run_full_comparison()

if __name__ == "__main__":
    print("🚀 Starting Portfolio Management Methods Comparison")
    results = compare_methods()
    
    if results:
        print("✅ Comparison completed!")
    else:
        print("❌ Comparison failed - no results to compare.")
