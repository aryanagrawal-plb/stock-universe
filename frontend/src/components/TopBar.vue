<script setup lang="ts">
import logoUrl from "../assets/logo.svg";
</script>

<template>
  <header class="topbar">
    <div class="topbar-left">
      <img :src="logoUrl" alt="Stock Universe" class="topbar-logo" />
      <span class="topbar-title">Stock Universe</span>
    </div>
    <div class="topbar-right">
      <button class="topbar-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/>
          <line x1="3" y1="6" x2="21" y2="6"/>
          <path d="M16 10a4 4 0 01-8 0"/>
        </svg>
        My Basket
      </button>
      <button class="topbar-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        My Account
      </button>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 48px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar-logo {
  width: 28px;
  height: 28px;
}

.topbar-title {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.3px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.topbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 13px;
  font-family: var(--font-sans);
  color: var(--color-text-muted);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.15s ease;
}

.topbar-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
  border-color: var(--color-text-muted);
}
</style>
