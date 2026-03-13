/**
 * Constants for AG Grid Stock Screener.
 * Display names map to snake_case API fields.
 */

// Columns pinned on the left of every tab (shared context)
export const PINNED_COLUMNS = ["Code", "Name", "Ticker"] as const;

// Tab definitions: tab label -> list of tab-specific columns (appended after PINNED_COLUMNS)
export const TAB_COLUMNS: Record<string, readonly string[]> = {
  Overview: [
    "Price",
    "Market Cap",
    "P/E Ratio",
    "Dividend Yield",
    "ROE",
    "EPS",
    "Return_YTD",
    "Return_1M",
    "Exchange",
    "Sub-Industry",
  ],
  Performance: [
    "Return_1M",
    "Return_3M",
    "Return_6M",
    "Return_1Y",
    "Return_3Y",
    "Return_5Y",
    "Return_10Y",
    "Return_YTD",
    "Volatility_1M",
    "Volatility_3M",
    "Volatility_6M",
    "Volatility_1Y",
    "Volatility_3Y",
    "Volatility_5Y",
    "Volatility_10Y",
    "Volatility_YTD",
    "Sharpe_1M",
    "Sharpe_3M",
    "Sharpe_1Y",
    "Sharpe_3Y",
    "Sharpe_5Y",
    "Sharpe_10Y",
  ],
  Valuation: [
    "P/E Ratio",
    "P/B Ratio",
    "Market Cap",
    "Price",
    "EPS",
    "Price Return",
    "Total Return",
  ],
  Dividends: [
    "Dividend Yield",
    "Total Return",
    "Price Return",
    "Turnover",
  ],
  "Risk Metrics": [
    "Sortino_10Y",
    "Max Drawdown_1M",
    "Max Drawdown_3M",
    "Max Drawdown_1Y",
    "Max Drawdown_3Y",
    "Max Drawdown_5Y",
    "Max Drawdown_10Y",
    "VaR_1M",
    "VaR_3M",
    "VaR_1Y",
    "VaR_3Y",
    "VaR_5Y",
    "VaR_10Y",
    "Skewness_1Y",
    "Kurtosis_1Y",
    "Sortino_1M",
    "Sortino_3M",
    "Sortino_1Y",
    "Sortino_3Y",
    "Sortino_5Y",
  ],
  Identifiers: [
    "Code",
    "RIC",
    "ISIN",
    "SEDOL",
    "FIGI",
    "Datastream Code",
  ],
};

// Map display names to snake_case API field names
export const DISPLAY_TO_FIELD: Record<string, string> = {
  // Fundamentals
  "Price": "price",
  "Market Cap": "market_cap",
  "P/E Ratio": "pe_ratio",
  "P/B Ratio": "pb_ratio",
  "Dividend Yield": "dividend_yield",
  "ROE": "roe",
  "EPS": "eps",
  "Turnover": "turnover",
  "Price Return": "price_return",
  "Total Return": "total_return",
  "Unadj. Price": "unadjusted_price",
  // Categorical
  "Exchange": "exchange",
  "Sub-Industry": "sub_industry",
  "Country": "country",
  "Industry": "industry",
  "Currency": "currency",
  // Identifiers
  "Code": "code",
  "Name": "name",
  "Ticker": "ticker",
  "RIC": "ric",
  "ISIN": "isin",
  "SEDOL": "sedol",
  "FIGI": "figi",
  "Datastream Code": "datastream_code",
  "Barra ID": "barra_id",
  "Barra Root ID": "barra_root_id",
};

// Add metric_period mappings
function toFieldName(metric: string, period: string): string {
  const m = metric === "Max Drawdown" ? "max_drawdown" : metric === "VaR" ? "var" : metric.toLowerCase();
  const p = period.toLowerCase();
  return `${m}_${p}`;
}

for (const metric of ["Return", "Volatility", "Sharpe", "Sortino", "Skewness", "Kurtosis", "Max Drawdown", "VaR"]) {
  for (const period of ["1M", "3M", "6M", "1Y", "3Y", "5Y", "10Y", "MTD", "QTD", "YTD"]) {
    DISPLAY_TO_FIELD[`${metric}_${period}`] = toFieldName(metric, period);
  }
}

// Columns that use text filter (agTextColumnFilter)
export const TEXT_FILTER_COLUMNS = new Set([
  "ID",
  "Code",
  "Name",
  "Ticker",
  "RIC",
  "ISIN",
  "SEDOL",
  "FIGI",
  "Datastream Code",
  "Barra ID",
  "Barra Root ID",
]);

// Categorical columns - use set filter when Enterprise available (agSetColumnFilter)
export const SET_FILTER_COLUMNS = new Set([
  "Currency",
  "Country",
  "Industry",
  "Sub-Industry",
  "Exchange",
]);

// Number columns get agNumberColumnFilter
export const FUNDAMENTALS_COLUMNS = [
  "Dividend Yield",
  "EPS",
  "Market Cap",
  "P/B Ratio",
  "P/E Ratio",
  "Price",
  "Price Return",
  "ROE",
  "Total Return",
  "Turnover",
  "Unadj. Price",
] as const;

export const METRIC_NAMES_LIST = [
  "Return",
  "Volatility",
  "Sharpe",
  "Skewness",
  "Kurtosis",
  "Sortino",
  "Max Drawdown",
  "VaR",
] as const;

export const PERIODS_LIST = ["1M", "3M", "6M", "1Y", "3Y", "5Y", "10Y", "MTD", "QTD", "YTD"] as const;

function buildMetricColumns(): Set<string> {
  const set = new Set<string>();
  for (const metric of METRIC_NAMES_LIST) {
    for (const period of PERIODS_LIST) {
      set.add(`${metric}_${period}`);
    }
  }
  return set;
}

export const NUMBER_FILTER_COLUMNS = new Set([
  ...FUNDAMENTALS_COLUMNS,
  ...buildMetricColumns(),
]);

// Columns displayed as X.XX% (2 decimal places + % sign)
// Metric columns stored as raw decimals (0.0434 = 4.34%): multiply by 100
function buildPercentDecimalColumns(): Set<string> {
  const set = new Set<string>();
  for (const metric of ["Return", "Volatility", "Max Drawdown", "VaR"] as const) {
    for (const period of PERIODS_LIST) {
      set.add(`${metric}_${period}`);
    }
  }
  return set;
}

export const PERCENT_DECIMAL_COLUMNS = buildPercentDecimalColumns();

// Fundamental columns already stored in % form (4.34 = 4.34%): show 2dp + %
export const PERCENT_DISPLAY_COLUMNS = new Set([
  "Dividend Yield",
  "ROE",
  "Price Return",
  "Total Return",
]);

export const PERCENT_COLUMNS = new Set([
  ...PERCENT_DECIMAL_COLUMNS,
  ...PERCENT_DISPLAY_COLUMNS,
]);

// Large number columns: comma separator, 2dp
export const LARGE_NUMBER_COLUMNS = new Set(["Market Cap", "Turnover"]);

// Ratio columns: 2dp, no % sign
function buildRatioColumns(): Set<string> {
  const set = new Set<string>([
    "P/E Ratio",
    "P/B Ratio",
    "EPS",
    "Price",
    "Unadj. Price",
  ]);
  for (const metric of ["Sharpe", "Sortino", "Skewness", "Kurtosis"] as const) {
    for (const period of PERIODS_LIST) {
      set.add(`${metric}_${period}`);
    }
  }
  return set;
}

export const RATIO_COLUMNS = buildRatioColumns();

// Columns that should have red/green color formatting based on sign
export const COLOR_FORMATTED_COLUMNS = new Set([
  ...PERCENT_COLUMNS,
  ...RATIO_COLUMNS,
  "Price Return",
  "Total Return",
  "EPS",
  "ROE",
  "Dividend Yield",
  ...buildMetricColumns(),
]);

// Flex columns per tab (auto-width)
export const FLEX_COLUMNS = new Set(["Name", "Ticker", "Industry", "Country"]);

// Filter tooltips (optional)
export const FILTER_TOOLTIPS: Record<string, string> = {
  "Country": "Country where the stock is listed.",
  "Industry": "Primary sector classification (e.g. Financials, Technology).",
  "Exchange": "Stock exchange where the security trades.",
  "Currency": "Trading currency of the security.",
  "Sub-Industry": "Sub-sector classification within the primary industry.",
  "Price": "Current adjusted price of the security.",
  "Market Cap": "Total market capitalisation (price x shares outstanding).",
  "P/E Ratio": "Price-to-earnings ratio. Lower may indicate undervaluation.",
  "Div Yield": "Annual dividend as a percentage of the stock price.",
  "ROE": "Return on equity -- net income as a percentage of shareholder equity.",
  "EPS": "Earnings per share -- net income divided by outstanding shares.",
};
