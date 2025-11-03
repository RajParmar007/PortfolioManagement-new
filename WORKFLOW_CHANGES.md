# Portfolio Management System - Workflow Changes

## Overview
The application has been restructured to provide a two-phase workflow where users have full control over company selection and analysis parameters.

## Changes Made

### 1. Backend (fastapi_backend.py)

#### New Endpoint Structure:
- **`POST /agents/shortlist`** - Phase 1: Shortlist companies
  - Input: `sector` (string), `top_n` (number)
  - Output: List of companies matching criteria
  - Uses: `shortlist_sector()` agent

- **`POST /agents/analyze-companies`** - Phase 2: Analyze selected companies
  - Input: `tickers` (list), `investor_profile` (object)
  - Output: Complete analysis with recommendation
  - Maintains exact LangChain flow from main.py:
    1. Data Ingestion (stock data, news, reddit)
    2. Technical Analysis
    3. Sentiment Analysis
    4. Prediction Analysis
    5. Portfolio Recommendation

### 2. Frontend API Client (frontend/src/lib/fastapi.ts)

Simplified to two main functions:
```typescript
agentAPI.shortlistCompanies(sector: string, top_n: number)
agentAPI.analyzeCompanies(tickers: string[], investorProfile: InvestorProfile)
```

### 3. UI (frontend/src/app/dashboard/page.tsx)

#### Phase 1: Company Shortlisting
- User selects:
  - Sector (Technology, Finance, Healthcare, etc.)
  - Number of companies to shortlist (5-50)
- Click "Shortlist Companies" button
- Results displayed as selectable cards
- All companies auto-selected by default

#### Phase 2: Analysis
- User can:
  - Toggle company selection (click cards)
  - Set risk tolerance (low/medium/high)
  - Set investment timeframe (years)
- Click "Run Analysis" button
- Complete analysis runs on selected companies only
- Results displayed with:
  - Portfolio Recommendation (highlighted)
  - Technical Analysis per company
  - Sentiment Analysis per company
  - Price Predictions per company

## Key Features

### User Control
- Choose sector and number of companies
- Select specific companies from shortlist
- Configure analysis parameters independently

### LangChain Flow Preservation
The exact agent chain from `main.py` is maintained:
```
Data Ingestion → Technical Analysis → Sentiment Analysis → 
Prediction → Portfolio Recommendation
```

No agent functionality has been changed - only the workflow orchestration.

### Clean UI
- Two-column layout
- Left: Configuration panels (Phase 1 & 2)
- Right: Results display
- Visual feedback during processing
- Clear phase separation

## How to Use

1. **Start Backend:**
   ```bash
   cd c:\Users\Anuj\Desktop\PortfolioManagement-new
   python fastapi_backend.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Workflow:**
   - Select sector and company count
   - Click "Shortlist Companies"
   - Review and select companies
   - Configure risk tolerance and timeframe
   - Click "Run Analysis"
   - View comprehensive results

## Technical Notes

- All agent functions remain unchanged
- Backend maintains compatibility with existing agents
- Frontend uses TypeScript for type safety
- API responses include all analysis data
- Error handling at each phase
