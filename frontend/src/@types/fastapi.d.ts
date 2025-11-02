declare module '@/lib/fastapi' {
  interface AgentAPI {
    shortlistCompanies: (criteria: any) => Promise<any>;
    getStockData: (symbols: string[]) => Promise<any>;
    runSentimentAnalysis: (symbols: string[]) => Promise<any>;
    runTechnicalAnalysis: (symbols: string[]) => Promise<any>;
    runPredictionAnalysis: (symbols: string[]) => Promise<any>;
    getPortfolioRecommendation: (criteria: any) => Promise<any>;
    runCompleteAnalysis: (criteria: any) => Promise<any>;
  }

  export const agentAPI: AgentAPI;
  export default agentAPI;
}
