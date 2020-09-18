import Vue from 'vue'
import Router from 'vue-router'
import Login from './views/Login.vue'
import Mapa from './views/Mapa.vue'
Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'login',
      component: Login
    },
    {
      path: '/mapa',
      name: 'mapa',
      component: Mapa
    }
  ]
})
