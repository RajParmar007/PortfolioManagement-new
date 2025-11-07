// FastAPI client configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface InvestorProfile {
  risk_tolerance: string;
  investment_horizon: string;
  preferred_sectors: string[];
}

/**
 * Function 1: Shortlist companies based on sector and number
 */
async function shortlistCompanies(sector: string, top_n: number): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/agents/shortlist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sector, top_n })
  });
  if (!response.ok) {
    throw new Error(`Shortlisting failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Function 2: Analyze selected companies and get final recommendation
 */
async function analyzeCompanies(tickers: string[], investorProfile: InvestorProfile): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/agents/analyze-companies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      tickers, 
      investor_profile: investorProfile 
    })
  });
  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }
  return response.json();
}

export const agentAPI = {
  shortlistCompanies,
  analyzeCompanies
};

export default agentAPI;
