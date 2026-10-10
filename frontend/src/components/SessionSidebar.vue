<script setup>
import { ref } from 'vue'

const props = defineProps({
  sessions: { type: Array, required: true },
  currentSessionId: { type: String, default: null },
  senderId: { type: String, default: '' },
})

const emit = defineEmits(['new', 'select', 'rename', 'delete'])

const editingId = ref(null)
const editingTitle = ref('')

function relativeTime(ts) {
  if (!ts) return ''
  const diff = Date.now() / 1000 - ts
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)} 天前`
  return new Date(ts * 1000).toLocaleDateString('zh-CN')
}

function startRename(session) {
  editingId.value = session.session_id
  editingTitle.value = session.title
}

function submitRename(session) {
  const title = editingTitle.value.trim()
  editingId.value = null
  if (title && title !== session.title) {
    emit('rename', { sessionId: session.session_id, title })
  }
}

function askDelete(session) {
  if (confirm(`确定删除会话「${session.title}」吗？`)) {
    emit('delete', session.session_id)
  }
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-head">
      <div class="logo">AI</div>
      <button class="new-btn" @click="emit('new')">
        <span class="plus">+</span> 新建对话
      </button>
    </div>

    <div class="session-list">
      <div v-if="!sessions.length" class="empty">暂无会话，点击上方新建对话</div>
      <div
        v-for="s in sessions"
        :key="s.session_id"
        class="session-item"
        :class="{ active: s.session_id === currentSessionId }"
        @click="emit('select', s.session_id)"
      >
        <template v-if="editingId === s.session_id">
          <input
            v-model="editingTitle"
            class="rename-input"
            autofocus
            @click.stop
            @keyup.enter="submitRename(s)"
            @keyup.esc="editingId = null"
            @blur="submitRename(s)"
          />
        </template>
        <template v-else>
          <div class="session-main">
            <div class="session-title">{{ s.title }}</div>
            <div class="session-time">{{ relativeTime(s.updated_at) }}</div>
          </div>
          <div class="session-actions" @click.stop>
            <button title="重命名" @click="startRename(s)">✎</button>
            <button title="删除" @click="askDelete(s)">🗑</button>
          </div>
        </template>
      </div>
    </div>

    <div class="sidebar-foot">sender: {{ senderId }}</div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: #f7f8fa;
  border-right: 1px solid #e5e7eb;
}
.sidebar-head {
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #e5e7eb;
}
.logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #10b981, #3b82f6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}
.new-btn {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #fff;
  font-size: 13px;
  color: #374151;
  transition: all 0.15s;
}
.new-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}
.plus {
  font-weight: 700;
}
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.empty {
  padding: 20px 10px;
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 2px;
  transition: background 0.12s;
}
.session-item:hover {
  background: #eceef1;
}
.session-item.active {
  background: #e3ebfb;
}
.session-main {
  flex: 1;
  min-width: 0;
}
.session-title {
  font-size: 13px;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.session-time {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}
.session-actions {
  display: none;
  gap: 2px;
  flex-shrink: 0;
}
.session-item:hover .session-actions {
  display: flex;
}
.session-actions button {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  font-size: 12px;
  color: #6b7280;
  line-height: 1;
}
.session-actions button:hover {
  background: #dfe2e7;
  color: #1f2937;
}
.rename-input {
  flex: 1;
  min-width: 0;
  padding: 5px 8px;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
}
.sidebar-foot {
  padding: 10px 14px;
  font-size: 11px;
  color: #9ca3af;
  border-top: 1px solid #e5e7eb;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
