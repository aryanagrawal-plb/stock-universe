<script setup lang="ts">
import { computed } from "vue";
import { Scatter } from "vue-chartjs";
import {
  Chart as ChartJS,
  LinearScale,
  LogarithmicScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";
import type { Stock } from "../types/stock";

ChartJS.register(LinearScale, LogarithmicScale, PointElement, Tooltip, Legend);

const props = defineProps<{
  stocks: Stock[];
}>();

const INDUSTRY_COLORS: Record<string, string> = {
  "Technology": "#6c5ce7",
  "Financials": "#00cec9",
  "Healthcare": "#ff6b6b",
  "Energy": "#ffa502",
  "Consumer Discretionary": "#a29bfe",
  "Consumer Staples": "#51cf66",
  "Industrials": "#fd79a8",
  "Materials": "#e17055",
  "Real Estate": "#74b9ff",
  "Utilities": "#55efc4",
  "Telecommunications": "#636e72",
  "Energy - Fossil Fuels": "#f39c12",
  "Energy - Renewable Energy": "#2ecc71",
};

const chartData = computed(() => {
  const byIndustry = new Map<string, { x: number; y: number; label: string }[]>();

  for (const s of props.stocks) {
    if (s.market_cap == null || s.pe_ratio == null) continue;
    const points = byIndustry.get(s.industry) ?? [];
    points.push({
      x: s.market_cap,
      y: s.pe_ratio,
      label: s.code,
    });
    byIndustry.set(s.industry, points);
  }

  return {
    datasets: Array.from(byIndustry.entries()).map(([industry, points]) => ({
      label: industry,
      data: points,
      backgroundColor: INDUSTRY_COLORS[industry] ?? "#8b8fa3",
      pointRadius: 5,
      pointHoverRadius: 8,
    })),
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 0 } as const,
  plugins: {
    legend: {
      position: "top" as const,
      labels: { color: "#8b8fa3", font: { size: 10 }, boxWidth: 10 },
    },
    tooltip: {
      callbacks: {
        label: (ctx: unknown) => {
          const { label, x, y } = (
            ctx as { raw: { label: string; x: number; y: number } }
          ).raw;
          return `${label}: Mkt Cap $${x.toLocaleString(undefined, { maximumFractionDigits: 0 })}, P/E ${y.toFixed(1)}`;
        },
      },
    },
  },
  scales: {
    x: {
      type: "logarithmic" as const,
      title: { display: true, text: "Market Cap ($M)", color: "#8b8fa3" },
      grid: { color: "#2a2e3a" },
      ticks: { color: "#8b8fa3" },
    },
    y: {
      title: { display: true, text: "P/E Ratio", color: "#8b8fa3" },
      grid: { color: "#2a2e3a" },
      ticks: { color: "#8b8fa3" },
      min: 0,
      max: 100,
    },
  },
};
</script>

<template>
  <div class="scatter-container">
    <h3 class="scatter-title">Stock Universe</h3>
    <div class="chart-wrap">
      <Scatter :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.scatter-container {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.scatter-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--color-text);
}

.chart-wrap {
  flex: 1;
  min-height: 350px;
  position: relative;
}
</style>
