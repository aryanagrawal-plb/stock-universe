export interface Stock {
  code: string;
  name: string;
  ticker: string;
  currency?: string;
  country?: string;
  industry?: string;
  sub_industry?: string;
  exchange?: string;

  ric?: string | null;
  isin?: string | null;
  sedol?: string | null;
  figi?: string | null;
  datastream_code?: string | null;
  barra_id?: string | null;
  barra_root_id?: string | null;

  price?: number | null;
  market_cap?: number | null;
  pe_ratio?: number | null;
  pb_ratio?: number | null;
  dividend_yield?: number | null;
  eps?: number | null;
  roe?: number | null;
  turnover?: number | null;
  price_return?: number | null;
  total_return?: number | null;
  unadjusted_price?: number | null;

  return_1m?: number | null;
  return_3m?: number | null;
  return_6m?: number | null;
  return_1y?: number | null;
  return_3y?: number | null;
  return_5y?: number | null;
  return_10y?: number | null;
  return_ytd?: number | null;

  volatility_1m?: number | null;
  volatility_3m?: number | null;
  volatility_6m?: number | null;
  volatility_1y?: number | null;
  volatility_3y?: number | null;
  volatility_5y?: number | null;
  volatility_10y?: number | null;
  volatility_ytd?: number | null;

  sharpe_1m?: number | null;
  sharpe_3m?: number | null;
  sharpe_1y?: number | null;
  sharpe_3y?: number | null;
  sharpe_5y?: number | null;
  sharpe_10y?: number | null;

  sortino_1m?: number | null;
  sortino_3m?: number | null;
  sortino_1y?: number | null;
  sortino_3y?: number | null;
  sortino_5y?: number | null;
  sortino_10y?: number | null;

  max_drawdown_1m?: number | null;
  max_drawdown_3m?: number | null;
  max_drawdown_1y?: number | null;
  max_drawdown_3y?: number | null;
  max_drawdown_5y?: number | null;
  max_drawdown_10y?: number | null;

  var_1m?: number | null;
  var_3m?: number | null;
  var_1y?: number | null;
  var_3y?: number | null;
  var_5y?: number | null;
  var_10y?: number | null;

  skewness_1y?: number | null;
  kurtosis_1y?: number | null;
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

export type FilterAction = "set" | "add" | "remove" | "clear" | "watchlist" | "none";
export type FilterStatus = "pending" | "applied" | "dismissed";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  pendingFilters?: UniverseFilters | null;
  action?: FilterAction;
  filterStatus?: FilterStatus;
  alertName?: string | null;
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

export interface Alert {
  id: string;
  name: string;
  filters: UniverseFilters;
  created_at: string;
  status: "active" | "paused";
}
