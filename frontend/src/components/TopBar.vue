<script setup lang="ts">
import logoUrl from '@/assets/new-premialab-logo.svg';

const navItems = [
  { label: "MY UNIVERSE", active: true },
  { label: "DATA", active: false },
  { label: "ANALYTICS", active: false },
  { label: "AI REPORT", active: false },
  { label: "MY LAB", active: false },
  { label: "INSIGHTS", active: false },
  { label: "RESOURCES", active: false },
];
</script>

<template>
  <header class="pl-navbar">
    <div class="pl-navbar-inner">
      <div class="pl-navbar-brand">
        <img :src="logoUrl" alt="PremiaLab" class="pl-navbar-logo" />
      </div>

      <nav class="pl-navbar-nav">
        <a
          v-for="item in navItems"
          :key="item.label"
          href="#"
          class="pl-nav-item"
          :class="{ active: item.active }"
          @click.prevent
        >
          {{ item.label }}
        </a>
      </nav>

      <div class="pl-navbar-right">
        <button class="squared-center-fa-btn" title="Help">
          <icon icon="circle-question" />
        </button>
        <button class="squared-center-fa-btn pl-user-btn" title="Account">
          <icon icon="user" />
          <icon icon="chevron-down" class="pl-caret" />
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
.pl-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1030;
  height: 75px;
  background: #0c1743;
}

.pl-navbar-inner {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 24px;
  gap: 16px;
}

.pl-navbar-brand {
  flex-shrink: 0;
  margin-right: auto;
}

.pl-navbar-logo {
  height: 36px;
  width: auto;
}

.pl-navbar-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pl-nav-item {
  padding: 6px 14px;
  font-family: 'Work Sans', sans-serif;
  font-weight: 300;
  font-size: 0.789875rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  border: 1px solid transparent;
  border-radius: 4px;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;

  &:hover {
    color: rgba(255, 255, 255, 0.9);
  }

  &.active {
    color: #0c1743;
    background: #fff;
    border-color: rgba(12, 23, 67, 0.2);
  }
}

.pl-navbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.pl-user-btn {
  width: auto;
  padding: 0 10px;
  border-radius: 17px;
  gap: 5px;
}

.pl-caret {
  font-size: 0.6em;
  opacity: 0.6;
}
</style>
