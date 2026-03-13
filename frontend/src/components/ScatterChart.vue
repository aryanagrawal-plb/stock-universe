<script setup lang="ts">
import { ref, computed, watchEffect, onMounted, onUnmounted } from "vue";
import * as d3 from "d3";
import type { Stock } from "../types/stock";

const props = defineProps<{
  stocks: Stock[];
  selectedUniverse?: string;
}>();

const emit = defineEmits<{
  "update:universe": [value: string];
}>();

interface GroupOption {
  label: string;
  field: string;
  tooltip: string;
}

const GROUP_OPTIONS: GroupOption[] = [
  { label: "Industry",     field: "industry",     tooltip: "Primary sector classification" },
  { label: "Country",      field: "country",       tooltip: "Country where the stock is listed" },
  { label: "Exchange",     field: "exchange",      tooltip: "Stock exchange" },
  { label: "Currency",     field: "currency",      tooltip: "Trading currency" },
  { label: "Sub-Industry", field: "sub_industry",  tooltip: "Sub-sector classification" },
];

const selectedGroup = ref<GroupOption>(GROUP_OPTIONS[0]);
const showGroupDropdown = ref(false);

const PALETTE = [
  "#6c5ce7", "#00cec9", "#ff6b6b", "#ffa502", "#a29bfe",
  "#51cf66", "#fd79a8", "#e17055", "#74b9ff", "#55efc4",
  "#636e72", "#f39c12", "#2ecc71", "#e84393", "#0984e3",
  "#d63031", "#00b894", "#fdcb6e", "#6c5ce7", "#b2bec3",
  "#fab1a0", "#81ecec", "#dfe6e9", "#ffeaa7", "#ff7675",
];

const colorMap = computed(() => {
  const map = new Map<string, string>();
  const values = activeGroupValues.value;
  for (let i = 0; i < values.length; i++) {
    map.set(values[i], PALETTE[i % PALETTE.length]);
  }
  return map;
});

function colorFor(value: string): string {
  return colorMap.value.get(value) ?? "#8b8fa3";
}

function getGroupValue(stock: Stock): string {
  return ((stock as unknown as Record<string, unknown>)[selectedGroup.value.field] as string) ?? "";
}

interface PeriodOption {
  label: string;
  volField: keyof Stock;
  retField: keyof Stock;
  xLabel: string;
  yLabel: string;
}

const PERIOD_OPTIONS: PeriodOption[] = [
  { label: "1M",  volField: "volatility_1m",  retField: "return_1m",  xLabel: "1M Volatility",  yLabel: "1M Return" },
  { label: "3M",  volField: "volatility_3m",  retField: "return_3m",  xLabel: "3M Volatility",  yLabel: "3M Return" },
  { label: "6M",  volField: "volatility_6m",  retField: "return_6m",  xLabel: "6M Volatility",  yLabel: "6M Return" },
  { label: "1Y",  volField: "volatility_1y",  retField: "return_1y",  xLabel: "1Y Volatility",  yLabel: "1Y Return" },
  { label: "3Y",  volField: "volatility_3y",  retField: "return_3y",  xLabel: "3Y Volatility",  yLabel: "3Y Return" },
  { label: "5Y",  volField: "volatility_5y",  retField: "return_5y",  xLabel: "5Y Volatility",  yLabel: "5Y Return" },
  { label: "YTD", volField: "volatility_ytd", retField: "return_ytd", xLabel: "YTD Volatility", yLabel: "YTD Return" },
];

const selectedPeriod = ref<PeriodOption>(PERIOD_OPTIONS[3]);

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
const currentTourLabel = ref<string | null>(null);
const tourFilterValue = ref<string | null>(null);

const UNIVERSE_OPTIONS = [
  "All",
  "Equities",
  "Commodity",
  "Fixed Income",
  "Foreign Exchange",
  "Credit",
  "Multi-Asset",
] as const;
const displayUniverse = computed(
  () => (props.selectedUniverse as (typeof UNIVERSE_OPTIONS)[number]) ?? "Equities"
);
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

const volField = computed(() => selectedPeriod.value.volField);
const retField = computed(() => selectedPeriod.value.retField);

function stockVal(s: Stock, field: string): unknown {
  return (s as unknown as Record<string, unknown>)[field];
}

const validStocks = computed(() => {
  const vf = volField.value;
  const rf = retField.value;
  const withData = props.stocks.filter(
    (s) =>
      stockVal(s, vf) != null &&
      stockVal(s, rf) != null &&
      typeof stockVal(s, vf) === "number" &&
      typeof stockVal(s, rf) === "number"
  );
  const vols = withData.map((s) => stockVal(s, vf) as number).sort(d3.ascending);
  const p95 = d3.quantile(vols, 0.95) ?? Infinity;
  return withData.filter((s) => (stockVal(s, vf) as number) <= p95);
});

function stockOpacity(stock: Stock): number {
  if (tourFilterValue.value == null) return 0.85;
  return getGroupValue(stock) === tourFilterValue.value ? 0.85 : 0.04;
}

function getVol(s: Stock): number {
  return (s as unknown as Record<string, number>)[volField.value];
}
function getRet(s: Stock): number {
  return (s as unknown as Record<string, number>)[retField.value];
}

const xScale = computed(() =>
  d3
    .scaleLinear()
    .domain(d3.extent(validStocks.value, getVol) as [number, number])
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

const activeGroupValues = computed(() => {
  const set = new Set<string>();
  for (const s of validStocks.value) {
    const v = getGroupValue(s);
    if (v) set.add(v);
  }
  return [...set].sort();
});

const tourStops = computed(() => {
  const stops: Array<{ label: string; transform: d3.ZoomTransform }> = [];

  const byGroup = d3.group(validStocks.value, getGroupValue);
  const plotW = width.value - margin.left - margin.right;
  const plotH = height.value - margin.top - margin.bottom;

  for (const [groupVal, stocks] of byGroup) {
    if (stocks.length < 2 || !groupVal) continue;

    const xs = stocks.map((s) => xScale.value(getVol(s))).sort(d3.ascending);
    const ys = stocks.map((s) => yScale.value(getRet(s))).sort(d3.ascending);

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
      label: groupVal,
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
    tourFilterValue.value = stop.label;
    currentTourLabel.value = stop.label;

    svg
      .transition("tour")
      .duration(1000)
      .call(zoomBehavior!.transform, stop.transform)
      .on("end", () => {
        if (!isTourActive.value) return;
        stopIndex += 1;
        if (stopIndex >= stops.length) {
          tourTimeoutId = setTimeout(() => endTour(), 1200);
          return;
        }
        tourTimeoutId = setTimeout(goToStop, 500);
      });
  }

  goToStop();
}

function endTour(): void {
  isTourActive.value = false;
  currentTourLabel.value = null;
  tourFilterValue.value = null;
  if (tourTimeoutId != null) {
    clearTimeout(tourTimeoutId);
    tourTimeoutId = null;
  }
  if (svgRef.value && zoomBehavior) {
    d3.select(svgRef.value)
      .transition()
      .duration(750)
      .call(zoomBehavior.transform, d3.zoomIdentity);
  }
}

function cancelTour(): void {
  isTourActive.value = false;
  currentTourLabel.value = null;
  tourFilterValue.value = null;
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

function selectGroup(opt: GroupOption): void {
  cancelTour();
  selectedGroup.value = opt;
  showGroupDropdown.value = false;
}

function onPointEnter(stock: Stock): void {
  if (isTourActive.value) return;
  const cx = xScale.value(getVol(stock));
  const cy = yScale.value(getRet(stock));
  hoveredStock.value = { stock, cx, cy };
}

function onPointLeave(): void {
  hoveredStock.value = null;
}

function selectUniverse(option: (typeof UNIVERSE_OPTIONS)[number]): void {
  emit("update:universe", option);
  isUniverseMenuOpen.value = false;
  document.removeEventListener("click", closeUniverseMenuOnClickOutside);
}

function tooltipText(stock: Stock): string {
  const vol = (getVol(stock) * 100).toFixed(1);
  const ret = (getRet(stock) * 100).toFixed(1);
  const group = getGroupValue(stock);
  return `${stock.code} (${group}): Vol ${vol}%, Ret ${ret}%`;
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
        <h3 class="scatter-title" >
          <span style="margin-right: 1rem">My Universe</span>
          <span class="universe-selection">{{ displayUniverse }}</span>
          <span class="universe-chevron">&#9660;</span>
        </h3>
        <div v-show="isUniverseMenuOpen" class="universe-menu">
          <button
            v-for="opt in UNIVERSE_OPTIONS"
            :key="opt"
            class="universe-option"
            :class="{ active: displayUniverse === opt }"
            @click.stop="selectUniverse(opt)"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <div v-if="displayUniverse === 'Equities'" class="period-selector">
        <button
          v-for="p in PERIOD_OPTIONS"
          :key="p.label"
          class="period-btn"
          :class="{ active: selectedPeriod.label === p.label }"
          @click="selectedPeriod = p"
        >
          {{ p.label }}
        </button>
      </div>

      <div class="header-spacer"></div>

      <div class="tour-controls">
        <div v-if="displayUniverse === 'Equities'" class="group-selector-wrap">
          <button
            class="tour-btn"
            :class="{ 'tour-btn--active': showGroupDropdown }"
            @click="showGroupDropdown = !showGroupDropdown"
          >
            {{ selectedGroup.label }}
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px">
              <polyline :points="showGroupDropdown ? '18 15 12 9 6 15' : '6 9 12 15 18 9'" />
            </svg>
          </button>
          <div v-if="showGroupDropdown" class="group-dropdown shadow">
            <button
              v-for="opt in GROUP_OPTIONS"
              :key="opt.field"
              class="group-dropdown-item"
              :class="{ selected: selectedGroup.field === opt.field }"
              @click="selectGroup(opt)"
            >
              <span class="group-dropdown-label">{{ opt.label }}</span>
              <span class="group-dropdown-hint">{{ opt.tooltip }}</span>
            </button>
          </div>
        </div>
        <button
          v-if="displayUniverse === 'Equities' && !isTourActive"
          class="tour-btn"
          @click="startTour"
        >
          Start Tour
        </button>
        <button
          v-if="displayUniverse === 'Equities' && isTourActive"
          class="tour-btn tour-btn--stop"
          @click="cancelTour"
        >
          Stop Tour
        </button>
        <button
          v-if="displayUniverse === 'Equities' && isZoomed && !isTourActive"
          class="tour-btn"
          @click="resetZoom"
        >
          Reset Zoom
        </button>
      </div>
    </div>

    <div v-if="displayUniverse === 'Equities'" ref="containerRef" class="chart-wrap">
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
              :cx="xScale(getVol(stock))"
              :cy="yScale(getRet(stock))"
              :r="(hoveredStock?.stock.code === stock.code ? 5.3 : 3.3) / currentTransform.k"
              :fill="colorFor(getGroupValue(stock))"
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

        <text
          :x="(margin.left + width - margin.right) / 2"
          :y="height - 8"
          text-anchor="middle"
          fill="#495057"
          font-size="12"
          font-family="'Fira Sans', sans-serif"
        >
          {{ selectedPeriod.xLabel }}
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
          {{ selectedPeriod.yLabel }}
        </text>

        <text
          v-if="isTourActive && currentTourLabel"
          :x="width / 2"
          :y="margin.top + 24"
          text-anchor="middle"
          fill="#495057"
          font-size="18"
          font-weight="600"
          font-family="'Fira Sans', sans-serif"
        >
          {{ currentTourLabel }}
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
    <div v-else class="chart-wrap chart-placeholder">
      <p class="chart-placeholder-text">Not implemented yet</p>
    </div>

    <div class="color-legend">
      <span
        v-for="val in activeGroupValues"
        :key="val"
        class="legend-item"
      >
        <span class="legend-dot" :style="{ background: colorFor(val) }"></span>
        <span class="legend-label">{{ val }}</span>
      </span>
    </div>
  </div>
</template>

<style scoped>
.scatter-container {
  padding: 12px 20px 6px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden;
}

.scatter-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
  flex-shrink: 0;
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
  flex-shrink: 0;
  margin-bottom: 0;
}

.header-spacer {
  flex: 1;
}

/* Group selector */
.group-selector-wrap {
  position: relative;
}

.tour-btn--active {
  border-color: #1a85a1;
  color: #1a85a1;
  background: rgba(26, 133, 161, 0.06);
}

.group-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  min-width: 220px;
  background: #fff;
  border: 1px solid #d8dde2;
  border-radius: 6px;
  z-index: 300;
  padding: 4px 0;
}

.group-dropdown-item {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 7px 14px;
  font-family: 'Fira Sans', sans-serif;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  transition: background 0.1s;
}

.group-dropdown-item:hover {
  background: #f1f3f5;
}

.group-dropdown-item.selected {
  background: rgba(26, 133, 161, 0.06);
}

.group-dropdown-label {
  font-size: 13px;
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

.group-dropdown-item.selected .group-dropdown-label {
  color: #1a85a1;
}

.group-dropdown-hint {
  font-size: 10px;
  color: #adb5bd;
  margin-top: 1px;
}

/* Period selector */
.period-selector {
  display: flex;
  gap: 2px;
  background: #f1f3f5;
  border-radius: 5px;
  padding: 2px;
}

.period-btn {
  padding: 3px 9px;
  font-size: 11px;
  font-weight: 600;
  font-family: 'Fira Sans', sans-serif;
  color: #6c757d;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.period-btn:hover {
  color: #495057;
  background: #e9ecef;
}

.period-btn.active {
  color: #fff;
  background: #1a85a1;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}

/* Tour controls — right aligned */
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
  border-radius: 0.25rem;
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

/* Chart area */
.chart-wrap {
  flex: 1;
  min-height: 350px;
  position: relative;
}

.chart-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder-text {
  font-family: 'Fira Sans', sans-serif;
  font-size: 14px;
  color: #8b8fa3;
}

.data-point {
  cursor: pointer;
  transition: fill-opacity 1s ease;
}

/* Legend */
.color-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
  padding: 6px 4px 4px;
  flex-shrink: 0;
  max-height: 52px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #d8dde2 transparent;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  font-size: 10px;
  font-family: 'Fira Sans', sans-serif;
  color: #6c757d;
  white-space: nowrap;
}
</style>
