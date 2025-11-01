# Multi-Agent Investment System Setup Guide

## Overview
This project consists of a Next.js frontend with Supabase authentication and a FastAPI backend that integrates with your existing AI agents.

## Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Supabase account

## Setup Instructions

### 1. Supabase Setup

1. Create a new Supabase project at https://supabase.com
2. Go to Settings > API to get your project URL and anon key
3. In the SQL Editor, run the following to create the required tables:

```sql
-- Create profiles table
CREATE TABLE profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  investor_type TEXT,
  preferred_sectors TEXT[],
  risk_tolerance TEXT,
  investment_horizon TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (id)
);

-- Create investment_analyses table
CREATE TABLE investment_analyses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users ON DELETE CASCADE,
  analysis_type TEXT NOT NULL,
  ticker_symbols TEXT[] NOT NULL,
  results JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE investment_analyses ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can view own analyses" ON investment_analyses FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own analyses" ON investment_analyses FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### 2. Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create and configure environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your Supabase credentials:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
NEXTAUTH_SECRET=your_random_secret_string
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

### 3. Backend Setup

1. Install FastAPI dependencies:
```bash
pip install -r fastapi_requirements.txt
```

2. Make sure your existing agent dependencies are installed:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
python fastapi_backend.py
```

The API will be available at http://localhost:8000
API documentation will be at http://localhost:8000/docs

## Usage

### Authentication
1. Visit http://localhost:3000
2. Click "Sign Up" to create an account
3. Verify your email (check Supabase Auth settings)
4. Sign in and access the dashboard

### Dashboard Features
1. **AI Agents Tab**: Run individual agents or complete analysis
2. **Analysis Results Tab**: View comprehensive results from all agents
3. **Profile Settings Tab**: Configure your investor preferences

### API Endpoints
- `GET /`: API status
- `POST /agents/shortlist`: Company shortlisting
- `GET /agents/stock-data/{ticker}`: Stock data retrieval
- `GET /agents/news/{ticker}`: News data retrieval
- `GET /agents/reddit/{ticker}`: Reddit sentiment data
- `POST /agents/sentiment-analysis`: Sentiment analysis
- `POST /agents/technical-analysis`: Technical analysis
- `GET /agents/prediction/{ticker}`: Price prediction
- `POST /agents/portfolio-recommendation`: Portfolio recommendations
- `POST /agents/complete-analysis`: Run complete workflow

## Architecture

```
Frontend (Next.js)
├── Authentication (Supabase Auth)
├── Database (Supabase PostgreSQL)
├── UI Components (shadcn/ui + TailwindCSS)
└── API Integration (Axios)

Backend (FastAPI)
├── Agent Integration
├── CORS Middleware
├── Pydantic Models
└── Error Handling

AI Agents (Your existing system)
├── Company Shortlisting Agent
├── Data Ingestion Agent
├── Sentiment Analysis Agent
├── Technical Analysis Agent
├── Prediction Agent
└── Portfolio Manager Agent
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure FastAPI backend is running on port 8000
2. **Authentication Issues**: Check Supabase configuration and environment variables
3. **Agent Errors**: Ensure all Python dependencies are installed
4. **Database Errors**: Verify Supabase tables are created correctly

### Development Tips

1. Use browser dev tools to debug frontend issues
2. Check FastAPI logs for backend errors
3. Monitor Supabase logs for database issues
4. Test individual agents before running complete analysis

## Next Steps

1. Configure your investor profile in the dashboard
2. Test individual agents with different sectors
3. Run complete analysis workflows
4. Customize the UI based on your preferences
5. Add more sophisticated error handling and logging
