"""
Data Alignment Checker for Backtesting
Validates that news and Reddit data align with stock data dates to prevent look-ahead bias
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

class DataAlignmentChecker:
    """
    Check and fix data alignment issues in backtesting
    """
    
    def __init__(self):
        pass
    
    def check_backtest_data_alignment(self, results_file: str) -> Dict[str, Any]:
        """
        Check data alignment in a backtest results file
        
        Args:
            results_file: Path to consolidated backtest results JSON
            
        Returns:
            Dictionary with alignment analysis
        """
        
        print(f"🔍 Checking data alignment in {os.path.basename(results_file)}")
        
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        alignment_issues = []
        
        for i, backtest in enumerate(results.get('individual_results', [])):
            backtest_info = backtest.get('backtest_info', {})
            start_date = backtest_info.get('start_date')
            end_date = backtest_info.get('end_date')
            
            print(f"\n📊 Backtest {i+1}: {start_date} to {end_date}")
            
            if not start_date or not end_date:
                continue
                
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            historical_data = backtest.get('historical_data', {})
            
            for ticker, data in historical_data.items():
                print(f"  Checking {ticker}...")
                
                # Check stock data alignment
                stock_alignment = self._check_stock_data_alignment(
                    data.get('stock', ''), start_dt, end_dt, ticker
                )
                
                # Check news data alignment
                news_alignment = self._check_news_data_alignment(
                    data.get('news', ''), start_dt, end_dt, ticker
                )
                
                # Check Reddit data alignment
                reddit_alignment = self._check_reddit_data_alignment(
                    data.get('reddit', []), start_dt, end_dt, ticker
                )
                
                if stock_alignment['issues'] or news_alignment['issues'] or reddit_alignment['issues']:
                    alignment_issues.append({
                        'backtest': i+1,
                        'ticker': ticker,
                        'period': f"{start_date} to {end_date}",
                        'stock_issues': stock_alignment['issues'],
                        'news_issues': news_alignment['issues'],
                        'reddit_issues': reddit_alignment['issues']
                    })
        
        return {
            'total_backtests': len(results.get('individual_results', [])),
            'alignment_issues': alignment_issues,
            'has_issues': len(alignment_issues) > 0
        }
    
    def _check_stock_data_alignment(self, stock_data: str, start_dt: datetime, end_dt: datetime, ticker: str) -> Dict[str, Any]:
        """Check if stock data aligns with backtest period"""
        
        issues = []
        
        try:
            if stock_data.startswith('{'):
                data = json.loads(stock_data)
                
                # Convert timestamps to dates
                dates = []
                for timestamp_str in data.keys():
                    timestamp_ms = int(timestamp_str)
                    date = datetime.fromtimestamp(timestamp_ms / 1000)
                    dates.append(date)
                
                if dates:
                    earliest_date = min(dates)
                    latest_date = max(dates)
                    
                    print(f"    📈 Stock data: {earliest_date.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}")
                    
                    # Check if stock data covers the backtest period
                    if earliest_date > start_dt:
                        issues.append(f"Stock data starts after backtest start ({earliest_date.strftime('%Y-%m-%d')} > {start_dt.strftime('%Y-%m-%d')})")
                    
                    if latest_date < end_dt:
                        issues.append(f"Stock data ends before backtest end ({latest_date.strftime('%Y-%m-%d')} < {end_dt.strftime('%Y-%m-%d')})")
                else:
                    issues.append("No stock data found")
            else:
                issues.append(f"Stock data error: {stock_data[:100]}...")
                
        except Exception as e:
            issues.append(f"Error parsing stock data: {str(e)}")
        
        return {'issues': issues}
    
    def _check_news_data_alignment(self, news_data: str, start_dt: datetime, end_dt: datetime, ticker: str) -> Dict[str, Any]:
        """Check if news data aligns with backtest period"""
        
        issues = []
        
        if news_data.startswith("Error"):
            issues.append(f"News data error: {news_data}")
            print(f"    📰 News: ERROR - {news_data[:50]}...")
        else:
            # For now, we can't easily extract dates from news headlines
            # This would require parsing the NewsAPI response format
            print(f"    📰 News: Available (cannot verify dates from current format)")
        
        return {'issues': issues}
    
    def _check_reddit_data_alignment(self, reddit_data: List[Dict], start_dt: datetime, end_dt: datetime, ticker: str) -> Dict[str, Any]:
        """Check if Reddit data aligns with backtest period"""
        
        issues = []
        
        if isinstance(reddit_data, list):
            dates_in_range = 0
            dates_out_of_range = 0
            future_posts = []
            
            for post in reddit_data:
                if isinstance(post, dict) and 'created_date' in post:
                    post_date_str = post['created_date']
                    try:
                        post_date = datetime.strptime(post_date_str, '%Y-%m-%d')
                        
                        if start_dt <= post_date <= end_dt:
                            dates_in_range += 1
                        else:
                            dates_out_of_range += 1
                            if post_date > end_dt:
                                future_posts.append({
                                    'title': post.get('title', '')[:50] + '...',
                                    'date': post_date_str
                                })
                    except ValueError:
                        issues.append(f"Invalid Reddit post date format: {post_date_str}")
            
            print(f"    🔴 Reddit: {dates_in_range} posts in range, {dates_out_of_range} out of range")
            
            if future_posts:
                issues.append(f"Found {len(future_posts)} Reddit posts from the future (look-ahead bias)")
                for post in future_posts[:3]:  # Show first 3
                    issues.append(f"  Future post: '{post['title']}' from {post['date']}")
            
        elif isinstance(reddit_data, str) and reddit_data.startswith("Error"):
            issues.append(f"Reddit data error: {reddit_data}")
            print(f"    🔴 Reddit: ERROR - {reddit_data[:50]}...")
        else:
            print(f"    🔴 Reddit: Unknown format")
        
        return {'issues': issues}
    
    def print_alignment_report(self, alignment_results: Dict[str, Any]):
        """Print a formatted alignment report"""
        
        print("\n" + "="*80)
        print("🔍 DATA ALIGNMENT ANALYSIS REPORT")
        print("="*80)
        
        total_backtests = alignment_results['total_backtests']
        issues = alignment_results['alignment_issues']
        
        print(f"📊 Total backtests analyzed: {total_backtests}")
        print(f"⚠️  Backtests with alignment issues: {len(issues)}")
        
        if not issues:
            print("✅ No alignment issues found!")
            return
        
        print(f"\n🚨 ALIGNMENT ISSUES FOUND:")
        
        for issue in issues:
            print(f"\n📍 Backtest {issue['backtest']} - {issue['ticker']} ({issue['period']}):")
            
            if issue['stock_issues']:
                print(f"  📈 Stock Data Issues:")
                for stock_issue in issue['stock_issues']:
                    print(f"    - {stock_issue}")
            
            if issue['news_issues']:
                print(f"  📰 News Data Issues:")
                for news_issue in issue['news_issues']:
                    print(f"    - {news_issue}")
            
            if issue['reddit_issues']:
                print(f"  🔴 Reddit Data Issues:")
                for reddit_issue in issue['reddit_issues']:
                    print(f"    - {reddit_issue}")
        
        print("\n" + "="*80)
        print("💡 RECOMMENDATIONS:")
        print("1. Fix NewsAPI historical access limitations")
        print("2. Filter Reddit posts to only include dates within backtest period")
        print("3. Consider using mock data for consistent testing")
        print("4. Validate all data sources before running analysis")
        print("="*80)

def check_latest_backtest_alignment():
    """Check alignment for the most recent backtest results"""
    
    results_dir = "testing_framework/backtest_results"
    
    if not os.path.exists(results_dir):
        print("❌ No backtest results directory found")
        return
    
    # Find the most recent LLM results file
    files = [f for f in os.listdir(results_dir) if f.startswith("consolidated_optimized_llm_backtests_")]
    
    if not files:
        print("❌ No LLM backtest results found")
        return
    
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(results_dir, f)))
    file_path = os.path.join(results_dir, latest_file)
    
    checker = DataAlignmentChecker()
    results = checker.check_backtest_data_alignment(file_path)
    checker.print_alignment_report(results)
    
    return results

if __name__ == "__main__":
    print("🔍 Starting Data Alignment Check")
    results = check_latest_backtest_alignment()
