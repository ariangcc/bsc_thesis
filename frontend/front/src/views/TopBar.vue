<template>
    <div class="cont">
        <div class="item1">
            <div class ="brand-image">
                <img src="@/images/logo_verde.png" height="140">
            </div>
        </div>
        <div class="item2">
            <img src="@/images/cara_feliz.png" height="80" width="90" class="center">
            <h6 id="img-down">Banca de Negocios</h6>
        </div>
        <div class="item3">
            <h5>{{user.charge}}</h5>
            <h3 class="p-0" id="name">{{user.name}}</h3>
            <h5>{{user.code}}</h5>
            <button class="button mb-2" @click="logOff()">Salir</button>
        </div>
    </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
export default {
    computed :{
        ...mapState(['user']),
    },
    methods :{
        ...mapActions(['setLoginEntry']),
        logOff(){
            this.setLoginEntry(false);
            this.$router.push('/');
        }
    }
}
</script>

<style src="@/styles/TopBar.css" scoped>