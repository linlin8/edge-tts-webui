<template>
  <div
    :class="['min-h-screen flex flex-col', isDark ? 'dark' : '']"
  >
    <div class="flex flex-col h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-200">
      <!-- 顶部导航 -->
      <header class="flex-shrink-0 h-14 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="h-full flex items-center justify-between px-4 max-w-screen-2xl mx-auto">
          <!-- Logo -->
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-sm">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clip-rule="evenodd"/>
              </svg>
            </div>
            <span class="font-bold text-gray-900 dark:text-gray-100 text-base tracking-tight">Edge TTS</span>
          </div>

          <!-- Tab 切换 -->
          <nav class="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              class="px-3.5 py-1.5 text-sm font-medium rounded-md transition-all duration-150 focus:outline-none"
              :class="activeTab === tab.id
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'"
              :aria-selected="activeTab === tab.id"
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </nav>

          <!-- 右侧工具 -->
          <div class="flex items-center gap-2">
            <!-- 暗色模式切换 -->
            <button
              class="btn-ghost p-2 rounded-lg"
              :aria-label="isDark ? '切换浅色模式' : '切换深色模式'"
              :title="isDark ? '切换浅色模式' : '切换深色模式'"
              @click="toggleDark"
            >
              <svg v-if="isDark" class="w-4.5 h-4.5 w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
              </svg>
            </button>
          </div>
        </div>
      </header>

      <!-- 主体内容 -->
      <main class="flex-1 overflow-hidden max-w-screen-2xl mx-auto w-full px-4 py-4">
        <!-- TTS Tab -->
        <div v-show="activeTab === 'tts'" class="flex gap-4 h-full">
          <!-- 左侧：语音选择（5/12） -->
          <div class="w-5/12 card p-4 flex flex-col overflow-hidden">
            <h2 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex-shrink-0">
              选择语音
            </h2>
            <VoiceSelector
              v-model="selectedVoice"
              class="flex-1 overflow-hidden"
            />
          </div>
          <!-- 右侧：TTS表单（7/12） -->
          <div class="w-7/12 card p-4 flex flex-col overflow-y-auto">
            <h2 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex-shrink-0">
              文字转语音
              <span v-if="selectedVoice" class="ml-2 text-xs font-normal text-blue-500">{{ selectedVoice }}</span>
            </h2>
            <TTSForm :selected-voice="selectedVoice" class="flex-1" @update:params="p => { ttsRate = p.rate; ttsVolume = p.volume; ttsPitch = p.pitch }" />
          </div>
        </div>

        <!-- 历史 Tab -->
        <div v-show="activeTab === 'history'" class="h-full card p-4 overflow-hidden flex flex-col">
          <HistoryList :active-tab="activeTab" class="flex-1 overflow-hidden" />
        </div>

        <!-- 对话 Tab -->
        <div v-show="activeTab === 'chat'" class="h-full card p-4 overflow-hidden flex flex-col">
          <ChatPanel
            :selected-voice="selectedVoice"
            :is-configured="ragflowConfigured"
            :tts-rate="ttsRate"
            :tts-volume="ttsVolume"
            :tts-pitch="ttsPitch"
            class="flex-1 overflow-hidden"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VoiceSelector from './components/VoiceSelector.vue'
import TTSForm from './components/TTSForm.vue'
import HistoryList from './components/HistoryList.vue'
import ChatPanel from './components/ChatPanel.vue'

const isDark = ref(false)
const activeTab = ref('tts')
const selectedVoice = ref('zh-CN-XiaoxiaoNeural')
const ttsRate = ref('+0%')
const ttsVolume = ref('+0%')
const ttsPitch = ref('+0Hz')
const ragflowConfigured = ref(false)

const tabs = [
  { id: 'tts', label: 'TTS 合成' },
  { id: 'history', label: '历史记录' },
  { id: 'chat', label: 'AI 对话' },
]

function toggleDark() {
  isDark.value = !isDark.value
  localStorage.setItem('dark', isDark.value ? '1' : '0')
}

onMounted(async () => {
  // 恢复暗色偏好
  const saved = localStorage.getItem('dark')
  if (saved === '1') isDark.value = true
  else if (saved === null && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    isDark.value = true
  }

  // 检测RAGFlow配置状态
  try {
    const res = await fetch('/api/v1/chat/status')
    if (res.ok) {
      const json = await res.json()
      ragflowConfigured.value = json.data?.configured === true
    }
  } catch {
    ragflowConfigured.value = false
  }
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
