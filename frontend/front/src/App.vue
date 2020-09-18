<template>
  <div id="app">
    <TopBar v-if="login_entry"></TopBar>
    <router-view/>
  </div>
</template>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>

<script>

import TopBar from '@/views/TopBar.vue'
import { mapState } from 'vuex';
export default {
  components: {
    TopBar
  },
  computed:{
    ...mapState(['login_entry'])
  }
}
</script>