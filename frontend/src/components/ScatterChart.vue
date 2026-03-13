<script setup lang="ts">
import { computed, onMounted } from "vue";
import { Scatter } from "vue-chartjs";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";
import { useStocks } from "../composables/useStocks";

ChartJS.register(LinearScale, PointElement, Tooltip, Legend);

const { stocks, fetchStocks } = useStocks();

onMounted(() => fetchStocks());

const sectorColors: Record<string, string> = {
  Technology: "#6c5ce7",
  Financials: "#00cec9",
  Healthcare: "#ff6b6b",
  Energy: "#ffa502",
  "Consumer Discretionary": "#a29bfe",
  "Consumer Staples": "#51cf66",
};

const chartData = computed(() => {
  const bySector = new Map<string, { x: number; y: number; label: string }[]>();

  for (const s of stocks.value) {
    const points = bySector.get(s.sector) ?? [];
    points.push({
      x: s.market_cap / 1e9,
      y: s.pe_ratio ?? 0,
      label: s.ticker,
    });
    bySector.set(s.sector, points);
  }

  return {
    datasets: Array.from(bySector.entries()).map(([sector, points]) => ({
      label: sector,
      data: points,
      backgroundColor: sectorColors[sector] ?? "#8b8fa3",
      pointRadius: 8,
      pointHoverRadius: 11,
    })),
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "top" as const,
      labels: { color: "#8b8fa3", font: { size: 11 } },
    },
    tooltip: {
      callbacks: {
        label: (ctx: { raw: { label: string; x: number; y: number } }) => {
          const { label, x, y } = ctx.raw;
          return `${label}: Mkt Cap $${x.toFixed(0)}B, P/E ${y.toFixed(1)}`;
        },
      },
    },
  },
  scales: {
    x: {
      title: { display: true, text: "Market Cap ($B)", color: "#8b8fa3" },
      grid: { color: "#2a2e3a" },
      ticks: { color: "#8b8fa3" },
    },
    y: {
      title: { display: true, text: "P/E Ratio", color: "#8b8fa3" },
      grid: { color: "#2a2e3a" },
      ticks: { color: "#8b8fa3" },
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
