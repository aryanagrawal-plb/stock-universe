<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted } from "vue";
import { useChat } from "../composables/useChat";
import { aiFiltersToChips } from "../composables/useStocks";
import type { UniverseFilters, FilterAction, ChatMessage } from "../types/stock";

const emit = defineEmits<{
  "set-filters": [filters: UniverseFilters];
  "apply-filters": [filters: UniverseFilters];
  "remove-filters": [filters: UniverseFilters];
  "clear-filters": [];
}>();

const { messages, isSending, sendMessage, confirmFilters, dismissFilters } =
  useChat((action: FilterAction, filters: UniverseFilters | null) => {
    if (action === "set" && filters) emit("set-filters", filters);
    else if (action === "add" && filters) emit("apply-filters", filters);
    else if (action === "remove" && filters) emit("remove-filters", filters);
    else if (action === "clear") emit("clear-filters");
  });

const input = ref("");
const messagesEl = ref<HTMLElement | null>(null);
const chatInputEl = ref<HTMLInputElement | null>(null);

function focusInput(): void {
  chatInputEl.value?.focus();
}

function clearHistory(): void {
  handleClearChat();
}

defineExpose({ focusInput, clearHistory });

const lastPendingIndex = computed<number>(() => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].filterStatus === "pending") return i;
  }
  return -1;
});

const inputEmpty = computed(() => input.value.trim().length === 0);
const hasPendingSuggestion = computed(() => lastPendingIndex.value !== -1);
const highlightDismissed = ref(false);
const showHighlight = computed(() => inputEmpty.value && hasPendingSuggestion.value && !highlightDismissed.value);

async function handleSend(): Promise<void> {
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await sendMessage(text);
  await nextTick();
  scrollToBottom();
}

function scrollToBottom(): void {
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
  }
}

watch(() => messages.value.length, async () => {
  highlightDismissed.value = false;
  await nextTick();
  scrollToBottom();
});

watch(isSending, async () => {
  await nextTick();
  scrollToBottom();
});

onMounted(async () => {
  await nextTick();
  scrollToBottom();
});

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (inputEmpty.value && hasPendingSuggestion.value) {
      handleConfirm(lastPendingIndex.value);
    } else {
      handleSend();
    }
    return;
  }
  if (e.key === "Escape" && hasPendingSuggestion.value) {
    e.preventDefault();
    highlightDismissed.value = true;
  }
}

function handleConfirm(index: number): void {
  confirmFilters(index);
}

function handleDismiss(index: number): void {
  dismissFilters(index);
}

function getFilterChips(msg: ChatMessage) {
  if (!msg.pendingFilters) return [];
  return aiFiltersToChips(msg.pendingFilters);
}

function actionLabel(msg: ChatMessage): string {
  if (msg.action === "watchlist") return "Alert criteria";
  if (msg.action === "set") return "Set";
  if (msg.action === "remove") return "Remove";
  if (msg.action === "clear") return "Clear all";
  return "Add";
}

function confirmBtnLabel(msg: ChatMessage): string {
  return msg.action === "watchlist" ? "Create Alert" : "Apply";
}

function appliedBadgeLabel(msg: ChatMessage): string {
  return msg.action === "watchlist" ? "Alert created" : "Filters applied";
}
</script>

<template>
  <div class="pl-chat-panel" :class="{ 'has-pending': showHighlight }">
    <div ref="messagesEl" class="pl-chat-messages">
      <div v-if="messages.length === 0 && !isSending" class="pl-chat-empty">
        Ask the AI to filter stocks, e.g.<br />
        <em>"Show me US tech stocks under $50"</em>
      </div>
      <template
        v-for="(msg, i) in messages"
        :key="i"
      >
        <div
          class="pl-chat-msg"
          :class="[msg.role, { 'pl-highlighted': showHighlight && i === lastPendingIndex }]"
        >
        <div v-if="showHighlight && i === lastPendingIndex" class="pl-highlight-hint">
          Press Enter to apply these changes, or press Esc to do nothing
        </div>
        <span class="pl-chat-msg-text">{{ msg.content }}</span>

        <div v-if="msg.filterStatus && msg.pendingFilters && getFilterChips(msg).length > 0" class="pl-pending-chips">
          <span class="pl-pending-label" :class="{ 'pl-remove': msg.action === 'remove' }">
            {{ actionLabel(msg) }}:
          </span>
          <span
            v-for="(chip, ci) in getFilterChips(msg)"
            :key="ci"
            class="pl-preview-chip"
            :class="{ 'pl-chip-remove': msg.action === 'remove' }"
          >
            <span class="pl-preview-chip-cat">{{ chip.category }}:</span>
            {{ chip.value }}
          </span>
        </div>
        <div v-if="msg.filterStatus === 'pending' && msg.action === 'clear'" class="pl-pending-chips">
          <span class="pl-pending-label pl-remove">Clear all filters</span>
        </div>

        <div v-if="msg.filterStatus === 'pending'" class="pl-filter-actions">
          <button
            class="pl-btn-apply"
            :class="{ 'pl-btn-alert': msg.action === 'watchlist' }"
            @click="handleConfirm(i)"
          >
            {{ confirmBtnLabel(msg) }}
          </button>
          <button class="pl-btn-dismiss" @click="handleDismiss(i)">Dismiss</button>
        </div>
        <div v-else-if="msg.filterStatus === 'applied'" class="pl-filter-badge pl-badge-applied">
          {{ appliedBadgeLabel(msg) }}
        </div>
        <div v-else-if="msg.filterStatus === 'dismissed'" class="pl-filter-badge pl-badge-dismissed">
          Dismissed
        </div>
        </div>
      </template>
      <div v-if="isSending" class="pl-chat-msg assistant">
        <span class="pl-chat-msg-text pl-typing">Thinking...</span>
      </div>
    </div>

    <div class="pl-chat-input-row">
      <input
        ref="chatInputEl"
        v-model="input"
        type="text"
        :placeholder="'Ask about stocks...'"
        class="pl-chat-input"
        @keydown="handleKeydown"
        @focus="highlightDismissed = false"
        @blur="highlightDismissed = true"
      />
      <button
        class="pl-chat-send"
        :disabled="isSending || !input.trim()"
        @click="handleSend"
      >
        Send
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.pl-chat-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: #fff;
}

.pl-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
}

.pl-chat-empty {
  color: #bbc1c7;
  font-size: 13px;
  text-align: center;
  padding: 40px 12px;
  line-height: 1.6;

  em {
    color: #1a85a1;
    font-style: italic;
  }
}

.pl-chat-msg {
  margin-bottom: 12px;
  padding: 10px 14px;
  border-radius: 0.75rem;
  max-width: 85%;
  color: #fff;
  transition: background 0.2s, box-shadow 0.2s;

  &.user {
    background: #1a85a1;
    margin-left: auto;
    border-bottom-right-radius: 0.15rem;
  }

  &.assistant {
    background: #0c1743;
    margin-right: auto;
    border-bottom-left-radius: 0.15rem;
  }

  &.pl-highlighted {
    position: relative;
    border: 1px solid #1a85a1;
    box-shadow: 0 0 0 3px rgba(26, 133, 161, 0.15);
  }
}

.has-pending .pl-chat-msg:not(.pl-highlighted) {
  opacity: 0.15;
}

.pl-highlight-hint {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  font-size: 11px;
  color: #495057;
  text-align: center;
  padding: 0 0 6px;
  line-height: 1.4;
  pointer-events: none;
}

.has-pending .pl-chat-input:focus {
  border-color: #d8dde2;
  box-shadow: none;
}

.pl-chat-msg-text {
  font-size: 14px;
  line-height: 1.55;
  display: block;
  word-break: break-word;
  color: #fff;
  white-space: pre-line;
}

.pl-typing {
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}

.pl-pending-chips {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
}

.pl-pending-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: rgba(255, 255, 255, 0.7);
  margin-right: 2px;

  &.pl-remove {
    color: #f0a860;
  }
}

.pl-preview-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 99px;
  white-space: nowrap;

  &.pl-chip-remove {
    color: #f0a860;
    background: rgba(240, 168, 96, 0.15);
    border-color: rgba(240, 168, 96, 0.25);
    text-decoration: line-through;
  }
}

.pl-preview-chip-cat {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.pl-filter-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.pl-btn-apply {
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 600;
  font-family: 'Fira Sans', sans-serif;
  color: #fff;
  background: #27ae60;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: #219a52;
  }

  &.pl-btn-alert {
    background: #0c1743;

    &:hover {
      background: #1a2a6c;
    }
  }
}

.pl-btn-dismiss {
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 600;
  font-family: 'Fira Sans', sans-serif;
  color: #6c757d;
  background: #f0f0f0;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: #e0e0e0;
  }
}

.pl-filter-badge {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 10px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  border-radius: 0.25rem;
}

.pl-badge-applied {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
}

.pl-badge-dismissed {
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.1);
}

.pl-chat-input-row {
  display: flex;
  gap: 8px;
  padding: 10px 16px;
  border-top: 1px solid #d8dde2;
  flex-shrink: 0;
}

.pl-chat-input {
  flex: 1;
  min-width: 0;
  padding: 7px 10px;
  font-size: 13px;
  font-family: 'Fira Sans', sans-serif;
  color: #4b4b4b;
  background: #f5f7fa;
  border: 1px solid #d8dde2;
  border-radius: 0.25rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;

  &::placeholder {
    color: #bbc1c7;
  }

  &:focus {
    border-color: #1a85a1;
    box-shadow: 0 0 0 3px rgba(26, 133, 161, 0.15);
  }
}

.pl-chat-send {
  flex-shrink: 0;
  padding: 0 14px;
  font-size: 12px;
  font-weight: 600;
  font-family: 'Fira Sans', sans-serif;
  color: #fff;
  background: #1a85a1;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.15s;

  &:hover:not(:disabled) {
    background: #167089;
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}
</style>
