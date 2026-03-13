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

export type FilterAction = "add" | "remove" | "clear" | "none";
export type FilterStatus = "pending" | "applied" | "dismissed";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  pendingFilters?: UniverseFilters | null;
  action?: FilterAction;
  filterStatus?: FilterStatus;
}

export interface NumericRange {
  min: number | null;
  max: number | null;
}

export interface UniverseFilters {
  countries?: string[] | null;
  industries?: string[] | null;
  sub_industries?: string[] | null;
  currencies?: string[] | null;
  exchanges?: string[] | null;

  search?: string | null;

  price?: NumericRange | null;
  market_cap?: NumericRange | null;
  pe_ratio?: NumericRange | null;
  pb_ratio?: NumericRange | null;
  dividend_yield?: NumericRange | null;
  earnings_per_share?: NumericRange | null;
  return_on_equity?: NumericRange | null;

  return_1m?: NumericRange | null;
  return_3m?: NumericRange | null;
  return_6m?: NumericRange | null;
  return_1y?: NumericRange | null;
  return_3y?: NumericRange | null;
  return_5y?: NumericRange | null;
  return_ytd?: NumericRange | null;

  volatility_1y?: NumericRange | null;
  sharpe_1y?: NumericRange | null;
  sortino_1y?: NumericRange | null;
  max_drawdown_1y?: NumericRange | null;
}
