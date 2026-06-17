import { createApp } from 'vue'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import Toast, { POSITION } from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import VueVirtualScroller from 'vue-virtual-scroller'
import App from './App.vue'
import './styles/index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

const toastOptions = {
  position: POSITION.TOP_RIGHT,
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: false,
  pauseOnHover: true,
  draggable: false,
  maxToasts: 5,
  transition: 'Vue-Toastification__fade',
}

const app = createApp(App)
app.use(VueQueryPlugin, { queryClient })
app.use(Toast, toastOptions)
app.use(VueVirtualScroller)
app.mount('#app')
