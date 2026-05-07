import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'
import './assets/styles/variables.css'
import './assets/styles/global.css'
import './assets/styles/responsive.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

const authStore = useAuthStore()
authStore.restoreSession()

app.mount('#app')
