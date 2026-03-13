<script setup lang="ts">
import TopBar from "./components/TopBar.vue";
import StockTable from "./components/StockTable.vue";
import ScatterChart from "./components/ScatterChart.vue";
import AiChat from "./components/AiChat.vue";
</script>

<template>
  <div class="app">
    <TopBar />
    <main class="content">
      <section class="chart-section">
        <ScatterChart />
      </section>
      <section class="table-section">
        <StockTable />
      </section>
    </main>
    <AiChat />
  </div>
</template>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --color-bg: #0f1117;
  --color-surface: #1a1d27;
  --color-surface-hover: #242836;
  --color-border: #2a2e3a;
  --color-text: #e4e6eb;
  --color-text-muted: #8b8fa3;
  --color-primary: #6c5ce7;
  --color-primary-hover: #7f70f0;
  --color-accent: #00cec9;
  --color-danger: #ff6b6b;
  --color-success: #51cf66;
  --radius: 8px;
  --font-mono: "JetBrains Mono", "Fira Code", monospace;
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

body {
  font-family: var(--font-sans);
  background: var(--color-bg);
  color: var(--color-text);
  margin: 0;
}

.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.content {
  flex: 1;
  overflow-y: auto;
}

.chart-section {
  height: 420px;
  border-bottom: 1px solid var(--color-border);
}

.table-section {
  min-height: 300px;
}
</style>
