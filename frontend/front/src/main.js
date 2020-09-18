import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import Vuelidate from 'vuelidate'
import VueGoogleApi from 'vue-google-api'
import vSelect from 'vue-select'

Vue.config.productionTip = false
Vue.use(Vuelidate)

import VuePromiseBtn from 'vue-promise-btn'
 
// not required. Styles for built-in spinner
import 'vue-promise-btn/dist/vue-promise-btn.css'
 
Vue.use(VuePromiseBtn) // or with global options Vue.use(VuePromiseBtn, {})
const config = {
  apiKey: 'xI-ZVnKUdlPG1C6xU_k1B-by',
  clientId: '274413991865-8nkl0uofvj08dkksqjeuv7pupmnqu2qv.apps.googleusercontent.com',
  
}
Vue.use(VueGoogleApi, config)

Vue.component('v-select', vSelect)



new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

