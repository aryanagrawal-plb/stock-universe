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
      <div class="panel-left">
        <StockTable />
      </div>
      <div class="panel-right">
        <ScatterChart />
      </div>
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
  min-height: 100vh;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  display: flex;
  flex: 1;
  gap: 1px;
  background: var(--color-border);
  overflow: hidden;
}

.panel-left {
  flex: 1;
  background: var(--color-bg);
  overflow-y: auto;
  min-width: 0;
}

.panel-right {
  flex: 1;
  background: var(--color-bg);
  overflow-y: auto;
  min-width: 0;
}
</style>
