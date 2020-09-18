<template>
    <div class="cont">

        <div class="row"> 
            <div class="col-right">
                <div id="map" class="map"></div>
            </div> 

            
            

            <div class="col-left">
                <div class="info-box">
                    <img class="conida" src="@/images/CONIDA.png" alt="Isotipo Conida">
                    <p id = "info-text">
                        Lorem ipsum dolor sit amet, 
                    </p>
                </div>
                <hr>

                <div class="loc-title" v-show=ep>
                    <i class="fas fa-map-marker-alt"></i>
                    Área de interés (AOI)
                </div>
                
                <div class="loc-form" v-show=ep>
                    <div class="txt-sup">Superior(N/W):
                        <input type="text" id="top" class="sup-x"> <input type="text" id="left" class="sup-y">
                    </div>
                    <div class="txt-inf">Inferior(S/E):
                        <input type="text" id="bottom" class="sup-x"> <input type="text" id="right" class="sup-y">
                    </div>
                </div>
                <div class="time-title" v-show=ep>
                    <i class="fas fa-clock"></i>
                    Período de Adquisición
                </div>
                
                <div class="time-form" v-show=ep>
                    <div class="txt-sup">Fecha Inicial:
                        <input type="date" id="start-date" class="date-field">
                    </div>
                    <div class="txt-inf">Fecha Final:
                        <input type="date" id="end-date" class="date-field">
                    </div>
                </div>
                <button class="text-white btn" v-show=ep v-on:click=searchImagesByDateAndPosition>Buscar</button>

                <div class="loc-title" v-show=!ep>
                    <i class="fas fa-image img-icon" style="color:red"></i>
                    Selección de Imágenes
                </div>
                <div class="img-form mt-5 ml-5" v-show=!ep>
                    <table id="img-table">
                        <thead class="table-header">
                            <tr>
                                <th class="Nombre" style="word-wrap: break-word">Nombre de archivo</th>
                                <th class="Fecha">Fecha Adq.</th>
                            </tr>	
                        </thead>
                        <tbody id='t_Body'></tbody>

                    </table>
                </div>
                <div v-show=!ep>
                    <button class="text-white btn1" v-on:click=selectRaster>Seleccionar</button>
                    <button class="text-white btn2" v-on:click=returnToFirst>Regresar</button>
                </div>
            </div>

            
        </div>

        <footer id="footer">
        <h6 class="text-right pt-2 pr-4">Agencia Espacial del Perú - 2020</h6>
        </footer>
        
    </div>
</template>

<script>

    import L from 'leaflet';
    import axios from 'axios';
    import * as ImageDA from '@/dataAccess/imageDA.js';
    global.jQuery = require('jquery');
    var $ = global.jQuery;

    export default {

        data: function(){
            return {
                map: null,
                selectedImage: {},
                prevSelected: null,
                imageData: null,
                free: 1,
                tileLayer: null,
                layers : [],
                ep: true,
                imageDict: {},
                pathDict: {},
                rectangle: null
            }
        },

        mounted() {
            this.initMap();
            },

        methods: {
            initMap() {
                this.map = L.map('map').setView([-12.065,	-77.035], 5);
                //this.map = L.map('map').setView([-15.391735740879676, -69.65893791338345], 11);
                this.tileLayer = L.tileLayer(
                    'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                    {
                        minZoom: 5,
                        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
                        }
                    );
                    
                this.tileLayer.addTo(this.map);

                L.control.scale().addTo(this.map);
            },

            insertLayer(url, imageBounds, options) {
                L.imageOverlay(url, imageBounds, options).addTo(this.map);
            },

            returnToFirst(){
                this.ep = !this.ep;
                this.free = 1;
                this.cleanRect();
            },

            selectRaster() {
                this.free = 1;
                this.cleanRect();
                this.ep = !this.ep;
                let options = {opacity: 0.7};
                ImageDA.doCheckFiles(this.selectedImage.path).then((res) =>{
                    console.log(res.data)
                    
                    if(res.data["is_located"]){
                        this.imageData = res.data;
                        console.log(this.imageData);

                        let urlMask = this.imageData.mask.png_mask;
                        let top = parseFloat(this.imageData.mask.bounding_box.top);
                        let bottom = parseFloat(this.imageData.mask.bounding_box.bottom);
                        let left = parseFloat(this.imageData.mask.bounding_box.left);
                        let right = parseFloat(this.imageData.mask.bounding_box.right);
                        
                        this.insertLayer("http://localhost:9997" + urlMask, [[left, top], [right, bottom]], options);
                        this.map.setView([(left + right) * 0.5, (top + bottom) * 0.5], 12);
                    }
                    else{
                        ImageDA.doPredict(this.selectedImage.path).then((res2) =>{
                            this.imageData = res2.data;
                            console.log(this.imageData);

                            let urlMask = this.imageData.mask.png_mask;
                            let top = parseFloat(this.imageData.mask.bounding_box.top);
                            let bottom = parseFloat(this.imageData.mask.bounding_box.bottom);
                            let left = parseFloat(this.imageData.mask.bounding_box.left);
                            let right = parseFloat(this.imageData.mask.bounding_box.right);
                            
                            this.insertLayer("http://localhost:9997" + urlMask, [[left, top], [right, bottom]], options);
                            this.map.setView([(left + right) * 0.5, (top + bottom) * 0.5], 12);
                        }).catch(error =>{
                            console.log(error)
                            Swal.fire({
                                title: 'Error',
                                type: 'error',
                                text: 'Error en doPredict'
                            })
                    
                        })
                    }

                    
                }).catch(error =>{
                    console.log(error)
                    Swal.fire({
                        title: 'Error',
                        type: 'error',
                        text: 'Error en checkFiles'
                    })
                    
                })
                
            },

            addRect(element){
                console.log("Entra")
                console.log(element)
                console.log(this.imageDict)
                console.log(element.id)
                console.log(this.free)
                if(this.free == 1){
                    let bb = this.imageDict[element.id];
                    console.log(element.id)
                    console.log(bb)
                    let bounds = [[bb.left, bb.top],[bb.right, bb.bottom]]
                    console.log(bounds)
                    this.rectangle = L.rectangle(bounds)
                    console.log(this.rectangle)
                    this.map.addLayer(this.rectangle)
                }
            },

            cleanRect(){
                if(this.free == 1){
                    this.map.removeLayer(this.rectangle);
                }
            },

            addRectAndCheck(element){
                if(!(this.rectangle === null)){
                    console.log("Borrando")
                    this.map.removeLayer(this.rectangle);
                    this.rectangle = null;
                    this.prevSelected.style.backgroundColor = "white"; 
                }
                this.free = 1;
                console.log("Se puede fijar");
                this.addRect(element);
                this.selectedImage.path = this.pathDict[element.id];
                this.free = 0;
                element.style.backgroundColor = "green";
                this.prevSelected = element;
            },

            searchImagesByDateAndPosition() {
                //document.querySelector(".popup").style.display="flex";
                // Coordinates
                let top = document.getElementById("top").value;
                let bottom = document.getElementById("bottom").value;
                let left = document.getElementById("left").value;
                let right = document.getElementById("right").value;
                //Dates
                let startDate = document.getElementById("start-date").value;
                let endDate = document.getElementById("end-date").value;

                console.log("coordenadas");
                console.log(top);
                console.log(bottom);
                console.log(left);
                console.log(right);

                ImageDA.doSearchImages(top, bottom, left, right, startDate, endDate).then((res) => {
                    console.log(res.data);
                    console.log("Lista encontrada!");
                    this.append_json(res.data)
                    this.ep = !this.ep;
                }).catch(error =>{
                    console.log(error)
                    Swal.fire({
                        title: 'Error',
                        type: 'error',
                        text: 'Error en searchImages'
                    })
                    
                })
            },
            Cerrar_Resultados(){
                document.querySelector(".popup").style.display="none";
            },
            append_json(data){
                var table = document.getElementById("img-table");
                console.log(table);            
                console.log(data);
                while(table.rows.length > 1){
                    table.deleteRow(-1);
                }
                data.images.forEach((object, index) =>{
                    console.log("Agregando registro");
                    this.imageDict[object.name] = object.bounding_box
                    this.pathDict[object.name] = object.path
                });
                data.images.forEach((object, index) => {
                    console.log("Empezando");
                    var tr = document.createElement('tr');
                    tr.setAttribute("id", object.name)
                    console.log("Agregando listener 1");
                    tr.addEventListener("mouseenter", (tr) =>{
                        this.addRect(tr.originalTarget);
                    });
                    console.log("Agregando listener 2");
                    tr.addEventListener("mouseleave", () =>{
                        this.cleanRect();
                    });
                    tr.addEventListener("click", (tr) => {
                        this.addRectAndCheck(tr.originalTarget)
                    });
                    console.log("Agregando innerHTML");
                    tr.innerHTML = '<td style="word-wrap: break-word" v-on:mouseenter="addRect(this)" v-on:mouseleave=cleanRect id="' + object.name + '">' +
                     object.name + '</td>' +
                    '<td v-on:mouseenter="addRect(this)" v-on:mouseleave=cleanRect id="' + object.name + '">' + object.date + '</td>';
                    table.appendChild(tr);
                });
            }
        },
    }

	document.addEventListener('DOMContentLoaded', () => {
        let resizer = new ResizeObserver(handleResize);
        resizer.observe(document.querySelector('.col-left'));
    });

    function handleResize(entries) {
        console.log('resize called');
        let div = entries[0].target;
        if(entries[0].contentRect.width < 250){
            div.classList.add('small');
        }
        else{
            div.classList.remove('small');
        }
        
    }

    //@import 'https://unpkg.com/leaflet@1.2.0/dist/leaflet.css';
</script>

<style scoped>
  @import 'https://unpkg.com/leaflet@1.2.0/dist/leaflet.css';

  hr {
      display: block;
      color: black;
      border-width: 0.25em;
      margin-top: 4em;
      margin-bottom: 0.5em;
      margin-left: 2em;
      margin-right: 2em;
      }
  
  .blue_bar{
      background-color: #1B3059;
      width: 100%;
      height: 15vh;
      position: relative;
      }

  .col-left{
      position: fixed;
      height: 100%;
      width: 25%; 
      top: 0; 
      bottom: 5vh; 
      left: 0; 
      right: 0; 
      background-color: white;
  }
/* 
  .one{
      background-color: cornflowerblue;
      color: white;
  }

  .two{
      background-color: rebeccapurple;
      color: white;
  } */

  .col-left.small {
        background-color: rebeccapurple;
      width: 300px;
    }

/*       
      .col-left.small .one {
        background-color: rebeccapurple;
        width: 300;
      }
      .col-left.small .two {
        background-color: cornflowerblue;
        width: 300;
      } */
      /*.big img {
        width: 100%;
      }*/
  .col-right{
      position: fixed;
      top: 0; 
      bottom: 5vh; 
      left: 25vw; 
      right: 0;
  } 

  .conida{
      position: relative;
      display: block;
      height: 22%;
      width: auto;
      margin-left: auto;
      margin-right: auto;
  }

  .info-box{
      position: relative;
      display: block;
      background-color:#333333;
      border-radius: 10%;
      padding: 20px; 
      width: 90%;
      height: 33%;
      top: 3vh;
      margin-left: auto;
      margin-right: auto;
  }
  
  .loc-title{
      font-size: 100%;
      font-family: 'Montserrat';
      position: absolute;
      background-color: #FFFFFF;
      margin-left: 13%;
      margin-top:2.5%;
    }
    
    .loc-form{
        border-radius: 25px;
        border: 1px solid #929292;
        width: 90%;
        height: 16%; 
        /* margin-left: 19px;
        margin-top: 8%; */
        margin:auto;
        margin-top: 8%;
    }
    .time-title{
        font-size: 100%;
        font-family: 'Montserrat';
        position: absolute;
        background-color: #FFFFFF;
        margin-left: 13%;
        margin-top:2.5%;
    }
    .time-form{
        border-radius: 25px;
        border: 1px solid #929292;
        width: 90%;
        height: 16%; 
        /* margin-left: 19px;
        margin-top: 8%; */
        margin:auto;
        margin-top: 8%;
    }

    #table{
        table-layout:fixed;
        width:20px;
        border-collapse: collapse;
	}
	td, th{
		border: 1px solid;
		padding: 8px;
        width:20px;
	}
	th{
		font-weight: bold;
		text-transform: uppercase;
        background-color: #C0C0C0;
        font-size: 90%;
	}
	tr:nth-child(even){
		background-color: beige;
	}
	tr:hover{
		background-color: black;
		color:white
	}
	tbody{
			border-collapse: collapse;
			width: 100%;
	}
    .img-table{
        margin-left: auto;
        margin-right: auto;
        margin-top: 4vh;
        position: relative;
        background-color: #FFFFFF;
        font-family: 'Montserrat';
    }
    .img-form{
        border: 1px solid;
        width: 80%;
        height: 40%;
        border-radius: 25px;
    }
    
    button{
        background-color: #090d4d;
        font-weight: 600;  
        width: 30%;
        margin-left: 35%;
        margin-top: 6%;
    }
    button:hover{
        background-color: #b20004;
        opacity : 0.750;
    }
    .txt-sup{
        margin-top: 10%;
        margin-left:5%;
    }
    .txt-inf{
        margin-top: 3%;
        margin-left: 9%;
    }
    .sup-x{
        width: 25%;
        margin-left:8%;
    }
    .sup-y{
        margin-left:3%;
        width: 25%;
    }
    .date-field{
        margin-left:8%;
        width: 50%;
    }

    .btn1{
        border-radius: 8px;
        border: 1px solid;
        position: absolute;
        margin-top: 2vh;
        margin-left: 27vh;
        margin-right: auto;
        height: 4%;
        font-family: 'Montserrat';
        font-weight: bold;
        width: 30%;
    }
    .btn2{
        border-radius: 8px;
        border: 1px solid;
        position: absolute;
        margin-top: 2vh;
        margin-left: 10vh;
        margin-right: auto;
        height: 4%;
        width: 25%;
        font-family: 'Montserrat';
        font-weight: bold;
    }
    .btn1:hover{
        background-color: #c0c0c0;
    }
    .btn2:hover{
        background-color: #c0c0c0;
    }

  #info-text{
      position: relative;
      text-align: center;
      color: aliceblue;
  }
      
  #footer{
      position: fixed;
      left : 0;
      bottom: 0;
      width: 100%;
      background-color: #1B3059;
      height: 5vh;
    }

  #map {
      position: relative;
      height: 100%;
      width: 100%; 
      }
</style>
