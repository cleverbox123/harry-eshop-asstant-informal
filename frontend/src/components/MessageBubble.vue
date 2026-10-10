<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  message: { type: Object, required: true },
})

const isUser = computed(() => props.message.role === 'user')
</script>

<template>
  <div class="row" :class="{ 'row-user': isUser, 'row-bot': !isUser }">
    <div class="avatar">{{ isUser ? '我' : 'AI' }}</div>
    <div class="bubble" :class="{ 'bubble-user': isUser, 'bubble-bot': !isUser }">
      <div class="text">{{ message.text }}</div>
      <div class="time">{{ message.time }}</div>
    </div>
  </div>
</template>

<style scoped>
.row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 14px;
}
.row-user {
  flex-direction: row-reverse;
}
.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
}
.row-user .avatar {
  background: #3b82f6;
}
.row-bot .avatar {
  background: #10b981;
}
.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.55;
  word-break: break-word;
  white-space: pre-wrap;
}
.bubble-user {
  background: #3b82f6;
  color: #fff;
  border-top-right-radius: 4px;
}
.bubble-bot {
  background: #fff;
  color: #1f2937;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}
.text {
  font-size: 14px;
}
.time {
  font-size: 11px;
  opacity: 0.6;
  margin-top: 4px;
}
.row-user .time {
  text-align: right;
}
</style>
