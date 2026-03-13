import { ref, reactive, watch } from "vue";
import type { Stock, StockFilters } from "../types/stock";

export function useStocks() {
  const stocks = ref<Stock[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const filters = reactive<StockFilters>({
    sector: "",
    minPrice: null,
    maxPrice: null,
    search: "",
  });

  async function fetchStocks(): Promise<void> {
    isLoading.value = true;
    error.value = null;

    const params = new URLSearchParams();
    if (filters.sector) params.set("sector", filters.sector);
    if (filters.minPrice !== null) params.set("min_price", String(filters.minPrice));
    if (filters.maxPrice !== null) params.set("max_price", String(filters.maxPrice));
    if (filters.search) params.set("search", filters.search);

    try {
      const url = `/api/stocks${params.toString() ? `?${params}` : ""}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      stocks.value = await response.json();
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to fetch stocks";
    } finally {
      isLoading.value = false;
    }
  }

  watch(filters, () => fetchStocks(), { deep: true });

  return { stocks, filters, isLoading, error, fetchStocks };
}
