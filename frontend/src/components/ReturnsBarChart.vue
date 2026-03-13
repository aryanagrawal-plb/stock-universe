<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import * as d3 from "d3";
import type { Stock } from "../types/stock";

const props = defineProps<{
  params?: { data?: Stock } | null;
}>();

const containerRef = ref<HTMLDivElement | null>(null);
const svgRef = ref<SVGSVGElement | null>(null);

const PERIODS = [
  { label: "1M", field: "return_1m" as keyof Stock },
  { label: "3M", field: "return_3m" as keyof Stock },
  { label: "6M", field: "return_6m" as keyof Stock },
  { label: "1Y", field: "return_1y" as keyof Stock },
  { label: "5Y", field: "return_5y" as keyof Stock },
];

const chartData = computed(() => {
  const stock = props.params?.data;
  if (!stock) return [];
  return PERIODS.map(({ label, field }) => {
    const raw = stock[field] as number | null | undefined;
    const pct = raw != null ? raw * 100 : null;
    return { label, value: pct };
  });
});

const hasData = computed(() =>
  chartData.value.some((d) => d.value != null)
);

const xExtent = computed(() => {
  const values = chartData.value
    .map((d) => d.value)
    .filter((v): v is number => v != null);
  if (values.length === 0) return [-10, 10];
  const min = Math.min(0, ...values);
  const max = Math.max(0, ...values);
  const pad = Math.max(10, (max - min) * 0.1);
  return [Math.min(min - pad, 0), Math.max(max + pad, 0)];
});

const width = ref(400);
const height = 200;
const margin = { top: 20, right: 50, bottom: 40, left: 50 };

function renderChart(): void {
  if (!svgRef.value || !containerRef.value || !hasData.value) return;

  const w = containerRef.value.clientWidth || 400;
  width.value = w;
  const chartWidth = w - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const [xMin, xMax] = xExtent.value;
  const xScale = d3
    .scaleLinear()
    .domain([xMin, xMax])
    .range([0, chartWidth]);

  const yScale = d3
    .scaleBand()
    .domain(PERIODS.map((p) => p.label))
    .range([0, chartHeight])
    .padding(0.3);

  d3.select(svgRef.value).selectAll("*").remove();

  const svg = d3
    .select(svgRef.value)
    .attr("width", w)
    .attr("height", height);

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const zeroX = xScale(0);
  g.append("line")
    .attr("x1", zeroX)
    .attr("x2", zeroX)
    .attr("y1", 0)
    .attr("y2", chartHeight)
    .attr("stroke", "#d8dde2")
    .attr("stroke-width", 1)
    .attr("stroke-dasharray", "4,2");

  const barGroup = g.append("g");

  chartData.value.forEach((d) => {
    if (d.value == null) return;

    const x0 = Math.min(xScale(0), xScale(d.value));
    const x1 = Math.max(xScale(0), xScale(d.value));
    const barWidth = Math.abs(x1 - x0);
    const isPositive = d.value >= 0;
    const fill = isPositive ? "#2ecc71" : "#d9534f";

    barGroup
      .append("rect")
      .attr("x", x0)
      .attr("y", (yScale(d.label) ?? 0))
      .attr("width", barWidth)
      .attr("height", yScale.bandwidth() ?? 0)
      .attr("fill", fill)
      .attr("rx", 2);

    const textX = isPositive ? x1 + 6 : x0 - 6;
    const textAnchor = isPositive ? "start" : "end";
    barGroup
      .append("text")
      .attr("x", textX)
      .attr("y", (yScale(d.label) ?? 0) + (yScale.bandwidth() ?? 0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", textAnchor)
      .attr("fill", "#495057")
      .style("font-size", "9px")
      .style("font-family", "'Fira Sans', sans-serif")
      .text(`${d.value >= 0 ? "+" : ""}${d.value.toFixed(2)}%`);
  });

  const yAxis = d3.axisLeft(yScale).tickSize(0);
  g.append("g")
    .attr("class", "y-axis")
    .call(yAxis)
    .selectAll("line, path")
    .attr("stroke", "none");
  g.selectAll(".y-axis .tick text")
    .attr("fill", "#495057")
    .style("font-size", "11px")
    .style("font-family", "'Fira Sans', sans-serif");

  const xAxis = d3
    .axisBottom(xScale)
    .ticks(5)
    .tickFormat((d) => `${d}%`);
  const xAxisG = g.append("g").attr("class", "x-axis").attr("transform", `translate(0,${chartHeight})`);
  xAxisG.call(xAxis);
  xAxisG.selectAll("line, path").attr("stroke", "#d8dde2");
  xAxisG.selectAll(".tick text")
    .attr("fill", "#495057")
    .style("font-size", "10px")
    .style("font-family", "'Fira Sans', sans-serif");

  g.append("text")
    .attr("x", chartWidth / 2)
    .attr("y", chartHeight + margin.bottom - 6)
    .attr("text-anchor", "middle")
    .attr("fill", "#6c757d")
    .style("font-size", "10px")
    .style("font-family", "'Fira Sans', sans-serif")
    .text("Return (%)");

  g.append("text")
    .attr("transform", `rotate(-90)`)
    .attr("x", -chartHeight / 2)
    .attr("y", -margin.left + 14)
    .attr("text-anchor", "middle")
    .attr("fill", "#6c757d")
    .style("font-size", "10px")
    .style("font-family", "'Fira Sans', sans-serif")
    .text("Period");
}

let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  if (!containerRef.value) return;
  resizeObserver = new ResizeObserver(() => renderChart());
  resizeObserver.observe(containerRef.value);
  renderChart();
});

onUnmounted(() => {
  if (resizeObserver && containerRef.value) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
});

watch([chartData, hasData], () => renderChart(), { flush: "post" });
</script>

<template>
  <div ref="containerRef" class="returns-bar-chart">
    <div v-if="!hasData" class="returns-bar-chart-empty">
      No return data available
    </div>
    <svg v-else ref="svgRef" class="returns-bar-chart-svg" />
  </div>
</template>

<style lang="scss" scoped>
.returns-bar-chart {
  padding: 16px 20px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin: 8px 12px;
}

.returns-bar-chart-empty {
  font-size: 13px;
  color: #6c757d;
  font-family: "Fira Sans", sans-serif;
}

.returns-bar-chart-svg {
  display: block;
  width: 100%;
  height: 200px;
}
</style>
