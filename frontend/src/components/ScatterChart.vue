<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import * as am5 from "@amcharts/amcharts5";
import * as am5xy from "@amcharts/amcharts5/xy";
import am5themes_Animated from "@amcharts/amcharts5/themes/Animated";
import type { Stock } from "../types/stock";

const props = defineProps<{
  stocks: Stock[];
}>();

const chartDiv = ref<HTMLElement | null>(null);
let root: am5.Root | null = null;
let chart: am5xy.XYChart | null = null;

const LAB_COLORS = [
  "#4f81bd", "#9bbb58", "#4bacc6", "#2c4d75",
  "#86b6b8", "#008b8d", "#d9534f", "#f0ad4e",
  "#5cb85c", "#7c5295", "#c0504d", "#1a85a1",
];


function updateData(): void {
  if (!chartDiv.value) return;

  // Dispose and rebuild chart entirely when data changes
  if (root) {
    root.dispose();
    root = null;
    chart = null;
  }

  if (props.stocks.length === 0) return;

  root = am5.Root.new(chartDiv.value);
  root.setThemes([am5themes_Animated.new(root)]);
  const r = root;

  chart = r.container.children.push(
    am5xy.XYChart.new(r, {
      panX: true,
      panY: true,
      wheelY: "zoomXY",
      pinchZoomX: true,
    })
  );

  const xAxis = chart.xAxes.push(
    am5xy.ValueAxis.new(r, {
      logarithmic: true,
      treatZeroAs: 1,
      renderer: am5xy.AxisRendererX.new(r, {}),
      tooltip: am5.Tooltip.new(r, {}),
    })
  );
  xAxis.children.push(
    am5.Label.new(r, {
      text: "Market Cap ($M)",
      x: am5.p50,
      centerX: am5.p50,
      fontFamily: "Fira Sans",
      fontSize: 12,
      fill: am5.color("#495057"),
    })
  );

  const yAxis = chart.yAxes.push(
    am5xy.ValueAxis.new(r, {
      min: 0,
      max: 100,
      strictMinMax: true,
      renderer: am5xy.AxisRendererY.new(r, {}),
      tooltip: am5.Tooltip.new(r, {}),
    })
  );
  yAxis.children.unshift(
    am5.Label.new(r, {
      text: "P/E Ratio",
      rotation: -90,
      y: am5.p50,
      centerX: am5.p50,
      fontFamily: "Fira Sans",
      fontSize: 12,
      fill: am5.color("#495057"),
    })
  );

  [xAxis, yAxis].forEach((axis) => {
    const renderer = axis.get("renderer");
    renderer.labels.template.setAll({
      fontFamily: "Fira Sans",
      fontSize: 12,
      fill: am5.color("#495057"),
    });
    renderer.grid.template.setAll({
      stroke: am5.color("#d8dde2"),
      strokeOpacity: 0.6,
    });
  });

  const byIndustry = new Map<string, { marketCap: number; peRatio: number; code: string }[]>();
  for (const s of props.stocks) {
    if (s.market_cap == null || s.pe_ratio == null) continue;
    if (s.market_cap <= 0 || s.pe_ratio < 0 || s.pe_ratio > 100) continue;
    const list = byIndustry.get(s.industry) ?? [];
    list.push({ marketCap: s.market_cap, peRatio: s.pe_ratio, code: s.code });
    byIndustry.set(s.industry, list);
  }

  let colorIdx = 0;

  for (const [industry, points] of byIndustry) {
    const series = chart.series.push(
      am5xy.LineSeries.new(r, {
        name: industry,
        xAxis: xAxis,
        yAxis: yAxis,
        valueXField: "marketCap",
        valueYField: "peRatio",
        tooltip: am5.Tooltip.new(r, {
          labelText: "{code}: Mkt Cap ${marketCap}, P/E {peRatio}",
          getFillFromSprite: false,
          autoTextColor: false,
        }),
      })
    );

    const color = am5.color(LAB_COLORS[colorIdx % LAB_COLORS.length]);
    colorIdx++;

    series.strokes.template.set("visible", false);

    const tooltip = series.get("tooltip");
    if (tooltip) {
      tooltip.get("background")?.setAll({
        fill: am5.color("#ffffff"),
        fillOpacity: 0.8,
        strokeWidth: 1,
        stroke: am5.color("#d8dde2"),
      });
      tooltip.label.setAll({
        fill: am5.color("#4b4b4b"),
        fontFamily: "Fira Sans",
        fontSize: 12,
      });
    }

    series.bullets.push(() =>
      am5.Bullet.new(r, {
        sprite: am5.Circle.new(r, {
          radius: 4,
          fill: color,
          strokeWidth: 1,
          stroke: color,
          fillOpacity: 0.7,
        }),
      })
    );

    series.data.setAll(points);
  }

  chart.appear(1000, 100);
}

watch(() => props.stocks, updateData, { deep: true });

onMounted(() => {
  if (props.stocks.length > 0) {
    updateData();
  }
});

onBeforeUnmount(() => {
  if (root) {
    root.dispose();
    root = null;
  }
});
</script>

<template>
  <div class="scatter-container">
    <h3 class="scatter-title">My Universe</h3>
    <div ref="chartDiv" class="chart-root"></div>
  </div>
</template>

<style scoped lang="scss">
.scatter-container {
  padding: 16px 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.scatter-title {
  font-family: 'Fira Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #495057;
}

.chart-root {
  flex: 1;
  min-height: 350px;
  width: 100%;
}
</style>
