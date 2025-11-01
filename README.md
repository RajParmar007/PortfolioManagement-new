# Multi-Agent Investment System

A comprehensive AI-powered investment analysis platform that combines multiple specialized agents to provide intelligent investment recommendations.

## 🚀 Features

- **Multi-Agent Architecture**: Six specialized AI agents working together
- **Modern Web Interface**: Next.js frontend with TailwindCSS and shadcn/ui
- **Secure Authentication**: Supabase-powered user management
- **Real-time Analysis**: FastAPI backend with live market data integration
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

### Frontend (Next.js)
- **Home Page**: Landing page with feature overview
- **Authentication**: Login/signup with Supabase Auth
- **Dashboard**: Protected route with agent controls and results
- **About Page**: Detailed information about the system

### Backend (FastAPI)
- **RESTful API**: Clean endpoints for all agent operations
- **Agent Integration**: Direct integration with existing Python agents
- **CORS Support**: Configured for frontend communication
- **Error Handling**: Comprehensive error responses

### AI Agents
1. **Company Shortlisting Agent**: Identifies promising investment opportunities
2. **Data Ingestion Agent**: Collects real-time market data and news
3. **Sentiment Analysis Agent**: Analyzes market sentiment from multiple sources
4. **Technical Analysis Agent**: Performs advanced technical analysis
5. **Prediction Agent**: Uses ML models for price forecasting
6. **Portfolio Manager Agent**: Synthesizes all analysis for recommendations

## 🛠️ Technology Stack

### Frontend
- Next.js 14 with App Router
- TypeScript for type safety
- TailwindCSS for styling
- shadcn/ui for components
- Supabase for authentication and database
- Axios for API communication

### Backend
- FastAPI for high-performance API
- Pydantic for data validation
- Uvicorn ASGI server
- Integration with existing agent system

### Database
- Supabase PostgreSQL
- Row Level Security (RLS)
- Real-time subscriptions

## 📋 Agent Flow

1. **User Profile Creation**: Users specify investment preferences and risk tolerance
2. **Company Shortlisting**: AI identifies potential stocks based on user profile and market conditions
3. **Data Ingestion**: Comprehensive data collection from multiple sources
4. **Multi-Agent Analysis**: 
   - Sentiment analysis from news and social media
   - Technical analysis with advanced indicators
   - ML-powered price predictions
5. **Portfolio Recommendations**: Synthesized recommendations tailored to user preferences

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Supabase account

### Setup
1. **Clone and setup frontend**:
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   # Configure your Supabase credentials in .env.local
   npm run dev
   ```

2. **Setup backend**:
   ```bash
   pip install -r fastapi_requirements.txt
   pip install -r requirements.txt
   python start_backend.py
   ```

3. **Configure Supabase**:
   - Create tables using SQL in SETUP.md
   - Configure authentication settings

### Access Points
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📊 Dashboard Features

### AI Agents Tab
- Individual agent controls
- Real-time status monitoring
- Results preview for each agent

### Analysis Results Tab
- Comprehensive analysis results
- Formatted JSON output
- Historical analysis tracking

### Profile Settings Tab
- Risk tolerance configuration
- Investment horizon settings
- Sector preferences

## 🔐 Security Features

- **Authentication**: Secure user authentication with Supabase
- **Route Protection**: Middleware-based route protection
- **Data Privacy**: Row-level security for user data
- **CORS Configuration**: Secure cross-origin requests

## 🎯 Use Cases

- **Individual Investors**: Personal portfolio analysis and recommendations
- **Financial Advisors**: Client portfolio management tools
- **Research**: Market analysis and trend identification
- **Education**: Learning about AI-powered investment strategies

## 📈 Future Enhancements

- Real-time portfolio tracking
- Advanced visualization charts
- Mobile app development
- Integration with brokerage APIs
- Social trading features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For setup help, check SETUP.md or create an issue in the repository.
