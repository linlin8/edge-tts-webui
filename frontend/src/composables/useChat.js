import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { useAudioQueue } from './useAudioQueue'

export function useChat() {
  const toast = useToast()
  const { enqueue } = useAudioQueue()

  const messages = ref([])     // [{role:'user'|'ai', content:'', isStreaming:false}]
  const sessionId = ref(localStorage.getItem('chat_session_id') || null)
  const isStreaming = ref(false)
  let abortController = null

  function newSession() {
    messages.value = []
    sessionId.value = null
    localStorage.removeItem('chat_session_id')
  }

  function _getLastMessageTime() {
    if (messages.value.length === 0) return null
    return messages.value[messages.value.length - 1].id
  }

  async function send(question, ttsParams = null) {
    const tts = !!ttsParams
    if (!question.trim() || isStreaming.value) return

    // 添加用户消息
    messages.value.push({ role: 'user', content: question, id: Date.now() })

    // 添加 AI 占位消息
    const aiMsg = { role: 'assistant', content: '', loading: true, id: Date.now() + 1, audioSrc: null }
    messages.value.push(aiMsg)
    isStreaming.value = true

    abortController = new AbortController()

    try {
      const resp = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          session_id: sessionId.value,
          tts,
          voice: ttsParams?.voice || 'zh-CN-XiaoxiaoNeural',
          rate: ttsParams?.rate || '+0%',
          volume: ttsParams?.volume || '+0%',
          pitch: ttsParams?.pitch || '+0Hz',
        }),
        signal: abortController.signal,
      })

      if (!resp.ok) {
        throw new Error(`服务器异常（${resp.status}），请稍后重试`)
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()  // 最后一行可能不完整

        for (const line of lines) {
          if (!line.startsWith('data:')) continue
          const raw = line.slice(5).trim()
          if (!raw) continue
          try {
            const evt = JSON.parse(raw)
            if (evt.type === 'text') {
              aiMsg.content += evt.delta
              if (evt.session_id) {
                sessionId.value = evt.session_id
                localStorage.setItem('chat_session_id', evt.session_id)
              }
            } else if (evt.type === 'audio') {
              enqueue(evt.data)
            } else if (evt.type === 'error') {
              toast.error(evt.msg || '对话出错')
            } else if (evt.type === 'done') {
              aiMsg.loading = false
              isStreaming.value = false
            }
          } catch { /* ignore parse errors */ }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        toast.error('连接失败：' + err.message)
      }
    } finally {
      aiMsg.loading = false
      isStreaming.value = false
    }
  }

  function abort() {
    abortController?.abort()
    isStreaming.value = false
  }

  return { messages, sessionId, isStreaming, send, newSession, abort }
}
