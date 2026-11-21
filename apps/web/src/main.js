import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router/index.js'
import App from './App.vue'
import { watchSessionChanges } from './services/sessionSync.js'
import './styles.css'

const app = createApp(App)

app.use(ElementPlus)
app.use(router)
app.mount('#app')

watchSessionChanges({
  toLogin: () => router.replace({ name: 'Login' }),
  reload: () => window.location.reload(),
})
