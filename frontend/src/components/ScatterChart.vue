<script setup lang="ts">
import { ref, computed, watchEffect, onMounted, onUnmounted } from "vue";
import * as d3 from "d3";
import type { Stock } from "../types/stock";

const props = defineProps<{
  stocks: Stock[];
}>();

const emit = defineEmits<{
  "update:universe": [value: string];
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

const containerRef = ref<HTMLDivElement | null>(null);
const svgRef = ref<SVGSVGElement | null>(null);
const gxRef = ref<SVGGElement | null>(null);
const gyRef = ref<SVGGElement | null>(null);

const width = ref(640);
const height = ref(400);
const margin = { top: 30, right: 20, bottom: 50, left: 60 };

const hoveredStock = ref<{
  stock: Stock;
  cx: number;
  cy: number;
} | null>(null);

const currentTransform = ref<d3.ZoomTransform>(d3.zoomIdentity);
const isTourActive = ref(false);
const currentTourIndustry = ref<string | null>(null);
const tourFilterIndustry = ref<string | null>(null);

const UNIVERSE_OPTIONS = [
  "All",
  "Equities",
  "Commodity",
  "Fixed Income",
  "Foreign Exchange",
  "Credit",
  "Multi-Asset",
] as const;
const selectedUniverse = ref<(typeof UNIVERSE_OPTIONS)[number]>("Equities");
const isUniverseMenuOpen = ref(false);
const universeDropdownRef = ref<HTMLDivElement | null>(null);

let resizeObserver: ResizeObserver | null = null;
let zoomBehavior: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null;
let tourTimeoutId: ReturnType<typeof setTimeout> | null = null;

onMounted(() => {
  if (containerRef.value) {
    const rect = containerRef.value.getBoundingClientRect();
    width.value = rect.width;
    height.value = Math.max(rect.height, 350);

    resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        width.value = entry.contentRect.width;
        height.value = Math.max(entry.contentRect.height, 350);
      }
    });
    resizeObserver.observe(containerRef.value);
  }

  if (svgRef.value) {
    zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([1, 20])
      .on("zoom", (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        currentTransform.value = event.transform;
        if (event.sourceEvent) cancelTour();
      });

    d3.select(svgRef.value).call(zoomBehavior);
  }
});

onUnmounted(() => {
  resizeObserver?.disconnect();
  cancelTour();
  document.removeEventListener("click", closeUniverseMenuOnClickOutside);
});

function toggleUniverseMenu(): void {
  isUniverseMenuOpen.value = !isUniverseMenuOpen.value;
  if (isUniverseMenuOpen.value) {
    setTimeout(() => document.addEventListener("click", closeUniverseMenuOnClickOutside), 0);
  } else {
    document.removeEventListener("click", closeUniverseMenuOnClickOutside);
  }
}

function closeUniverseMenuOnClickOutside(e: MouseEvent): void {
  const el = e.target as Node;
  if (!el || !universeDropdownRef.value?.contains(el)) {
    isUniverseMenuOpen.value = false;
    document.removeEventListener("click", closeUniverseMenuOnClickOutside);
  }
}

const validStocks = computed(() => {
  const withData = props.stocks.filter(
    (s) =>
      s.volatility_1y != null &&
      s.return_1y != null &&
      typeof s.volatility_1y === "number" &&
      typeof s.return_1y === "number"
  );
  const vols = withData.map((s) => s.volatility_1y as number).sort(d3.ascending);
  const p95 = d3.quantile(vols, 0.95) ?? Infinity;
  return withData.filter((s) => (s.volatility_1y as number) <= p95);
});

function stockOpacity(stock: Stock): number {
  if (tourFilterIndustry.value == null) return 0.85;
  return (stock.industry ?? "") === tourFilterIndustry.value ? 0.85 : 0.04;
}

const xScale = computed(() =>
  d3
    .scaleLinear()
    .domain(d3.extent(validStocks.value, (s) => s.volatility_1y as number) as [number, number])
    .nice()
    .range([margin.left, width.value - margin.right])
);

const yScale = computed(() =>
  d3
    .scaleLinear()
    .domain(d3.extent(validStocks.value, (s) => s.return_1y as number) as [number, number])
    .nice()
    .range([height.value - margin.bottom, margin.top])
);

const transformString = computed(() => currentTransform.value.toString());

const isZoomed = computed(() =>
  currentTransform.value.k !== 1 ||
  currentTransform.value.x !== 0 ||
  currentTransform.value.y !== 0
);

function renderAxes(): void {
  const t = currentTransform.value;
  if (gxRef.value) {
    const rescaled = t.rescaleX(xScale.value);
    const axis = d3.axisBottom(rescaled).ticks(6);
    const g = d3.select(gxRef.value).call(axis);
    g.selectAll("line, path").attr("stroke", "#d8dde2");
    g.selectAll("text").attr("fill", "#495057").style("font-size", "11px").style("font-family", "'Fira Sans', sans-serif");
  }
  if (gyRef.value) {
    const rescaled = t.rescaleY(yScale.value);
    const axis = d3.axisLeft(rescaled);
    const g = d3.select(gyRef.value).call(axis);
    g.selectAll("line, path").attr("stroke", "#d8dde2");
    g.selectAll("text").attr("fill", "#495057").style("font-size", "11px").style("font-family", "'Fira Sans', sans-serif");
  }
}

watchEffect(renderAxes);

const tourStops = computed(() => {
  const stops: Array<{ industry: string; transform: d3.ZoomTransform }> = [];

  const byIndustry = d3.group(validStocks.value, (s) => s.industry);
  const plotW = width.value - margin.left - margin.right;
  const plotH = height.value - margin.top - margin.bottom;

  for (const [industry, stocks] of byIndustry) {
    if (stocks.length < 2 || !industry) continue;

    const xs = stocks.map((s) => xScale.value(s.volatility_1y as number)).sort(d3.ascending);
    const ys = stocks.map((s) => yScale.value(s.return_1y as number)).sort(d3.ascending);

    const trimX0 = d3.quantile(xs, 0.05)!;
    const trimX1 = d3.quantile(xs, 0.95)!;
    const trimY0 = d3.quantile(ys, 0.05)!;
    const trimY1 = d3.quantile(ys, 0.95)!;

    const bw = Math.max(trimX1 - trimX0, 30);
    const bh = Math.max(trimY1 - trimY0, 30);
    const cx = (trimX0 + trimX1) / 2;
    const cy = (trimY0 + trimY1) / 2;

    const padding = 1.5;
    const scale = Math.max(Math.min(plotW / (bw * padding), plotH / (bh * padding), 10), 1);

    const midX = margin.left + plotW / 2;
    const midY = margin.top + plotH / 2;

    stops.push({
      industry,
      transform: d3.zoomIdentity
        .translate(midX, midY)
        .scale(scale)
        .translate(-cx, -cy),
    });
  }

  return stops;
});

function startTour(): void {
  if (!svgRef.value || !zoomBehavior || tourStops.value.length === 0) return;
  isTourActive.value = true;

  const svg = d3.select(svgRef.value);
  const stops = tourStops.value;
  let stopIndex = 0;

  function goToStop(): void {
    if (!isTourActive.value) return;

    const stop = stops[stopIndex];
    tourFilterIndustry.value = stop.industry;
    currentTourIndustry.value = stop.industry;

    svg
      .transition("tour")
      .duration(1000)
      .call(zoomBehavior!.transform, stop.transform)
      .on("end", () => {
        if (!isTourActive.value) return;
        stopIndex = (stopIndex + 1) % stops.length;
        tourTimeoutId = setTimeout(goToStop, 500);
      });
  }

  goToStop();
}

function cancelTour(): void {
  isTourActive.value = false;
  currentTourIndustry.value = null;
  tourFilterIndustry.value = null;
  if (tourTimeoutId != null) {
    clearTimeout(tourTimeoutId);
    tourTimeoutId = null;
  }
  if (svgRef.value) {
    d3.select(svgRef.value).interrupt("tour");
  }
}

function resetZoom(): void {
  cancelTour();
  if (svgRef.value && zoomBehavior) {
    d3.select(svgRef.value)
      .transition()
      .duration(750)
      .call(zoomBehavior.transform, d3.zoomIdentity);
  }
}

function colorFor(industry: string): string {
  return INDUSTRY_COLORS[industry] ?? "#8b8fa3";
}

function onPointEnter(stock: Stock): void {
  if (isTourActive.value) return;
  const cx = xScale.value(stock.volatility_1y as number);
  const cy = yScale.value(stock.return_1y as number);
  hoveredStock.value = { stock, cx, cy };
}

function onPointLeave(): void {
  hoveredStock.value = null;
}

function selectUniverse(option: (typeof UNIVERSE_OPTIONS)[number]): void {
  selectedUniverse.value = option;
  emit("update:universe", option);
  isUniverseMenuOpen.value = false;
  document.removeEventListener("click", closeUniverseMenuOnClickOutside);
}

function tooltipText(stock: Stock): string {
  const vol = ((stock.volatility_1y as number) * 100).toFixed(1);
  const ret = ((stock.return_1y as number) * 100).toFixed(1);
  return `${stock.code}: Vol ${vol}%, Ret ${ret}%`;
}

const tooltipX = computed(() => {
  if (!hoveredStock.value) return 0;
  const t = currentTransform.value;
  return hoveredStock.value.cx * t.k + t.x + 14;
});

const tooltipY = computed(() => {
  if (!hoveredStock.value) return 0;
  const t = currentTransform.value;
  return hoveredStock.value.cy * t.k + t.y - 10;
});
</script>

<template>
  <div class="scatter-container">
    <div class="scatter-header">
      <div
        ref="universeDropdownRef"
        class="universe-dropdown"
        @click.stop="toggleUniverseMenu"
      >
        <h3 class="scatter-title">
          My Universe
          <span class="universe-selection">{{ selectedUniverse }}</span>
          <span class="universe-chevron">▼</span>
        </h3>
        <div v-show="isUniverseMenuOpen" class="universe-menu">
          <button
            v-for="opt in UNIVERSE_OPTIONS"
            :key="opt"
            class="universe-option"
            :class="{ active: selectedUniverse === opt }"
            @click.stop="selectUniverse(opt)"
          >
            {{ opt }}
          </button>
        </div>
      </div>
      <div class="tour-controls">
        <button
          v-if="!isTourActive"
          class="tour-btn"
          @click="startTour"
        >
          Start Tour
        </button>
        <button
          v-else
          class="tour-btn tour-btn--stop"
          @click="cancelTour"
        >
          Stop Tour
        </button>
        <button
          v-if="isZoomed && !isTourActive"
          class="tour-btn"
          @click="resetZoom"
        >
          Reset Zoom
        </button>
      </div>
    </div>

    <div ref="containerRef" class="chart-wrap">
      <svg ref="svgRef" :width="width" :height="height">
        <defs>
          <clipPath id="scatter-clip">
            <rect
              :x="margin.left"
              :y="margin.top"
              :width="width - margin.left - margin.right"
              :height="height - margin.top - margin.bottom"
            />
          </clipPath>
        </defs>

        <!-- Clipped content with zoom transform -->
        <g clip-path="url(#scatter-clip)">
          <g :transform="transformString">
            <circle
              v-for="(stock, i) in validStocks"
              :key="stock.code + '-' + i"
              :cx="xScale(stock.volatility_1y as number)"
              :cy="yScale(stock.return_1y as number)"
              :r="(hoveredStock?.stock.code === stock.code ? 5.3 : 3.3) / currentTransform.k"
              :fill="colorFor(stock.industry ?? '')"
              :fill-opacity="stockOpacity(stock)"
              stroke="none"
              class="data-point"
              @mouseenter="onPointEnter(stock)"
              @mouseleave="onPointLeave"
            />
          </g>
        </g>

        <g
          ref="gxRef"
          :transform="`translate(0,${height - margin.bottom})`"
        />
        <g
          ref="gyRef"
          :transform="`translate(${margin.left},0)`"
        />

        <!-- Axis labels -->
        <text
          :x="(margin.left + width - margin.right) / 2"
          :y="height - 8"
          text-anchor="middle"
          fill="#495057"
          font-size="12"
          font-family="'Fira Sans', sans-serif"
        >
          1Y Volatility
        </text>
        <text
          :x="-(margin.top + height - margin.bottom) / 2"
          :y="14"
          text-anchor="middle"
          fill="#495057"
          font-size="12"
          font-family="'Fira Sans', sans-serif"
          transform="rotate(-90)"
        >
          1Y Return
        </text>

        <!-- Tour industry label -->
        <text
          v-if="isTourActive && currentTourIndustry"
          :x="width / 2"
          :y="margin.top + 24"
          text-anchor="middle"
          fill="#495057"
          font-size="18"
          font-weight="600"
          font-family="'Fira Sans', sans-serif"
        >
          {{ currentTourIndustry }}
        </text>

        <!-- Tooltip -->
        <g
          v-if="hoveredStock && !isTourActive"
          :transform="`translate(${tooltipX}, ${tooltipY})`"
        >
          <rect
            :width="tooltipText(hoveredStock.stock).length * 7.2 + 16"
            height="26"
            rx="4"
            fill="#ffffff"
            fill-opacity="0.9"
            stroke="#d8dde2"
            y="-18"
            x="-4"
          />
          <text fill="#4b4b4b" font-size="12" font-family="'Fira Sans', sans-serif" y="-1">
            {{ tooltipText(hoveredStock.stock) }}
          </text>
        </g>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.scatter-container {
  padding: 16px 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.scatter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.universe-dropdown {
  position: relative;
  cursor: pointer;
}

.scatter-title {
  font-family: 'Fira Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  cursor: default;
  display: flex;
  align-items: center;
  gap: 6px;
}

.universe-selection {
  color: #1a85a1;
  font-weight: 600;
}

.universe-chevron {
  color: #1a85a1;
  font-size: 10px;
}

.universe-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  min-width: 160px;
  padding: 6px 0;
  background: #fff;
  border: 1px solid #d8dde2;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.universe-option {
  display: block;
  width: 100%;
  padding: 8px 14px;
  font-size: 13px;
  font-family: 'Fira Sans', sans-serif;
  color: #495057;
  background: transparent;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s ease;
}

.universe-option:hover {
  background: #f1f3f5;
}

.universe-option.active {
  color: #1a85a1;
  font-weight: 600;
  background: rgba(26, 133, 161, 0.08);
}

.tour-controls {
  display: flex;
  gap: 6px;
}

.tour-btn {
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  font-family: 'Fira Sans', sans-serif;
  color: #495057;
  background: #f1f3f5;
  border: 1px solid #d8dde2;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.tour-btn:hover {
  background: #e9ecef;
  border-color: #ced4da;
}

.tour-btn--stop {
  color: #d9534f;
  border-color: rgba(217, 83, 79, 0.3);
}

.tour-btn--stop:hover {
  background: rgba(217, 83, 79, 0.1);
}

.chart-wrap {
  flex: 1;
  min-height: 350px;
  position: relative;
}

.data-point {
  cursor: pointer;
  transition: fill-opacity 1s ease;
}
</style>
