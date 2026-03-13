<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import * as d3 from "d3";

const NAVY = "#0a1628";
const INITIAL_POINTS = 2000;
const BULLET_DURATION_MS = 1000;
const WARP_DURATION_MS = 3000;
const WARP_STREAK_COUNT = 600;
const LOGO_ZOOM_MS = 1500;

const LOGO_W = 365.2;
const LOGO_H = 69.6;
const BARS_CX = 16;
const BARS_CY = 35;

const BARS_PATH = "M0,69.6l5.7-3.3V15.2L0,18.5V69.6z M13.1,54.4l5.7-3.3V0l-5.7,3.3V54.4z M26.3,18.5v19.6l5.7-3.2V15.2L26.3,18.5z";
const TEXT_PATH = "M75.8,27.1c0-5.1-3.8-8.2-9.6-8.2h-9.7v25.8h2.9v-9.1h6.3C71.2,35.6,75.8,32.7,75.8,27.1 M72.9,27.2c0,3.4-2.8,5.7-7.1,5.7h-6.4V21.6h6.5C70.1,21.6,72.9,23.5,72.9,27.2 M109.9,44.7h3.6l-7.9-10.5c4.1-0.7,7-3.2,7-7.5c0-4.6-3.7-7.7-9.3-7.7H92.2v25.8h2.9v-10h7.4L109.9,44.7L109.9,44.7z M109.6,26.7c0,3.3-2.8,5.3-6.6,5.3h-7.9V21.6h7.9C107.2,21.6,109.6,23.5,109.6,26.7 M148.5,18.9v2.6h-15.8v8.8h14.1V33h-14.1v9h15.9v2.7h-18.8V18.9L148.5,18.9z M177.9,37.6l9.4-13.8v20.9h2.9V18.9h-2.9L177.9,33l-9.4-14.1h-3v25.8h2.9V23.8l9.4,13.8H177.9z M208.8,18.9h2.9v25.8h-2.9V18.9z M270.4,44.7V18.9h3V42h14.5v2.7L270.4,44.7z M328.3,44.7l-11.7-26h-2.7l-11.7,26h3l3-6.8h14l3,6.8H328.3L328.3,44.7z M315.1,22.1l5.9,13.1h-11.7L315.1,22.1L315.1,22.1z M344.4,18.9h11c5.1,0,8.4,2.5,8.4,6.4c0,3.4-2.1,5.1-4.1,6c3,0.9,5.5,2.7,5.5,6.3c0,4.5-3.7,7.1-9.3,7.1h-11.5L344.4,18.9L344.4,18.9z M347.3,30.4h7.6c3.5,0,5.9-1.6,5.9-4.6c0-2.6-2-4.2-5.7-4.2h-7.9v8.8H347.3z M347.3,42.1h8.6c3.9,0,6.3-1.7,6.3-4.6c0-2.8-2.4-4.5-6.8-4.5h-8.1V42.1z M254.3,44.7l-11.7-26h-2.7l-11.7,26h3l3-6.8h14l3,6.8H254.3L254.3,44.7z M241.2,22.1l5.9,13.1h-11.7L241.2,22.1L241.2,22.1z";

const maskId = `bars-mask-${Math.random().toString(36).slice(2, 8)}`;

const emit = defineEmits<{ done: [] }>();

const svgRef = ref<SVGSVGElement | null>(null);
const streaksRef = ref<SVGGElement | null>(null);
const logoGroupRef = ref<SVGGElement | null>(null);
const logoBarsRef = ref<SVGPathElement | null>(null);
const logoTextRef = ref<SVGPathElement | null>(null);
const maskBarsRef = ref<SVGGElement | null>(null);
const navyBgRef = ref<SVGRectElement | null>(null);
const fadeOut = ref(false);
const vw = ref(window.innerWidth);
const vh = ref(window.innerHeight);

interface PlotPoint { x: number; y: number }

const points: PlotPoint[] = [];
for (let i = 0; i < INITIAL_POINTS; i++) {
  points.push({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
  });
}

let timeoutIds: ReturnType<typeof setTimeout>[] = [];

function warpElement(
  el: d3.Selection<SVGLineElement, unknown, null, undefined>,
  px: number, py: number,
  cx: number, cy: number,
  maxDist: number,
  stretchDur: number, flyDur: number,
): void {
  const angle = Math.atan2(py - cy, px - cx);
  const dist = Math.sqrt((px - cx) ** 2 + (py - cy) ** 2);
  const streakLen = 20 + dist * 0.2;

  el.transition()
    .duration(stretchDur)
    .attr("x2", px + Math.cos(angle) * streakLen)
    .attr("y2", py + Math.sin(angle) * streakLen)
    .attr("stroke-width", 1.5)
    .transition()
    .duration(flyDur)
    .ease(d3.easeCubicIn)
    .attr("x1", cx + Math.cos(angle) * maxDist * 0.9)
    .attr("y1", cy + Math.sin(angle) * maxDist * 0.9)
    .attr("x2", cx + Math.cos(angle) * (maxDist + streakLen * 5))
    .attr("y2", cy + Math.sin(angle) * (maxDist + streakLen * 5))
    .attr("opacity", 0)
    .remove();
}

function startLogoZoom(): void {
  if (!navyBgRef.value || !logoGroupRef.value || !maskBarsRef.value ||
      !logoBarsRef.value || !logoTextRef.value || !streaksRef.value) return;

  d3.select(streaksRef.value).selectAll("*").interrupt().remove();

  d3.select(navyBgRef.value).attr("mask", `url(#${maskId})`);

  const finalScale = Math.max(vw.value / 32, vh.value / 70) * 1.5;
  const finalTransform = `translate(${vw.value / 2}, ${vh.value / 2}) scale(${finalScale}) translate(${-BARS_CX}, ${-BARS_CY})`;

  d3.select(logoGroupRef.value)
    .transition().duration(LOGO_ZOOM_MS).ease(d3.easeCubicIn)
    .attr("transform", finalTransform);

  d3.select(maskBarsRef.value)
    .transition().duration(LOGO_ZOOM_MS).ease(d3.easeCubicIn)
    .attr("transform", finalTransform);

  d3.select(logoBarsRef.value)
    .transition().delay(LOGO_ZOOM_MS * 0.2).duration(LOGO_ZOOM_MS * 0.4)
    .attr("opacity", "0");

  d3.select(logoTextRef.value)
    .transition().duration(LOGO_ZOOM_MS * 0.3)
    .attr("opacity", "0");

  const tid = setTimeout(() => {
    d3.select(navyBgRef.value!)
      .transition().duration(400)
      .attr("opacity", "0")
      .on("end", () => {
        fadeOut.value = true;
        const doneTid = setTimeout(() => emit("done"), 300);
        timeoutIds.push(doneTid);
      });
  }, LOGO_ZOOM_MS);
  timeoutIds.push(tid);
}

function startWarp(): void {
  if (!streaksRef.value) return;
  const streaks = d3.select(streaksRef.value);
  const cx = vw.value / 2;
  const cy = vh.value / 2;
  const maxDist = Math.sqrt(cx * cx + cy * cy) * 2.5;

  streaks.selectAll("line").each(function () {
    const el = d3.select(this as SVGLineElement);
    const px = +el.attr("x1");
    const py = +el.attr("y1");
    warpElement(el, px, py, cx, cy, maxDist, 400, 2500);
  });

  const interval = WARP_DURATION_MS / WARP_STREAK_COUNT;
  for (let i = 0; i < WARP_STREAK_COUNT; i++) {
    const spawnDelay = i * interval;
    const angle = Math.random() * Math.PI * 2;
    const startDist = 10 + Math.random() * 60;
    const px = cx + Math.cos(angle) * startDist;
    const py = cy + Math.sin(angle) * startDist;
    const remainingTime = Math.max(WARP_DURATION_MS - spawnDelay, 400);
    const flyTime = remainingTime * 0.85;

    const tid = setTimeout(() => {
      if (!streaksRef.value) return;
      const el = streaks
        .append("line")
        .attr("x1", px).attr("y1", py)
        .attr("x2", px).attr("y2", py)
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 1.5)
        .attr("stroke-linecap", "round")
        .attr("opacity", 0.6) as unknown as d3.Selection<SVGLineElement, unknown, null, undefined>;

      warpElement(el, px, py, cx, cy, maxDist, Math.min(150, flyTime * 0.15), flyTime);
    }, spawnDelay);

    timeoutIds.push(tid);
  }

  const zoomTid = setTimeout(startLogoZoom, WARP_DURATION_MS);
  timeoutIds.push(zoomTid);
}

function runAnimation(): void {
  if (!svgRef.value || !streaksRef.value || !logoGroupRef.value || !maskBarsRef.value) return;

  const initTransform = `translate(${vw.value / 2}, ${vh.value / 2}) scale(${280 / LOGO_W}) translate(${-LOGO_W / 2}, ${-LOGO_H / 2})`;
  d3.select(logoGroupRef.value).attr("transform", initTransform);
  d3.select(maskBarsRef.value).attr("transform", initTransform);

  const streaks = d3.select(streaksRef.value);
  const n = INITIAL_POINTS;
  const decay = Math.pow(0.01, 1 / n);
  const initialDelay = BULLET_DURATION_MS * (1 - decay) / (1 - Math.pow(decay, n));

  let elapsed = 0;
  for (let i = 0; i < n; i++) {
    const delay = initialDelay * Math.pow(decay, i);
    elapsed += delay;

    const tid = setTimeout(() => {
      const pt = points[i];
      streaks
        .append("line")
        .attr("x1", pt.x).attr("y1", pt.y)
        .attr("x2", pt.x).attr("y2", pt.y)
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 3)
        .attr("stroke-linecap", "round")
        .attr("opacity", 0)
        .transition().duration(100)
        .attr("opacity", 0.7);
    }, elapsed);

    timeoutIds.push(tid);
  }

  const warpTid = setTimeout(startWarp, BULLET_DURATION_MS);
  timeoutIds.push(warpTid);
}

onMounted(runAnimation);

onUnmounted(() => {
  timeoutIds.forEach(clearTimeout);
  if (svgRef.value) {
    d3.select(svgRef.value).selectAll("*").interrupt();
  }
});
</script>

<template>
  <div class="splash" :class="{ 'splash--fade-out': fadeOut }">
    <svg ref="svgRef" class="splash-canvas" :width="vw" :height="vh">
      <defs>
        <mask :id="maskId">
          <rect :width="vw" :height="vh" fill="white" />
          <g ref="maskBarsRef">
            <path :d="BARS_PATH" fill="black" />
          </g>
        </mask>
      </defs>

      <rect ref="navyBgRef" :width="vw" :height="vh" :fill="NAVY" />
      <g ref="streaksRef" />
      <g ref="logoGroupRef">
        <path ref="logoBarsRef" :d="BARS_PATH" fill="white" />
        <path ref="logoTextRef" :d="TEXT_PATH" fill="white" fill-rule="evenodd" />
      </g>
    </svg>
  </div>
</template>

<style scoped>
.splash {
  position: fixed;
  inset: 0;
  z-index: 9999;
  transition: opacity 0.3s ease;
}

.splash--fade-out {
  opacity: 0;
  pointer-events: none;
}

.splash-canvas {
  position: absolute;
  inset: 0;
}
</style>
