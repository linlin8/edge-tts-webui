<template>
  <div
    class="card flex items-center gap-3 px-4 py-3"
    role="region"
    :aria-label="label || '音频播放器'"
  >
    <!-- 播放/暂停按钮 -->
    <button
      class="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0
        bg-blue-600 hover:bg-blue-700 active:bg-blue-800
        dark:bg-blue-500 dark:hover:bg-blue-400
        text-white shadow transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
      :aria-label="isPlaying ? '暂停' : '播放'"
      @click="togglePlay"
    >
      <!-- 加载中旋转 -->
      <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      <!-- 播放图标 -->
      <svg v-else-if="!isPlaying" class="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>
      </svg>
      <!-- 暂停图标 -->
      <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm4-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>
      </svg>
    </button>

    <!-- 进度条区域 -->
    <div class="flex-1 min-w-0">
      <div
        v-if="label"
        class="text-xs text-gray-500 dark:text-gray-400 truncate mb-1"
      >{{ label }}</div>
      <!-- 进度条 -->
      <div
        class="relative h-1.5 rounded-full bg-gray-200 dark:bg-gray-600 cursor-pointer group"
        role="slider"
        :aria-valuenow="Math.round(currentTime)"
        :aria-valuemin="0"
        :aria-valuemax="Math.round(duration || 1)"
        :aria-label="`播放进度：${formatTime(currentTime)} / ${formatTime(duration)}`"
        @click="seek"
        @keydown.left.prevent="seekBy(-5)"
        @keydown.right.prevent="seekBy(5)"
        tabindex="0"
      >
        <!-- 缓冲进度 -->
        <div
          class="absolute inset-y-0 left-0 rounded-full bg-gray-300 dark:bg-gray-500 transition-all"
          :style="{ width: `${buffered}%` }"
        />
        <!-- 播放进度 -->
        <div
          class="absolute inset-y-0 left-0 rounded-full bg-blue-500 transition-all"
          :style="{ width: `${progress}%` }"
        />
        <!-- 拖拽圆点 -->
        <div
          class="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-blue-600 shadow
            opacity-0 group-hover:opacity-100 transition-opacity"
          :style="{ left: `calc(${progress}% - 6px)` }"
        />
      </div>
      <!-- 时间 -->
      <div class="flex justify-between mt-1">
        <span class="text-xs tabular-nums text-gray-400 dark:text-gray-500">{{ formatTime(currentTime) }}</span>
        <span class="text-xs tabular-nums text-gray-400 dark:text-gray-500">{{ formatTime(duration) }}</span>
      </div>
    </div>

    <!-- 音量 -->
    <div class="flex items-center gap-1.5 flex-shrink-0">
      <button
        class="btn-ghost p-1"
        :aria-label="muted ? '取消静音' : '静音'"
        @click="toggleMute"
      >
        <svg v-if="muted || volume === 0" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15zm12.243-9.243L11.586 12l6.243 6.243"/>
        </svg>
        <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
        </svg>
      </button>
      <input
        v-model.number="volume"
        type="range"
        min="0"
        max="1"
        step="0.05"
        class="w-16 h-1 rounded-full appearance-none cursor-pointer bg-gray-200 dark:bg-gray-600 accent-blue-500"
        aria-label="音量"
        @input="applyVolume"
      />
    </div>

    <!-- 下载 -->
    <a
      v-if="src"
      :href="src"
      download
      class="btn-ghost p-1 flex-shrink-0"
      aria-label="下载音频"
      title="下载"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
      </svg>
    </a>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue'

const props = defineProps({
  src: { type: String, default: null },
  label: { type: String, default: '' },
  autoplay: { type: Boolean, default: false },
})

const isPlaying = ref(false)
const isLoading = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const buffered = ref(0)
const volume = ref(1)
const muted = ref(false)

const progress = computed(() =>
  duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0
)

let audio = null

function createAudio(src) {
  if (audio) {
    audio.pause()
    audio.src = ''
    audio.removeEventListener('timeupdate', onTimeUpdate)
    audio.removeEventListener('loadedmetadata', onMetadata)
    audio.removeEventListener('ended', onEnded)
    audio.removeEventListener('waiting', onWaiting)
    audio.removeEventListener('playing', onPlaying)
    audio.removeEventListener('progress', onProgress)
  }
  if (!src) { audio = null; return }
  audio = new Audio(src)
  audio.volume = volume.value
  audio.muted = muted.value
  audio.addEventListener('timeupdate', onTimeUpdate)
  audio.addEventListener('loadedmetadata', onMetadata)
  audio.addEventListener('ended', onEnded)
  audio.addEventListener('waiting', onWaiting)
  audio.addEventListener('playing', onPlaying)
  audio.addEventListener('progress', onProgress)
  if (props.autoplay) {
    isLoading.value = true
    audio.play().catch(() => {})
  }
}

function onTimeUpdate() { currentTime.value = audio?.currentTime || 0 }
function onMetadata() { duration.value = audio?.duration || 0 }
function onEnded() { isPlaying.value = false; currentTime.value = 0 }
function onWaiting() { isLoading.value = true }
function onPlaying() { isLoading.value = false; isPlaying.value = true }
function onProgress() {
  if (audio?.buffered.length && audio.duration) {
    buffered.value = (audio.buffered.end(audio.buffered.length - 1) / audio.duration) * 100
  }
}

async function togglePlay() {
  if (!audio) return
  if (isPlaying.value) {
    audio.pause()
    isPlaying.value = false
  } else {
    isLoading.value = true
    try {
      await audio.play()
    } catch {
      isLoading.value = false
    }
  }
}

function seek(event) {
  if (!audio || !duration.value) return
  const rect = event.currentTarget.getBoundingClientRect()
  const ratio = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width))
  audio.currentTime = ratio * duration.value
  currentTime.value = audio.currentTime
}

function seekBy(seconds) {
  if (!audio) return
  audio.currentTime = Math.max(0, Math.min(duration.value, audio.currentTime + seconds))
}

function toggleMute() {
  muted.value = !muted.value
  if (audio) audio.muted = muted.value
}

function applyVolume() {
  if (audio) audio.volume = volume.value
}

function formatTime(t) {
  if (!t || isNaN(t)) return '0:00'
  const m = Math.floor(t / 60)
  const s = Math.floor(t % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

watch(() => props.src, (newSrc) => {
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0
  buffered.value = 0
  isLoading.value = false
  createAudio(newSrc)
}, { immediate: true })

onBeforeUnmount(() => {
  if (audio) { audio.pause(); audio.src = '' }
})
</script>
