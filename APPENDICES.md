# Appendices

## Appendix A: System Flow

### 1. System Architecture
```
[User] 
  ↓ 
[Next.js Frontend] 
  ↓ (API Calls)
[FastAPI Backend] 
  ↓ (Processes via)
[AI Agents] 
  ↓ (Analyzes/Fetches)
[Market Data & External APIs]
  ↓ (Returns)
[Formatted Results to User]
```

### 2. Data Flow
1. User selects sector and companies in the frontend
2. Frontend sends selection to backend
3. Backend routes to appropriate analysis agents
4. Agents fetch and process market data
5. Analysis results are aggregated and formatted
6. Results are returned to frontend for display

### 3. User Interaction Flow
1. User lands on dashboard
2. Selects sector from dropdown
3. Views list of companies in sector
4. Selects companies for analysis
5. Clicks "Run Analysis"
6. Views analysis results
7. Makes investment decisions based on insights

## Appendix B: Component Structure

### 1. Frontend Components
- **Dashboard**
  - Main container component
  - Manages application state
  - Coordinates between child components

- **SectorSelector**
  - Dropdown for sector selection
  - Fetches companies based on selection

- **CompanyList**
  - Displays list of companies
  - Handles company selection
  - Shows selection status

- **AnalysisPanel**
  - Displays analysis results
  - Formats and renders recommendations
  - Shows loading/error states

### 2. Backend Services
- **FastAPI Application**
  - REST API endpoints
  - Request validation
  - Response formatting

- **AI Agents**
  - Company Shortlisting
  - Technical Analysis
  - Sentiment Analysis
  - Price Prediction

- **Data Services**
  - Market data fetching
  - Data preprocessing
  - Result aggregation

## Appendix C: Data Processing

### 1. Analysis Pipeline
1. Data Collection
   - Fetch market data
   - Retrieve news/sentiment data

2. Data Processing
   - Clean and normalize data
   - Calculate technical indicators
   - Process sentiment data

3. Analysis
   - Run technical analysis
   - Perform sentiment analysis
   - Generate predictions

4. Aggregation
   - Combine results
   - Generate recommendations
   - Format output

### 2. Error Handling
- **Input Validation**
  - Verify request parameters
  - Check data types and ranges

- **API Error Handling**
  - Timeout handling
  - Rate limiting
  - Fallback mechanisms

- **Data Processing Errors**
  - Missing data handling
  - Data quality checks
  - Fallback to alternative data sources

## Appendix D: Configuration

### 1. Environment Variables
- `API_BASE_URL`: Backend API URL
- `MAX_COMPANIES`: Maximum selectable companies
- `ANALYSIS_TIMEOUT`: Analysis request timeout
- `CACHE_TTL`: Data cache duration

### 2. Dependencies
- Frontend: Next.js, React, TypeScript, TailwindCSS
- Backend: FastAPI, Python 3.9+
- AI/ML: scikit-learn, pandas, numpy, transformers
- Data: yfinance, pandas-datareader

---
*This documentation provides a text-based overview of the system architecture and components.*
