<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useChat } from "../composables/useChat";

const { messages, isSending, sendMessage } = useChat();
const input = ref("");
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
  <div class="pl-chat-panel">
    <div class="pl-chat-header">
      <span class="pl-chat-badge">AI</span>
      <span class="pl-chat-title">Assistant</span>
    </div>

    <div ref="messagesEl" class="pl-chat-messages">
      <div v-if="messages.length === 0 && !isSending" class="pl-chat-empty">
        Ask the AI to help filter or analyze stocks.
      </div>
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="pl-chat-msg"
        :class="msg.role"
      >
        <span class="pl-chat-msg-role">{{ msg.role === "user" ? "You" : "AI" }}</span>
        <span class="pl-chat-msg-text">{{ msg.content }}</span>
      </div>
      <div v-if="isSending" class="pl-chat-msg assistant">
        <span class="pl-chat-msg-role">AI</span>
        <span class="pl-chat-msg-text pl-typing">Thinking...</span>
      </div>
    </div>

    <div class="pl-chat-input-row">
      <input
        v-model="input"
        type="text"
        placeholder="Ask about stocks..."
        class="pl-chat-input"
        @keydown="handleKeydown"
      />
      <button
        class="pl-chat-send"
        :disabled="isSending || !input.trim()"
        @click="handleSend"
      >
        <icon icon="paper-plane" />
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.pl-chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
}

.pl-chat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid #d8dde2;
  flex-shrink: 0;
}

.pl-chat-badge {
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #fff;
  background: #0c1743;
  border-radius: 4px;
}

.pl-chat-title {
  font-size: 13px;
  font-weight: 600;
  color: #495057;
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
}

.pl-chat-msg {
  margin-bottom: 12px;
}

.pl-chat-msg-role {
  display: block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 3px;
  color: #bbc1c7;
}

.pl-chat-msg.user .pl-chat-msg-role {
  color: #1a85a1;
}

.pl-chat-msg.assistant .pl-chat-msg-role {
  color: #0c1743;
}

.pl-chat-msg-text {
  font-size: 14px;
  line-height: 1.55;
  display: block;
  word-break: break-word;
  color: #4b4b4b;
}

.pl-typing {
  color: #bbc1c7;
  font-style: italic;
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
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
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
