
import './assets/global-map-fix.css'
import 'vue-toast-notification/dist/theme-default.css'
import { createApp } from 'vue'
import ToastPlugin from 'vue-toast-notification'
import App from './App.vue'
import { i18n } from './i18n'

createApp(App).use(ToastPlugin).use(i18n).mount('#app')
