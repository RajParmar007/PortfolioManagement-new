"""
Runner script for Model Comparison Framework
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_comparison_framework import run_model_comparison

if __name__ == "__main__":
    print("🚀 Starting AI Model vs Rule-Based Strategies Comparison (SMA EMPHASIS)")
    print("=" * 60)
    
    try:
        # Clear LLM cache to ensure new prompt is used
        from testing_agents import clear_testing_caches
        clear_testing_caches()
        print("🧹 Cleared testing caches for fresh run with SMA emphasis")
        
        # Run the comparison for AAPL over 3 months
        results = run_model_comparison("AAPL", 3)
        
        print("\n🎉 Comparison completed successfully!")
        print("📊 Check the results above and in the saved files.")
        
    except Exception as e:
        print(f"\n❌ Error running comparison: {str(e)}")
        print("Please check your dependencies and data availability.")
        
        # Print some debugging info
        print(f"\nDebugging info:")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path[:3]}...")  # First 3 entries
        
        import traceback
        traceback.print_exc()
