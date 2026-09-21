import { createApp } from 'vue'

import { createPinia } from 'pinia'

import App from './App.vue'

import router from './router'

import { useUserStore } from './stores/user'

import { getDeviceSnapshot } from './composables/useDevice'

import { useDeviceStore } from './stores/device'

import { setupProgressQueueSync } from './composables/useProgressQueue'

import './styles/reset.css'

import './styles/variables.css'

import './styles/components.css'



setupProgressQueueSync()



const app = createApp(App)

app.config.errorHandler = (err, _instance, info) => {
  console.error('[AppError]', info, err)
}

const pinia = createPinia()

app.use(pinia)

app.use(router)



useDeviceStore(pinia).deviceType = getDeviceSnapshot().deviceType



const userStore = useUserStore(pinia)

userStore.bootstrap().finally(() => {

  app.mount('#app')

})

