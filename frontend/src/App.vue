<script setup>
import { ref, nextTick, onMounted } from 'vue'
import MessageBubble from './components/MessageBubble.vue'
import ChatInput from './components/ChatInput.vue'
import SessionSidebar from './components/SessionSidebar.vue'
import {
  sendChat,
  listSessions,
  renameSession,
  deleteSession,
  getSessionHistory,
  getSenderId,
  getCurrentSessionId,
  setCurrentSessionId,
} from './api/chat.js'

const WELCOME_TEXT =
  '你好，这里是 Atguigu 电商助手。我可以帮你查订单状态、查物流、了解商品信息，或者提交退款申请。'

const messages = ref([])
const sessions = ref([])
const currentSessionId = ref(null)
const currentTitle = ref('新对话')
const loading = ref(false)
const errorMsg = ref('')
const listRef = ref(null)
const senderId = ref(getSenderId())

function now() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function scrollToBottom() {
  await nextTick()
  if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
}

function syncCurrentTitle() {
  const found = sessions.value.find((s) => s.session_id === currentSessionId.value)
  currentTitle.value = found ? found.title : '新对话'
}

async function refreshSessions() {
  try {
    sessions.value = await listSessions()
  } catch (err) {
    errorMsg.value = err.message || '会话列表加载失败'
  }
  syncCurrentTitle()
}

async function handleSend(text) {
  errorMsg.value = ''
  messages.value.push({ role: 'user', text, time: now() })
  await scrollToBottom()

  loading.value = true
  try {
    const res = await sendChat(text, currentSessionId.value)
    for (const m of res.messages || []) {
      if (m.text) messages.value.push({ role: 'bot', text: m.text, time: now() })
    }
    if (res.session_id && res.session_id !== currentSessionId.value) {
      currentSessionId.value = res.session_id
      setCurrentSessionId(res.session_id)
    }
    await refreshSessions()
  } catch (err) {
    errorMsg.value = err.message || '请求失败'
    messages.value.push({ role: 'bot', text: `抱歉，请求出错了：${errorMsg.value}`, time: now() })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

function handleNewSession() {
  currentSessionId.value = null
  setCurrentSessionId(null)
  messages.value = [{ role: 'bot', text: WELCOME_TEXT, time: now() }]
  errorMsg.value = ''
  syncCurrentTitle()
}

async function handleSelect(sessionId) {
  if (sessionId === currentSessionId.value) return
  currentSessionId.value = sessionId
  setCurrentSessionId(sessionId)
  syncCurrentTitle()
  messages.value = []
  errorMsg.value = ''
  try {
    const history = await getSessionHistory(sessionId)
    messages.value = (history.messages || [])
      .filter((m) => m.text)
      .map((m) => ({
        role: m.role === 'user' ? 'user' : 'bot',
        text: m.text,
        time: '',
      }))
    if (!messages.value.length) {
      messages.value = [{ role: 'bot', text: WELCOME_TEXT, time: now() }]
    }
  } catch (err) {
    errorMsg.value = err.message || '历史记录加载失败'
  }
  await scrollToBottom()
}

async function handleRename({ sessionId, title }) {
  try {
    await renameSession(sessionId, title)
    await refreshSessions()
  } catch (err) {
    errorMsg.value = err.message || '重命名失败'
  }
}

async function handleDelete(sessionId) {
  try {
    await deleteSession(sessionId)
    sessions.value = sessions.value.filter((s) => s.session_id !== sessionId)
    if (sessionId === currentSessionId.value) handleNewSession()
    else syncCurrentTitle()
  } catch (err) {
    errorMsg.value = err.message || '删除失败'
  }
}

onMounted(async () => {
  handleNewSession()
  await refreshSessions()
  const stored = getCurrentSessionId()
  const target = sessions.value.some((s) => s.session_id === stored)
    ? stored
    : sessions.value[0]?.session_id || null
  if (target) await handleSelect(target)
})
</script>

<template>
  <div class="layout">
    <SessionSidebar
      :sessions="sessions"
      :current-session-id="currentSessionId"
      :sender-id="senderId"
      @new="handleNewSession"
      @select="handleSelect"
      @rename="handleRename"
      @delete="handleDelete"
    />

    <div class="app">
      <header class="header">
        <div class="title">{{ currentTitle }}</div>
        <button class="reset-btn" @click="handleNewSession">新对话</button>
      </header>

      <main ref="listRef" class="message-list">
        <div v-if="errorMsg" class="error-bar">{{ errorMsg }}</div>
        <MessageBubble v-for="(m, i) in messages" :key="i" :message="m" />
        <div v-if="loading" class="typing">
          <span></span><span></span><span></span>
        </div>
      </main>

      <ChatInput :disabled="loading" @send="handleSend" />
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
}
.app {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}
.title {
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.reset-btn {
  padding: 6px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  background: #fff;
  transition: all 0.15s;
  flex-shrink: 0;
  margin-left: 12px;
}
.reset-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f9fafb;
}
.error-bar {
  margin-bottom: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  font-size: 12px;
}
.typing {
  display: flex;
  gap: 4px;
  padding: 10px 14px;
  background: #fff;
  border-radius: 12px;
  width: fit-content;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}
.typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #9ca3af;
  animation: bounce 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.15s; }
.typing span:nth-child(3) { animation-delay: 0.3s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
  30% { transform: translateY(-4px); opacity: 1; }
}
</style>
