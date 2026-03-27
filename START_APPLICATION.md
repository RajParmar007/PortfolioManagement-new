# Start Application Guide

## ✅ Fixed Issues
- Removed old TypeScript declaration files that were causing errors
- Backend and frontend are now properly connected
- **No agents have been changed** - all agent functionality remains intact

## 🚀 How to Start

### Step 1: Start Backend (Terminal 1)
```bash
cd c:\Users\Anuj\Desktop\PortfolioManagement-new
python fastapi_backend.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend (Terminal 2)
```bash
cd c:\Users\Anuj\Desktop\PortfolioManagement-new\frontend
npm run dev
```

**Expected output:**
```
- Local:        http://localhost:3000
```

### Step 3: Open Browser
Navigate to: `http://localhost:3000/dashboard`

## 📋 How to Use

### Phase 1: Shortlist Companies
1. Select a **Sector** (Technology, Finance, Healthcare, etc.)
2. Choose **Number of Companies** (5-50)
3. Click **"Shortlist Companies"**
4. Wait for results to load
5. All companies are auto-selected (click to toggle)

### Phase 2: Analyze Selected Companies
1. Configure **Risk Tolerance** (Low/Medium/High)
2. Set **Investment Timeframe** (years)
3. Review selected companies count
4. Click **"Run Analysis"**
5. Wait for complete analysis (this runs all agents)

## 🔄 Agent Flow (Unchanged)

The exact LangChain flow from `main.py` is preserved:

```
User Selects Companies
        ↓
Data Ingestion Agent (stock data, news, reddit)
        ↓
Technical Analysis Agent
        ↓
Sentiment Analysis Agent
        ↓
Prediction Agent
        ↓
Portfolio Manager Agent
        ↓
Final Recommendation
```

## 🎯 API Endpoints

### Backend (http://localhost:8000)
- `POST /agents/shortlist` - Shortlist companies by sector
- `POST /agents/analyze-companies` - Run complete analysis chain

### Frontend (http://localhost:3000)
- `/dashboard` - Main application interface

## 🐛 Troubleshooting

### TypeScript Errors in IDE
If you still see red squiggles:
1. Press `Ctrl+Shift+P`
2. Type: "TypeScript: Restart TS Server"
3. Press Enter

### Backend Not Starting
- Ensure all Python dependencies are installed
- Check that agents folder exists with all agent files

### Frontend Not Starting
```bash
cd frontend
npm install
npm run dev
```

## ✨ Features

✅ Two-phase workflow with user control
✅ Sector-based company shortlisting
✅ Flexible company selection
✅ Risk tolerance configuration
✅ Complete multi-agent analysis
✅ Comprehensive results display
✅ All agents unchanged and functional
