import { ref } from 'vue'

const queue = ref([])      // base64 mp3 数组
const isPlaying = ref(false)
let currentAudio = null

function _playNext() {
  if (queue.value.length === 0) {
    isPlaying.value = false
    return
  }
  isPlaying.value = true
  const b64 = queue.value.shift()
  const binary = atob(b64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  const blob = new Blob([bytes], { type: 'audio/mpeg' })
  const url = URL.createObjectURL(blob)

  currentAudio = new Audio(url)
  currentAudio.onended = () => {
    URL.revokeObjectURL(url)
    currentAudio = null
    _playNext()
  }
  currentAudio.onerror = () => {
    URL.revokeObjectURL(url)
    currentAudio = null
    _playNext()
  }
  currentAudio.play()
}

export function useAudioQueue() {
  function enqueue(base64) {
    queue.value.push(base64)
    if (!isPlaying.value) {
      _playNext()
    }
  }

  function clear() {
    queue.value = []
    if (currentAudio) {
      currentAudio.pause()
      currentAudio = null
    }
    isPlaying.value = false
  }

  return { isPlaying, enqueue, clear }
}
