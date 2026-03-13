export interface Stock {
  ticker: string;
  name: string;
  sector: string;
  price: number;
  market_cap: number;
  pe_ratio: number | null;
  dividend_yield: number | null;
  volume: number;
}

export interface StockFilters {
  sector: string;
  minPrice: number | null;
  maxPrice: number | null;
  search: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
