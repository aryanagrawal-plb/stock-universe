import { ref, computed, type Ref } from "vue";
import type {
  Stock,
  FilterChip,
  UniverseFilters,
  NumericRange,
} from "../types/stock";

function formatMarketCapValue(value: number): string {
  if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  return `$${value.toFixed(0)}`;
}

function getStockValueForCategory(stock: Stock, category: string): string {
  switch (category) {
    case "Country":
      return stock.country ?? "";
    case "Industry":
      return stock.industry ?? "";
    case "Sub-Industry":
      return stock.sub_industry ?? "";
    case "Exchange":
      return stock.exchange ?? "";
    case "Currency":
      return stock.currency ?? "";
    case "Ticker":
      return stock.code;
    case "Name":
      return stock.name;
    default:
      return "";
  }
}

function passesNumericRange(
  value: number | null | undefined,
  range: NumericRange | null | undefined
): boolean {
  if (!range) return true;
  if (value == null) return false;
  if (range.min != null && value < range.min) return false;
  if (range.max != null && value > range.max) return false;
  return true;
}

const NUMERIC_FILTER_STOCK_MAP: Record<string, keyof Stock> = {
  price: "price",
  market_cap: "market_cap",
  pe_ratio: "pe_ratio",
  pb_ratio: "pb_ratio",
  dividend_yield: "dividend_yield",
  earnings_per_share: "eps",
  return_on_equity: "roe",
  return_1m: "return_1m",
  return_3m: "return_3m",
  return_6m: "return_6m",
  return_1y: "return_1y",
  return_ytd: "return_ytd",
  volatility_1y: "volatility_1y",
  sharpe_1y: "sharpe_1y",
  max_drawdown_1y: "max_drawdown_1y",
};

function passesAiFilters(stock: Stock, ai: UniverseFilters): boolean {
  if (ai.countries?.length && !ai.countries.includes(stock.country ?? ""))
    return false;
  if (ai.industries?.length && !ai.industries.includes(stock.industry ?? ""))
    return false;
  if (
    ai.sub_industries?.length &&
    !ai.sub_industries.includes(stock.sub_industry ?? "")
  )
    return false;
  if (ai.currencies?.length && !ai.currencies.includes(stock.currency ?? ""))
    return false;
  if (ai.exchanges?.length && !ai.exchanges.includes(stock.exchange ?? ""))
    return false;

  if (ai.search) {
    const q = ai.search.toLowerCase();
    if (
      !stock.code.toLowerCase().includes(q) &&
      !stock.name.toLowerCase().includes(q)
    )
      return false;
  }

  for (const [filterKey, stockKey] of Object.entries(NUMERIC_FILTER_STOCK_MAP)) {
    const range = ai[filterKey as keyof UniverseFilters] as
      | NumericRange
      | null
      | undefined;
    if (range && (range.min != null || range.max != null)) {
      if (!passesNumericRange(stock[stockKey] as number | null, range))
        return false;
    }
  }

  return true;
}

/** Convert the categorical / text fields of UniverseFilters into FilterChips for display. */
export function aiFiltersToChips(ai: UniverseFilters): FilterChip[] {
  const chips: FilterChip[] = [];
  ai.countries?.forEach((v) => chips.push({ category: "Country", value: v }));
  ai.industries?.forEach((v) =>
    chips.push({ category: "Industry", value: v })
  );
  ai.sub_industries?.forEach((v) =>
    chips.push({ category: "Sub-Industry", value: v })
  );
  ai.currencies?.forEach((v) =>
    chips.push({ category: "Currency", value: v })
  );
  ai.exchanges?.forEach((v) =>
    chips.push({ category: "Exchange", value: v })
  );
  if (ai.search) chips.push({ category: "Search", value: ai.search });

  const RANGE_LABELS: Record<string, string> = {
    price: "Price",
    market_cap: "Market Cap",
    pe_ratio: "P/E",
    pb_ratio: "P/B",
    dividend_yield: "Div Yield",
    earnings_per_share: "EPS",
    return_on_equity: "ROE",
    return_1m: "1M Ret",
    return_3m: "3M Ret",
    return_6m: "6M Ret",
    return_1y: "1Y Ret",
    return_ytd: "YTD Ret",
    volatility_1y: "1Y Vol",
    sharpe_1y: "Sharpe",
    max_drawdown_1y: "Max DD",
  };

  for (const [key, label] of Object.entries(RANGE_LABELS)) {
    const range = ai[key as keyof UniverseFilters] as
      | NumericRange
      | null
      | undefined;
    if (!range) continue;
    if (range.min != null && range.max != null) {
      chips.push({ category: label, value: `${range.min}–${range.max}` });
    } else if (range.min != null) {
      chips.push({ category: label, value: `≥ ${range.min}` });
    } else if (range.max != null) {
      chips.push({ category: label, value: `≤ ${range.max}` });
    }
  }

  return chips;
}

const FILTERS_STORAGE_KEY = "stock-universe-filters";

const CATEGORICAL_KEYS: (keyof UniverseFilters)[] = [
  "countries", "industries", "sub_industries", "currencies", "exchanges",
];

const NUMERIC_KEYS: (keyof UniverseFilters)[] = [
  "price", "market_cap", "pe_ratio", "pb_ratio", "dividend_yield",
  "earnings_per_share", "return_on_equity",
  "return_1m", "return_3m", "return_6m", "return_1y", "return_3y",
  "return_5y", "return_ytd",
  "volatility_1y", "sharpe_1y", "sortino_1y", "max_drawdown_1y",
];

function mergeFilters(
  current: UniverseFilters | null,
  incoming: UniverseFilters,
): UniverseFilters {
  if (!current) return { ...incoming };
  const merged: Record<string, unknown> = { ...current };

  for (const key of CATEGORICAL_KEYS) {
    const inc = incoming[key] as string[] | null | undefined;
    if (inc?.length) {
      const cur = (current[key] as string[] | null) ?? [];
      merged[key] = [...new Set([...cur, ...inc])];
    }
  }

  if (incoming.search != null) merged.search = incoming.search;

  for (const key of NUMERIC_KEYS) {
    const inc = incoming[key] as NumericRange | null | undefined;
    if (inc) merged[key] = inc;
  }

  return merged as UniverseFilters;
}

function subtractFilters(
  current: UniverseFilters,
  toRemove: UniverseFilters,
): UniverseFilters {
  const result: Record<string, unknown> = { ...current };

  for (const key of CATEGORICAL_KEYS) {
    const rem = toRemove[key] as string[] | null | undefined;
    if (rem?.length) {
      const cur = (current[key] as string[] | null) ?? [];
      const filtered = cur.filter((v) => !rem.includes(v));
      result[key] = filtered.length > 0 ? filtered : null;
    }
  }

  if (toRemove.search != null) result.search = null;

  for (const key of NUMERIC_KEYS) {
    if (toRemove[key] != null) result[key] = null;
  }

  return result as UniverseFilters;
}

function hasActiveFilters(f: UniverseFilters): boolean {
  for (const key of CATEGORICAL_KEYS) {
    const v = f[key] as string[] | null | undefined;
    if (v?.length) return true;
  }
  if (f.search) return true;
  for (const key of NUMERIC_KEYS) {
    if (f[key] != null) return true;
  }
  return false;
}

export function useStocks() {
  const stocks = ref<Stock[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const filterChips = ref<FilterChip[]>([]);
  const aiFilters = ref<UniverseFilters | null>(null);

  const filteredStocks = computed<Stock[]>(() => {
    let result = stocks.value;

    // Manual chip filters: OR within same category, AND across categories
    if (filterChips.value.length > 0) {
      const chipsByCategory = new Map<string, string[]>();
      for (const chip of filterChips.value) {
        const values = chipsByCategory.get(chip.category) ?? [];
        values.push(chip.value);
        chipsByCategory.set(chip.category, values);
      }

      result = result.filter((stock) => {
        for (const [category, values] of chipsByCategory) {
          const stockValue = getStockValueForCategory(stock, category);
          if (!values.includes(stockValue)) return false;
        }
        return true;
      });
    }

    // AI-driven filters (categorical + numeric ranges)
    if (aiFilters.value) {
      result = result.filter((stock) =>
        passesAiFilters(stock, aiFilters.value!)
      );
    }

    return result;
  });

  async function fetchStocks(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await fetch("/api/stocks");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      stocks.value = Array.isArray(data) ? data : [];
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to fetch stocks";
      stocks.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  function applyAiFilters(filters: UniverseFilters): void {
    filterChips.value = [];
    aiFilters.value = mergeFilters(aiFilters.value, filters);
    _persistFilters();
  }

  function removeAiFilters(filters: UniverseFilters): void {
    if (!aiFilters.value) return;
    aiFilters.value = subtractFilters(aiFilters.value, filters);
    if (!hasActiveFilters(aiFilters.value)) {
      aiFilters.value = null;
    }
    _persistFilters();
  }

  function clearAiFilters(): void {
    aiFilters.value = null;
    _persistFilters();
  }

  function clearAllFilters(): void {
    filterChips.value = [];
    aiFilters.value = null;
    _persistFilters();
  }

  function _persistFilters(): void {
    try {
      if (aiFilters.value) {
        localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(aiFilters.value));
      } else {
        localStorage.removeItem(FILTERS_STORAGE_KEY);
      }
    } catch { /* ignore */ }
  }

  function restoreFilters(): void {
    try {
      const raw = localStorage.getItem(FILTERS_STORAGE_KEY);
      if (raw) aiFilters.value = JSON.parse(raw) as UniverseFilters;
    } catch { /* ignore */ }
  }

  const pinnedCodes: Ref<Set<string>> = ref(new Set());

  function togglePin(code: string): void {
    const next = new Set(pinnedCodes.value);
    if (next.has(code)) {
      next.delete(code);
    } else {
      next.add(code);
    }
    pinnedCodes.value = next;
  }

  const pinnedStocks = computed<Stock[]>(() =>
    filteredStocks.value.filter((s) => pinnedCodes.value.has(s.code))
  );

  return {
    stocks,
    filteredStocks,
    filterChips,
    aiFilters,
    isLoading,
    error,
    fetchStocks,
    formatMarketCapValue,
    pinnedCodes,
    togglePin,
    pinnedStocks,
    applyAiFilters,
    removeAiFilters,
    clearAiFilters,
    clearAllFilters,
    restoreFilters,
  };
}
