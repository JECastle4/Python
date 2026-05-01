
import './assets/global-map-fix.css'
import 'vue-toast-notification/dist/theme-default.css'
import { createApp } from 'vue'
import ToastPlugin from 'vue-toast-notification'
import App from './App.vue'

createApp(App).use(ToastPlugin).mount('#app')
