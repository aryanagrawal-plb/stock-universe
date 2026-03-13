export interface Stock {
  code: string;
  name: string;
  ticker: string;
  currency: string;
  country: string;
  industry: string;
  sub_industry: string;
  exchange: string;

  ric: string | null;
  isin: string | null;

  price: number | null;
  market_cap: number | null;
  pe_ratio: number | null;
  pb_ratio: number | null;
  dividend_yield: number | null;
  eps: number | null;
  roe: number | null;
  turnover: number | null;

  return_1m: number | null;
  return_3m: number | null;
  return_6m: number | null;
  return_1y: number | null;
  return_ytd: number | null;

  volatility_1y: number | null;
  sharpe_1y: number | null;
  max_drawdown_1y: number | null;
}

export interface StockFilters {
  sector: string;
  minPrice: number | null;
  maxPrice: number | null;
  search: string;
}

export interface FilterChip {
  category: string;
  value: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
