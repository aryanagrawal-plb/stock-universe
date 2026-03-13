<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useChat } from "../composables/useChat";

const { messages, isSending, sendMessage } = useChat();
const input = ref("");
const isOpen = ref(false);
const messagesEl = ref<HTMLElement | null>(null);

async function handleSend(): Promise<void> {
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await sendMessage(text);
  await nextTick();
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
  }
}

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}
</script>

<template>
  <div class="chat-panel" :class="{ open: isOpen }">
    <button class="chat-toggle" @click="isOpen = !isOpen">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
      AI Assistant
      <span class="chat-toggle-arrow">{{ isOpen ? "▼" : "▲" }}</span>
    </button>

    <div v-show="isOpen" class="chat-body">
      <div ref="messagesEl" class="chat-messages">
        <div v-if="messages.length === 0" class="chat-empty">
          Ask the AI assistant to help filter or analyze stocks.
        </div>
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat-msg"
          :class="msg.role"
        >
          <span class="chat-msg-role">{{ msg.role === "user" ? "You" : "AI" }}</span>
          <span class="chat-msg-text">{{ msg.content }}</span>
        </div>
        <div v-if="isSending" class="chat-msg assistant">
          <span class="chat-msg-role">AI</span>
          <span class="chat-msg-text typing">Thinking...</span>
        </div>
      </div>

      <div class="chat-input-row">
        <input
          v-model="input"
          type="text"
          placeholder="Ask about stocks..."
          class="chat-input"
          @keydown="handleKeydown"
        />
        <button class="chat-send" :disabled="isSending || !input.trim()" @click="handleSend">
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-panel {
  flex-shrink: 0;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.chat-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
}

.chat-toggle:hover {
  background: var(--color-surface-hover);
}

.chat-toggle-arrow {
  margin-left: auto;
  font-size: 10px;
  color: var(--color-text-muted);
}

.chat-body {
  display: flex;
  flex-direction: column;
  height: 280px;
  border-top: 1px solid var(--color-border);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px 20px;
}

.chat-empty {
  color: var(--color-text-muted);
  font-size: 13px;
  text-align: center;
  padding: 40px 0;
}

.chat-msg {
  margin-bottom: 10px;
}

.chat-msg-role {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  margin-right: 8px;
  color: var(--color-text-muted);
}

.chat-msg.user .chat-msg-role {
  color: var(--color-primary);
}

.chat-msg.assistant .chat-msg-role {
  color: var(--color-accent);
}

.chat-msg-text {
  font-size: 13px;
  line-height: 1.5;
}

.typing {
  color: var(--color-text-muted);
  font-style: italic;
}

.chat-input-row {
  display: flex;
  gap: 8px;
  padding: 10px 20px;
  border-top: 1px solid var(--color-border);
}

.chat-input {
  flex: 1;
  padding: 8px 12px;
  font-size: 13px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  outline: none;
}

.chat-input:focus {
  border-color: var(--color-primary);
}

.chat-send {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-sans);
  color: white;
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 0.15s;
}

.chat-send:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.chat-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
