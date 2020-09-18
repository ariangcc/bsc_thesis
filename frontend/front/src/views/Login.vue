<template>
  <div class="home">
  <div>
    <div class="blue_bar">
      <img class="img-fluid conida mt-3 ml-4" src="@/images/CONIDA.png" alt="">
    </div>

    <h3 id="titulo" class="text-center pt-5 mt-3">Plataforma de visualización de imágenes satelitales</h3>
    <div class="box pt-4 mt-1">
      <form id="form_login" class=" pt-2 mt-3 text-center" @submit.prevent='login'>
        <h3 class="text-center pt-3 mt-3">Acceso al sistema</h3>
        <div>
          <input type="text" class="form-control mb-2 mt-2" placeholder="Usuario"
          v-model.trim="$v.userr.$model" :class="{
          'is-invalid' : $v.userr.$error, 'is-valid' : !$v.userr.$invalid }">
          <div class="valid-feedback">Usuario Válido</div>
          <div class="invalid-feedback">
            <span v-if="!$v.userr.required">Usuario Requerido</span>
            <span v-if="!$v.userr.email">Formato Inadecuado </span>
          </div>
        </div>
        <div class="input-group-addon" id="show_hide_password">
          <input type="password" class="form-control" v-model="user.password" placeholder="Contraseña"
          v-model.trim="$v.password.$model" :class="{
          'is-invalid' : $v.password.$error, 'is-valid' : !$v.password.$invalid }">
          <div class="invalid-feedback">
            <span v-if="!$v.password.required">Contraseña Requerida</span>
          </div>
           <b href=""><i class="fa fa-eye-slash" aria-hidden="true"></i></b>
        </div>
        <div>
          <button type="submit" class="mt-2 text-white btn">Iniciar Sesión</button>
        </div>     
      </form>
      
    </div>

    <footer id="footer">
      <h6 class="text-right pt-2 pr-4">Agencia Espacial del Perú - 2020</h6>
    </footer>
  </div>
  </div>
</template>

<script>
    import {mapState, mapActions} from 'vuex'
    import Swal from 'sweetalert2'
    import * as UserDA from '@/dataAccess/userDA.js'
    import axios from 'axios';
    import { required, email } from 'vuelidate/lib/validators';
    
    $(document).ready(function() {
    $("#show_hide_password b").on('click', function(event) {
        event.preventDefault();
        if($('#show_hide_password input').attr("type") == "text"){
            $('#show_hide_password input').attr('type', 'password');
            $('#show_hide_password i').addClass( "fa-eye-slash" );
            $('#show_hide_password i').removeClass( "fa-eye" );
        }else if($('#show_hide_password input').attr("type") == "password"){
            $('#show_hide_password input').attr('type', 'text');
            $('#show_hide_password i').removeClass( "fa-eye-slash" );
            $('#show_hide_password i').addClass( "fa-eye" );
            }
        });
    });
    export default {
      name: 'Login',
      data(){
        return {
          userr : 'cbeltran',
          password : 'ternaus2020'
        }
      },
      validations: {
        userr: {
          required
        },
        password: {
          required
        }
      },
      computed:{
        ...mapState(['user','token'])
      },
      mounted() {
      },
      methods:{
          ...mapActions(['setToken','setAdmin']),
          login(){
              this.$v.$touch();
              if (this.$v.$invalid) {
              } else {
              UserDA.doLogin(this.user.username, this.user.password).then((res) =>{
                console.log(this.user.username);
                console.log(this.user.password);
                this.$router.push('/mapa');
            }).catch(error =>{
              this.$router.push('/mapa')
              /*
              Swal.fire({
                title: 'Error',
                type: 'error',
                text: 'Usuario y/o contraseña incorrectos'
              })
              */
            })
            }
          }
    },
    updated(){
      this.user.username = this.userr;
      this.user.password = this.password;
    }
} 
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
input{
  border-radius: 6px;
  text-indent: 4%;
  padding-bottom: 0.3em;
  font-size: 15px;
  font-weight: 350; 
  width: 30vh;
  height: 5vh;
  margin: auto;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #343F4B;
  font-weight: 400;
  font-size: 12px;
  margin-left: auto;
  margin-right: auto;
  padding-right: 10px;
}
button{
  background-color: #090d4d;
  font-weight: 600;  
  width: 30vh;
}
h3{
  font-weight: bold;
  font-size: 25px;
  color : #47525E;
}
h6{
  font-family:'Montserrat';
  font-weight: normal;
  font-size: 15px;
  color : #FFFFFF;
}
button:hover{
  background-color: #b20004;
  opacity : 0.80;
}
.box{
  height: 50vh;
  width: 60vh;
  margin: auto;
}
.conida{
  width: 25%;
  height: auto;
}
.blue_bar{
  background-color: #1B3059;
  width: 100%;
  height: 15vh;
  position: relative;
}
#titulo{
  font-family: 'Montserrat';
}
#form_login{
  background-color: #ECF3F1;
  font-family: 'Montserrat';
  height: 38vh;
}
#footer{
  position: fixed;
  left : 0;
  bottom: 0;
  width: 100%;
  background-color: #1B3059;
  height: 5vh;
}
</style>