import { ref, computed } from "vue";
import type { Stock, FilterChip } from "../types/stock";

function formatMarketCapValue(value: number): string {
  if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  return `$${value}`;
}

function formatVolumeValue(value: number): string {
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
  return String(value);
}

function getStockValueForCategory(stock: Stock, category: string): string {
  switch (category) {
    case "Sector":
      return stock.sector;
    case "Ticker":
      return stock.ticker;
    case "Name":
      return stock.name;
    case "Price":
      return stock.price.toFixed(2);
    case "Market Cap":
      return formatMarketCapValue(stock.market_cap);
    case "P/E":
      return stock.pe_ratio?.toFixed(1) ?? "";
    case "Div Yield":
      return stock.dividend_yield != null
        ? stock.dividend_yield.toFixed(2) + "%"
        : "";
    case "Volume":
      return formatVolumeValue(stock.volume);
    default:
      return "";
  }
}

export function useStocks() {
  const stocks = ref<Stock[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const filterChips = ref<FilterChip[]>([]);

  // OR within same category, AND across categories
  const filteredStocks = computed<Stock[]>(() => {
    if (filterChips.value.length === 0) return stocks.value;

    const chipsByCategory = new Map<string, string[]>();
    for (const chip of filterChips.value) {
      const values = chipsByCategory.get(chip.category) ?? [];
      values.push(chip.value);
      chipsByCategory.set(chip.category, values);
    }

    return stocks.value.filter((stock) => {
      for (const [category, values] of chipsByCategory) {
        const stockValue = getStockValueForCategory(stock, category);
        if (!values.includes(stockValue)) return false;
      }
      return true;
    });
  });

  async function fetchStocks(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await fetch("/api/stocks");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      stocks.value = await response.json();
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to fetch stocks";
    } finally {
      isLoading.value = false;
    }
  }

  return { stocks, filteredStocks, filterChips, isLoading, error, fetchStocks };
}
