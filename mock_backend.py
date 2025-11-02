from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import random
import uvicorn

app = FastAPI(title="Mock Investment System API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data generation functions
def generate_mock_companies(sector: str, n: int = 10) -> List[Dict[str, Any]]:
    companies = []
    for i in range(1, n + 1):
        companies.append({
            "ticker": f"{sector[:3].upper()}{i:03d}",
            "name": f"{sector.capitalize()} Company {i}",
            "sector": sector,
            "price": round(random.uniform(50, 500), 2),
            "change": round(random.uniform(-5, 5), 2),
            "market_cap": f"${random.randint(1, 1000)}B",
            "volume": f"{random.randint(1, 100)}M"
        })
    return companies

def generate_mock_analysis() -> Dict[str, Any]:
    return {
        "sentiment": {
            "score": round(random.uniform(-1, 1), 2),
            "label": random.choice(["Positive", "Neutral", "Negative"]),
            "confidence": round(random.uniform(0.7, 0.99), 2)
        },
        "technical": {
            "rsi": round(random.uniform(20, 80), 2),
            "macd": round(random.uniform(-2, 2), 2),
            "sma50": round(random.uniform(100, 200), 2),
            "sma200": round(random.uniform(90, 210), 2)
        },
        "prediction": {
            "price_target": round(random.uniform(100, 500), 2),
            "confidence": round(random.uniform(0.5, 0.95), 2),
            "recommendation": random.choice(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])
        }
    }

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Mock Investment System API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Company Shortlisting
class ShortlistRequest(BaseModel):
    sector: str
    limit: int = 15

@app.post("/api/companies/shortlist")
async def shortlist_companies(request: ShortlistRequest):
    return {
        "status": "success",
        "companies": generate_mock_companies(request.sector, min(request.limit, 50))
    }

# Stock Data
@app.post("/api/stocks/data")
async def get_stock_data(symbols: List[str]):
    data = {}
    for symbol in symbols:
        data[symbol] = {
            "price": round(random.uniform(50, 500), 2),
            "change": round(random.uniform(-5, 5), 2),
            "volume": random.randint(1000000, 10000000),
            "market_cap": random.randint(1000000000, 1000000000000)
        }
    return data

# Analysis Endpoints
@app.post("/api/analysis/sentiment")
async def run_sentiment_analysis(symbols: List[str]):
    return {symbol: generate_mock_analysis()["sentiment"] for symbol in symbols}

@app.post("/api/analysis/technical")
async def run_technical_analysis(symbols: List[str]):
    return {symbol: generate_mock_analysis()["technical"] for symbol in symbols}

@app.post("/api/analysis/prediction")
async def run_prediction_analysis(symbols: List[str]):
    return {symbol: generate_mock_analysis()["prediction"] for symbol in symbols}

# Portfolio Recommendation
class PortfolioRequest(BaseModel):
    risk_tolerance: str
    investment_horizon: str
    preferred_sectors: List[str]
    initial_investment: float
    investment_goal: float
    timeframe_years: int

@app.post("/api/portfolio/recommendation")
async def get_portfolio_recommendation(request: PortfolioRequest):
    sectors = request.preferred_sectors or ["Technology", "Finance", "Healthcare", "Energy"]
    companies = []
    for sector in sectors:
        companies.extend(generate_mock_companies(sector, 3))
    
    # Select a subset of companies
    selected_companies = random.sample(companies, min(10, len(companies)))
    
    # Generate portfolio allocation
    total_weight = 0
    portfolio = []
    for company in selected_companies:
        if total_weight >= 0.95:  # Ensure we don't go over 100%
            break
        weight = min(round(random.uniform(0.05, 0.3), 2), 1 - total_weight)
        portfolio.append({
            **company,
            "allocation": weight,
            "shares": int((request.initial_investment * weight) / company["price"])
        })
        total_weight += weight
    
    return {
        "status": "success",
        "portfolio": portfolio,
        "expected_return": round(random.uniform(0.05, 0.15), 2),
        "risk_level": request.risk_tolerance,
        "time_horizon": f"{request.timeframe_years} years"
    }

# Complete Analysis
class CompleteAnalysisRequest(BaseModel):
    sector: str
    risk_tolerance: str
    investment_horizon: str
    preferred_sectors: List[str]
    initial_investment: float
    investment_goal: float
    timeframe_years: int

@app.post("/api/analysis/complete")
async def run_complete_analysis(request: CompleteAnalysisRequest):
    # Get companies
    companies = generate_mock_companies(request.sector, 10)
    symbols = [c["ticker"] for c in companies]
    
    # Get analyses
    sentiment = await run_sentiment_analysis(symbols)
    technical = await run_technical_analysis(symbols)
    prediction = await run_prediction_analysis(symbols)
    
    # Get portfolio recommendation
    portfolio_request = PortfolioRequest(
        risk_tolerance=request.risk_tolerance,
        investment_horizon=request.investment_horizon,
        preferred_sectors=request.preferred_sectors,
        initial_investment=request.initial_investment,
        investment_goal=request.investment_goal,
        timeframe_years=request.timeframe_years
    )
    portfolio = await get_portfolio_recommendation(portfolio_request)
    
    return {
        "status": "success",
        "companies": companies,
        "analyses": {
            "sentiment": sentiment,
            "technical": technical,
            "prediction": prediction
        },
        "portfolio": portfolio
    }

if __name__ == "__main__":
    uvicorn.run("mock_backend:app", host="0.0.0.0", port=8000, reload=True)
