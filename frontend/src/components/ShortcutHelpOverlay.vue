<script setup lang="ts">
import { computed } from "vue";
import { SHORTCUT_HELP_ENTRIES } from "../composables/shortcuts";

const isOpen = defineModel<boolean>({ default: false });

const sections = computed(() => {
  const map = new Map<string, { keys: string; label: string }[]>();
  for (const entry of SHORTCUT_HELP_ENTRIES) {
    const list = map.get(entry.section) ?? [];
    list.push({ keys: entry.keys, label: entry.label });
    map.set(entry.section, list);
  }
  return Array.from(map.entries());
});

function close(): void {
  isOpen.value = false;
}
</script>

<template>
  <Teleport to="body">
    <Transition name="pl-help-fade">
      <div
        v-show="isOpen"
        class="pl-help-backdrop"
        role="dialog"
        aria-label="Keyboard shortcuts"
        aria-modal="true"
        @keydown.escape="close"
        @click.self="close"
      >
        <div class="pl-help-sheet">
          <div class="pl-help-header">
            <h2 class="pl-help-title">Shortcuts</h2>
            <button
              type="button"
              class="pl-help-close"
              aria-label="Close"
              @click="close"
            >
              ×
            </button>
          </div>
          <p class="pl-help-intro">
            Type a code in the command bar (top) and press Enter, or use single keys when not typing in an input.
          </p>
          <div class="pl-help-sections">
            <section
              v-for="[sectionName, entries] in sections"
              :key="sectionName"
              class="pl-help-section"
            >
              <h3 class="pl-help-section-title">{{ sectionName }}</h3>
              <ul class="pl-help-list">
                <li
                  v-for="(entry, i) in entries"
                  :key="`${sectionName}-${i}`"
                  class="pl-help-row"
                >
                  <kbd class="pl-help-keys">{{ entry.keys }}</kbd>
                  <span class="pl-help-label">{{ entry.label }}</span>
                </li>
              </ul>
            </section>
          </div>
          <p class="pl-help-footer">Press <kbd>Esc</kbd> or click outside to close</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped lang="scss">
.pl-help-backdrop {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(12, 23, 67, 0.45);
  padding: 24px;
}

.pl-help-sheet {
  background: #fff;
  border-radius: 0.35rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  max-width: 420px;
  width: 100%;
  max-height: 85vh;
  overflow: auto;
}

.pl-help-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid #d8dde2;
}

.pl-help-title {
  margin: 0;
  font-family: "Fira Sans", sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: #0c1743;
}

.pl-help-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  font-size: 20px;
  line-height: 1;
  color: #495057;
  background: none;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: color 0.15s, background 0.15s;

  &:hover {
    color: #0c1743;
    background: #eff2f6;
  }
}

.pl-help-intro {
  margin: 0;
  padding: 12px 18px;
  font-size: 12px;
  color: #495057;
  line-height: 1.5;
  border-bottom: 1px solid #e8ebf0;
}

.pl-help-sections {
  padding: 14px 18px;
}

.pl-help-section {
  margin-bottom: 16px;

  &:last-child {
    margin-bottom: 0;
  }
}

.pl-help-section-title {
  margin: 0 0 6px 0;
  font-family: "Fira Sans", sans-serif;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #1a85a1;
}

.pl-help-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.pl-help-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 4px 0;
  font-size: 13px;
}

.pl-help-keys {
  flex-shrink: 0;
  min-width: 70px;
  padding: 2px 6px;
  font-family: "Roboto Mono", monospace;
  font-size: 12px;
  font-weight: 500;
  color: #0c1743;
  background: #f5f7fa;
  border: 1px solid #d8dde2;
  border-radius: 0.2rem;
}

.pl-help-label {
  color: #4b4b4b;
}

.pl-help-footer {
  margin: 0;
  padding: 10px 18px;
  font-size: 11px;
  color: #bbc1c7;
  border-top: 1px solid #d8dde2;
}

.pl-help-footer kbd {
  padding: 1px 4px;
  font-size: 10px;
  background: #eff2f6;
  border-radius: 0.2rem;
}

.pl-help-fade-enter-active,
.pl-help-fade-leave-active {
  transition: opacity 0.15s ease;
}

.pl-help-fade-enter-from,
.pl-help-fade-leave-to {
  opacity: 0;
}
</style>
