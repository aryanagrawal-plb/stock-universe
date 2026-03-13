<script setup lang="ts">
import { computed } from "vue";
import ReturnsBarChart from "./ReturnsBarChart.vue";
import type { Stock } from "../types/stock";

const props = defineProps<{
  params?: { data?: Stock; node?: { data?: Stock } } | null;
}>();

const stockData = computed(() => props.params?.data ?? props.params?.node?.data ?? null);

const METRIC_LABELS: Record<string, string> = {
  code: "Code",
  name: "Name",
  ticker: "Ticker",
  price: "Price",
  market_cap: "Market Cap",
  pe_ratio: "P/E Ratio",
  pb_ratio: "P/B Ratio",
  dividend_yield: "Dividend Yield",
  roe: "ROE",
  eps: "EPS",
  return_1m: "Return 1M",
  return_3m: "Return 3M",
  return_6m: "Return 6M",
  return_1y: "Return 1Y",
  return_5y: "Return 5Y",
  volatility_1y: "Volatility 1Y",
  sharpe_1y: "Sharpe 1Y",
  industry: "Industry",
  country: "Country",
  exchange: "Exchange",
};

const DISPLAY_METRICS = [
  "price",
  "market_cap",
  "pe_ratio",
  "dividend_yield",
  "roe",
  "return_1m",
  "return_3m",
  "return_6m",
  "return_1y",
  "return_5y",
  "volatility_1y",
  "sharpe_1y",
  "industry",
  "country",
  "exchange",
];

function formatMetricLabel(key: string): string {
  return (
    METRIC_LABELS[key] ??
    key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
  );
}

function formatMetricValue(key: string, val: unknown): string {
  if (typeof val === "number") {
    if (key.startsWith("return_") || key.startsWith("volatility_"))
      return `${(val * 100).toFixed(2)}%`;
    if (key === "dividend_yield" || key === "roe") return `${val.toFixed(2)}%`;
    if (key === "market_cap" || key === "turnover")
      return val.toLocaleString("en-US", { maximumFractionDigits: 0 });
    return val.toFixed(2);
  }
  return String(val);
}
</script>

<template>
  <div class="stock-detail-panel">
    <section class="stock-detail-section stock-detail-returns">
      <h4 class="stock-detail-section-title">Returns</h4>
      <div class="stock-detail-chart">
        <ReturnsBarChart :params="stockData ? { data: stockData } : undefined" />
      </div>
    </section>
    <section v-if="stockData" class="stock-detail-section stock-detail-metrics">
      <h4 class="stock-detail-section-title">Stock fundamentals</h4>
      <div class="stock-detail-header">
        <strong>{{ stockData.name }}</strong>
        <span class="stock-detail-ticker">{{ stockData.ticker }}</span>
      </div>
      <dl class="stock-detail-metrics-list">
        <template v-for="key in DISPLAY_METRICS" :key="key">
          <template v-if="(stockData as unknown as Record<string, unknown>)[key] != null">
            <dt class="stock-detail-metric-term">
              {{ formatMetricLabel(key) }}
            </dt>
            <dd class="stock-detail-metric-value">
              {{
                formatMetricValue(
                  key,
                  (stockData as unknown as Record<string, unknown>)[key]
                )
              }}
            </dd>
          </template>
        </template>
      </dl>
    </section>
  </div>
</template>

<style lang="scss" scoped>
.stock-detail-panel {
  display: flex;
  flex-direction: row;
  gap: 24px;
  padding: 12px 16px;
  min-height: 0;
  align-items: stretch;
}

.stock-detail-section {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* Left: returns graph */
.stock-detail-returns {
  flex: 1;
  min-width: 0;
}

.stock-detail-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #495057;
  margin: 0 0 8px 0;
  font-family: "Fira Sans", sans-serif;
}

.stock-detail-chart {
  flex: 0 0 auto;
  min-width: 0;
}

/* Right: stock fundamentals */
.stock-detail-metrics {
  width: 260px;
  min-width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow: auto;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.stock-detail-header {
  margin-bottom: 12px;
  font-family: "Fira Sans", sans-serif;
}

.stock-detail-header strong {
  display: block;
  font-size: 14px;
  color: #212529;
}

.stock-detail-ticker {
  font-size: 12px;
  color: #1a85a1;
}

.stock-detail-metrics-list {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 2px 16px;
  margin: 0;
  font-size: 12px;
}

.stock-detail-metric-term {
  margin: 0;
  color: #6c757d;
  font-weight: 400;
}

.stock-detail-metric-value {
  margin: 0;
  color: #212529;
  font-family: "Roboto", monospace;
}
</style>
