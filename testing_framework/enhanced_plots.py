import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_results():
    """Load the results from the JSON file"""
    file_path = "testing_framework/comparison_results/model_comparison_AAPL_3months_20251013_171433.json"
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data

def rename_strategies(strategy_name):
    """Rename strategies for better presentation"""
    name_mapping = {
        'AI_Model': 'Portfolio Manager (AI)',
        'SMA_Crossover': 'Rule Based - SMA Crossover',
        'RSI': 'Rule Based - RSI',
        'MACD': 'Rule Based - MACD',
        'Bollinger_Bands': 'Rule Based - Bollinger Bands',
        'Combined_Technical': 'Rule Based - Combined Technical'
    }
    return name_mapping.get(strategy_name, strategy_name)

def get_strategy_colors():
    """Define distinct colors for each strategy"""
    colors = {
        'Portfolio Manager (AI)': '#FF4444',      # Bright Red
        'Rule Based - SMA Crossover': '#4444FF',  # Bright Blue  
        'Rule Based - RSI': '#44FF44',            # Bright Green
        'Rule Based - MACD': '#FF8800',          # Orange
        'Rule Based - Bollinger Bands': '#8844FF', # Purple
        'Rule Based - Combined Technical': '#FF4488' # Pink
    }
    return colors

def create_performance_dashboard():
    """Create a comprehensive performance dashboard"""
    
    data = load_results()
    colors = get_strategy_colors()
    
    # Prepare data
    strategies = []
    returns = []
    sharpe_ratios = []
    max_drawdowns = []
    win_rates = []
    portfolio_values = []
    volatilities = []
    calmar_ratios = []
    
    for strategy, metrics in data['performance_metrics'].items():
        renamed_strategy = rename_strategies(strategy)
        strategies.append(renamed_strategy)
        returns.append(metrics['total_return'])
        sharpe_ratios.append(metrics['sharpe_ratio'])
        max_drawdowns.append(abs(metrics['max_drawdown']))
        win_rates.append(metrics['win_rate'])
        portfolio_values.append(metrics['final_portfolio_value'])
        volatilities.append(metrics['volatility'])
        calmar_ratios.append(metrics['calmar_ratio'])
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 15))
    
    # Define colors for each strategy
    strategy_colors = [colors[strategy] for strategy in strategies]
    
    # 1. Total Returns (Top Left)
    ax1 = plt.subplot(3, 3, 1)
    bars1 = ax1.bar(range(len(strategies)), returns, color=strategy_colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax1.set_title('Total Returns (%)', fontsize=14, fontweight='bold', pad=20)
    ax1.set_ylabel('Return (%)', fontweight='bold')
    ax1.set_xticks(range(len(strategies)))
    ax1.set_xticklabels(strategies, rotation=45, ha='right')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars1, returns)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 2. Sharpe Ratios (Top Center)
    ax2 = plt.subplot(3, 3, 2)
    bars2 = ax2.bar(range(len(strategies)), sharpe_ratios, color=strategy_colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax2.set_title('Sharpe Ratios', fontsize=14, fontweight='bold', pad=20)
    ax2.set_ylabel('Sharpe Ratio', fontweight='bold')
    ax2.set_xticks(range(len(strategies)))
    ax2.set_xticklabels(strategies, rotation=45, ha='right')
    ax2.grid(axis='y', alpha=0.3)
    
    for i, (bar, value) in enumerate(zip(bars2, sharpe_ratios)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 3. Portfolio Values (Top Right)
    ax3 = plt.subplot(3, 3, 3)
    bars3 = ax3.bar(range(len(strategies)), portfolio_values, color=strategy_colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax3.set_title('Final Portfolio Values ($)', fontsize=14, fontweight='bold', pad=20)
    ax3.set_ylabel('Portfolio Value ($)', fontweight='bold')
    ax3.set_xticks(range(len(strategies)))
    ax3.set_xticklabels(strategies, rotation=45, ha='right')
    ax3.grid(axis='y', alpha=0.3)
    
    for i, (bar, value) in enumerate(zip(bars3, portfolio_values)):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'${value:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 4. Max Drawdown (Middle Left)
    ax4 = plt.subplot(3, 3, 4)
    bars4 = ax4.bar(range(len(strategies)), max_drawdowns, color=strategy_colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax4.set_title('Maximum Drawdown (%)', fontsize=14, fontweight='bold', pad=20)
    ax4.set_ylabel('Max Drawdown (%)', fontweight='bold')
    ax4.set_xticks(range(len(strategies)))
    ax4.set_xticklabels(strategies, rotation=45, ha='right')
    ax4.grid(axis='y', alpha=0.3)
    
    for i, (bar, value) in enumerate(zip(bars4, max_drawdowns)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 5. Win Rates (Middle Center)
    ax5 = plt.subplot(3, 3, 5)
    bars5 = ax5.bar(range(len(strategies)), win_rates, color=strategy_colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax5.set_title('Win Rates (%)', fontsize=14, fontweight='bold', pad=20)
    ax5.set_ylabel('Win Rate (%)', fontweight='bold')
    ax5.set_xticks(range(len(strategies)))
    ax5.set_xticklabels(strategies, rotation=45, ha='right')
    ax5.grid(axis='y', alpha=0.3)
    
    for i, (bar, value) in enumerate(zip(bars5, win_rates)):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 6. Volatility (Middle Right)
    ax6 = plt.subplot(3, 3, 6)
    bars6 = ax6.bar(range(len(strategies)), volatilities, color=strategy_colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax6.set_title('Volatility (%)', fontsize=14, fontweight='bold', pad=20)
    ax6.set_ylabel('Volatility (%)', fontweight='bold')
    ax6.set_xticks(range(len(strategies)))
    ax6.set_xticklabels(strategies, rotation=45, ha='right')
    ax6.grid(axis='y', alpha=0.3)
    
    for i, (bar, value) in enumerate(zip(bars6, volatilities)):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 7. Risk-Return Scatter (Bottom Left)
    ax7 = plt.subplot(3, 3, 7)
    scatter = ax7.scatter(volatilities, returns, c=strategy_colors, s=200, alpha=0.8, edgecolors='black', linewidth=2)
    ax7.set_title('Risk vs Return Profile', fontsize=14, fontweight='bold', pad=20)
    ax7.set_xlabel('Volatility (%)', fontweight='bold')
    ax7.set_ylabel('Total Return (%)', fontweight='bold')
    ax7.grid(alpha=0.3)
    
    # Add strategy labels to scatter plot
    for i, strategy in enumerate(strategies):
        ax7.annotate(strategy.split(' - ')[-1] if ' - ' in strategy else strategy, 
                    (volatilities[i], returns[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold')
    
    # 8. Calmar Ratios (Bottom Center)
    ax8 = plt.subplot(3, 3, 8)
    bars8 = ax8.bar(range(len(strategies)), calmar_ratios, color=strategy_colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax8.set_title('Calmar Ratios', fontsize=14, fontweight='bold', pad=20)
    ax8.set_ylabel('Calmar Ratio', fontweight='bold')
    ax8.set_xticks(range(len(strategies)))
    ax8.set_xticklabels(strategies, rotation=45, ha='right')
    ax8.grid(axis='y', alpha=0.3)
    
    for i, (bar, value) in enumerate(zip(bars8, calmar_ratios)):
        height = bar.get_height()
        ax8.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 9. Legend (Bottom Right)
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    # Create legend
    legend_elements = []
    for strategy, color in colors.items():
        legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.8, edgecolor='black'))
    
    ax9.legend(legend_elements, list(colors.keys()), loc='center', fontsize=11, title='Strategies', title_fontsize=12)
    
    # Add performance summary
    ai_return = data['performance_metrics']['AI_Model']['total_return']
    sma_return = data['performance_metrics']['SMA_Crossover']['total_return']
    improvement = ((ai_return - sma_return) / sma_return) * 100
    
    summary_text = f"""Performance Summary:
    
Portfolio Manager (AI): {ai_return:.2f}%
Best Rule-Based (SMA): {sma_return:.2f}%
AI Advantage: +{improvement:.0f}%

Testing Period: 3 months
Initial Capital: $10,000
Ticker: AAPL"""
    
    ax9.text(0.05, 0.3, summary_text, transform=ax9.transAxes, fontsize=10, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    plt.suptitle('Portfolio Management Strategies - Comprehensive Performance Analysis', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.94)
    
    # Save the plot
    plot_path = "testing_framework/enhanced_performance_dashboard.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Enhanced performance dashboard saved to: {plot_path}")
    
    return fig

def create_cumulative_returns_plot():
    """Create cumulative returns plot for all strategies"""
    
    data = load_results()
    colors = get_strategy_colors()
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Plot AI Model
    if 'raw_data' in data and 'ai_model' in data['raw_data']:
        ai_data = data['raw_data']['ai_model']
        dates = pd.to_datetime(ai_data['dates'])
        cumulative_returns = np.cumsum(ai_data['returns']) * 100  # Convert to percentage
        
        ax.plot(dates, cumulative_returns, 
               color=colors['Portfolio Manager (AI)'], linewidth=4, 
               label='Portfolio Manager (AI)', marker='o', markersize=6, alpha=0.9)
    
    # Plot Rule-Based Strategies
    if 'raw_data' in data and 'rule_based' in data['raw_data']:
        rule_data = data['raw_data']['rule_based']
        
        for strategy_name, strategy_data in rule_data.items():
            renamed_strategy = rename_strategies(strategy_name)
            dates = pd.to_datetime(strategy_data['dates'])
            cumulative_returns = np.cumsum(strategy_data['returns']) * 100
            
            # Different line styles for variety
            line_styles = {
                'Rule Based - SMA Crossover': '-',
                'Rule Based - RSI': '--',
                'Rule Based - MACD': '-.',
                'Rule Based - Bollinger Bands': ':',
                'Rule Based - Combined Technical': '-'
            }
            
            markers = {
                'Rule Based - SMA Crossover': 's',
                'Rule Based - RSI': '^',
                'Rule Based - MACD': 'D',
                'Rule Based - Bollinger Bands': 'v',
                'Rule Based - Combined Technical': 'p'
            }
            
            ax.plot(dates, cumulative_returns, 
                   color=colors[renamed_strategy], 
                   linewidth=3, 
                   label=renamed_strategy,
                   linestyle=line_styles.get(renamed_strategy, '-'),
                   marker=markers.get(renamed_strategy, 'o'), 
                   markersize=4, 
                   alpha=0.8)
    
    # Formatting
    ax.set_title('Cumulative Returns Over Time - All Strategies Comparison', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cumulative Return (%)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax.grid(alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Format x-axis
    ax.tick_params(axis='x', rotation=45)
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    
    # Add performance annotations
    final_ai_return = data['performance_metrics']['AI_Model']['total_return']
    final_sma_return = data['performance_metrics']['SMA_Crossover']['total_return']
    
    ax.text(0.02, 0.98, 
           f'Final Returns:\nPortfolio Manager (AI): +{final_ai_return:.2f}%\nBest Rule-Based (SMA): +{final_sma_return:.2f}%\nAI Advantage: +{((final_ai_return-final_sma_return)/final_sma_return)*100:.0f}%', 
           transform=ax.transAxes, fontsize=12, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, edgecolor='black'))
    
    plt.tight_layout()
    
    # Save the plot
    plot_path = "testing_framework/enhanced_cumulative_returns.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Enhanced cumulative returns plot saved to: {plot_path}")
    
    return fig

if __name__ == "__main__":
    print("Creating enhanced visualizations...")
    
    try:
        # Create performance dashboard
        create_performance_dashboard()
        
        # Create cumulative returns plot
        create_cumulative_returns_plot()
        
        print("\nEnhanced visualizations created successfully!")
        print("Files created:")
        print("- testing_framework/enhanced_performance_dashboard.png")
        print("- testing_framework/enhanced_cumulative_returns.png")
        
    except Exception as e:
        print(f"Error creating visualizations: {str(e)}")
        import traceback
        traceback.print_exc()
