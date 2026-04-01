# Multi-Agent Investment Intelligence System

An AI-powered investment analysis platform that uses a collaborative multi-agent architecture to analyze markets, evaluate companies, and generate personalized investment recommendations.

---

## Problem Statement

Retail investors face significant challenges when making investment decisions due to:

- Information overload from news, financial reports, and social media  
- Difficulty combining technical analysis, sentiment analysis, and predictions  
- Lack of personalized guidance based on risk appetite and financial goals  

Most traditional tools analyze these factors in isolation, forcing investors to manually interpret and connect insights. This project addresses this gap by using multiple specialized AI agents that work together, similar to how real-world financial firms operate.

---

## Key Features

- Multi-agent investment analysis pipeline  
- Six specialized AI agents with clearly defined responsibilities  
- End-to-end workflow from stock discovery to portfolio allocation  
- Personalized recommendations based on user preferences 
- Real-time market data and news analysis  
- Explainable and modular agent outputs  

---

## Multi-Agent Architecture

The system is designed around six independent yet cooperative AI agents. Each agent focuses on a specific financial analysis task and contributes to the final investment decision.

---

## AI Agents

### 1. Company Shortlisting Agent

Purpose: Identify investable companies

- Filters stocks based on sector, market capitalization, fundamentals, and trends  
- Aligns shortlisted companies with user investment goals and time horizon  
- Reduces the investment universe to high-potential candidates  

This agent acts as the entry point of the investment workflow.

---

### 2. Data Ingestion Agent

Purpose: Collect and structure data

- Gathers real-time market prices and historical financial data  
- Ingests relevant financial news and updates  
- Cleans and structures raw data for downstream agents  

This agent ensures that all analysis is based on reliable and up-to-date information.

---

### 3. Sentiment Analysis Agent

Purpose: Capture market psychology

- Analyzes sentiment from news articles and social media sources  
- Detects bullish, bearish, or neutral signals  
- Identifies hype-driven or fear-driven market behavior  

This agent introduces the human emotion aspect into investment analysis.

---

### 4. Technical Analysis Agent

Purpose: Analyze price action and trends

- Applies technical indicators such as moving averages, RSI, MACD, and volume  
- Identifies support and resistance levels  

This agent provides short-term and medium-term market insights.

---

### 5. Prediction Agent

Purpose: Forecast future price movement

- Uses machine learning models on historical and technical data  
- Estimates potential future price ranges and trend direction  
- Supports scenario-based and probabilistic forecasting  

This agent adds a forward-looking perspective to the system.

---

### 6. Portfolio Manager Agent

Purpose: Generate final investment recommendations

- Aggregates outputs from all other agents  
- Considers user risk tolerance and investment preferences  
- Recommends portfolio allocation and asset distribution  

This agent acts as a virtual investment advisor.

---

## Workflow

1. User defines investment preferences and risk appetite  
2. Company Shortlisting Agent selects suitable stocks  
3. Data Ingestion Agent gathers market and news data  
4. Sentiment, Technical, and Prediction Agents analyze the data independently  
5. Portfolio Manager Agent synthesizes all insights  
6. Final investment recommendations are generated  

---

## Use Cases

- Individual investors seeking data-driven decisions  
- Finance students learning investment analysis workflows  
- FinTech prototypes and robo-advisor systems  
- Research projects on multi-agent decision-making  

---

## Future Enhancements

- Real-time portfolio tracking and performance analytics  
- Advanced data visualization and interactive dashboards  
- Integration with brokerage and trading APIs  
- Risk stress testing and scenario simulation  
- Mobile application support  
- Social and collaborative investing features  

---

## Conclusion

This project demonstrates how multi-agent AI systems can replicate real-world financial decision-making by breaking complex investment analysis into cooperative, specialized agents. By combining market data ingestion, sentiment analysis, technical indicators, machine learning predictions, and portfolio logic, the system delivers holistic, explainable, and personalized investment insights beyond traditional single-model approaches.
