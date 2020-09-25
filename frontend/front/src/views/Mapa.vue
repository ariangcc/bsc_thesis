<template>
    <div class="cont">

        <div class="row"> 
            <div class="col-right">
                <div id="map" class="map"></div>
            </div> 

            <div class="col-left">
                <div class="info-box">
                    <img class="conida" src="@/images/CONIDA_LOGO.png" alt="Isotipo Conida"></img>
                    <p id="info-text"> Descarga de máscaras e imágenes </p>
                    <p id="info-text2"> Por favor, realice la búsqueda y selección de alguna imagen debajo</p>
                    <button id="btn3" class="text-white btn3" v-on:click="downloadTIFMask()">Descargar Máscara (TIF)</button>
                    <button id="btn4" class="text-white btn4" v-on:click="downloadPNGMask()">Descargar Máscara (PNG)</button>
                    <button id="btn6" class="text-white btn6" v-on:click="downloadPNGImg()">Descargar Imagen (PNG)</button>
		            <button id="btn5" class="text-white btn5" v-on:click="downloadTIFImg()">Descargar Imagen (TIF)</button>
                </div>
                <hr>

                <div class="loc-title" v-show=ep>
                    <i class="fas fa-map-marker-alt"></i>
                    Área de interés (AOI)
                </div>
                
                <div class="loc-form" v-show=ep>
                    <div class="txt-sup">Superior(N/W):
                        <input type="text" id="top" class="sup-x" v-on:change=drawRecFromLL> <input type="text" id="right" class="sup-y" v-on:change=drawRecFromLL>
                    </div>
                    <div class="txt-inf">Inferior(S/E):
                        <input type="text" id="bottom" class="inf-x"> <input type="text" id="left" class="inf-y">
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
                        <input type="date" id="end-date" class="date-field-inf">
                    </div>
                </div>
                <button id="search-btn" class="text-white btn" v-show=ep v-on:click=searchImagesByDateAndPosition>Buscar</button>
                <div class="loader" v-show=flag_Espera></div>
                <div class="loc-title" v-show=ep2>
                    <i class="fas fa-image img-icon" style="color:red"></i>
                    Selección de Imágenes
                </div>
                <div class="img-form mt-5 ml-5" v-show=ep2>
                    <table id="img-table">
                        <thead class="table-header">
                            <tr>
                                <th class="Nombre" style="word-wrap: break-word width:120px">Nombre de archivo</th>
                                <th class="Fecha" style="word-wrap: break-word width:120px">Fecha Adq.</th>
                            </tr>	
                        </thead>
                        <tbody id='t_Body'></tbody>

                    </table>
                </div>
                <div v-show=ep2>
                    <button class="text-white btn1" v-on:click=selectRaster>Seleccionar</button>
                    <button class="text-white btn2" v-on:click=returnToFirst>Regresar</button>
                </div>
            </div> 
        </div>

        <footer id="footer">
        <h6 class="text-right pt-2 pr-4">Agencia Espacial del Perú - 2020</h6>
        </footer>
        <button id="help-button"></button>
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
                flag_Espera: false,
                ep2: false,
                imageDict: {},
                pathDict: {},
                rectangle: null,
                sRight: -85,
                sBottom: -19,
                sLeft:  -68.5,
                sTop: 0,
            }
        },

        mounted() {
            this.initMap();
            this.disableButtons();
        },

        methods: {
            downloadTIFMask(){
                var anchor = document.createElement('a');
                anchor.href = "http://localhost:9997" + this.imageData.mask.tif_filename;
                anchor.target = '_blank';
                anchor.download = this.selectedImage.path;
                anchor.click();
            },
            downloadTIFImg(){
                var anchor = document.createElement('a');
                anchor.href = "http://cof.cnois.gob.pe/customer-office/net.eads.astrium.faceo.HomePage/HomePageLogin.jsp?locale=es";
                anchor.target = '_blank';
                anchor.click();
            },
            downloadPNGMask(){
                
                var anchor = document.createElement('a');
                anchor.href = "http://localhost:9997" + this.imageData.mask.png_mask;
                anchor.target = '_blank';
                anchor.download = this.selectedImage.path;
                anchor.click();
            },
            downloadPNGImg(){
                var anchor = document.createElement('a');
                anchor.href = "http://localhost:9997" + this.imageData.mask.png_raster;
                anchor.target = '_blank';
                anchor.download = this.selectedImage.path;
                anchor.click();
            },
            disableFirstScreen(){
                this.disableButtons();
                document.getElementById("top").disabled = true;
                document.getElementById("bottom").disabled = true;
                document.getElementById("left").disabled = true;
                document.getElementById("right").disabled = true;
                document.getElementById("start-date").disabled = true;
                document.getElementById("end-date").disabled = true;

                document.getElementById("search-btn").disabled = true;
            },
            enableFirstScreen(){
                this.ep = true;
                document.getElementById("top").disabled = false;
                document.getElementById("bottom").disabled = false;
                document.getElementById("left").disabled = false;
                document.getElementById("right").disabled = false;
                document.getElementById("start-date").disabled = false;
                document.getElementById("end-date").disabled = false;
                document.getElementById("search-btn").disabled = false;
            },
            disableButtons(){
                document.getElementById("btn3").disabled = true;
                document.getElementById("btn4").disabled = true;
                document.getElementById("btn5").disabled = true;
                document.getElementById("btn6").disabled = true;
            },
            enableButtons(){
                document.getElementById("btn3").disabled = false;
                document.getElementById("btn4").disabled = false;
                document.getElementById("btn5").disabled = false; 
                document.getElementById("btn6").disabled = false; 
            },
            initMap() {
                var mymap = L.map('map').setView([-12.065,	-77.035], 5);
                //this.map = L.map('map').setView([-15.391735740879676, -69.65893791338345], 11);
                this.tileLayer = L.tileLayer(
                    'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                    {
                        minZoom: 5,
                        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
                        }
                    );
                    
                this.tileLayer.addTo(mymap);

                L.control.scale().addTo(mymap);

                mymap.on('click', this.onMapClick);
                this.map = mymap;
                this.free = 0;

                document.getElementById("start-date").value = "2000-01-01";
                document.getElementById("end-date").value = "2020-01-01";
            },

            onMapClick(e){
                let top = e.latlng.lat + 1;
                let bottom = e.latlng.lat - 1;
                let right = e.latlng.lng + 1;
                let left = e.latlng.lng - 1;
                this.cleanRect();
                this.free = 1;
                let bounds = [[top, right], [bottom, left]];
                document.getElementById("top").value = top.toString();
                document.getElementById("bottom").value = bottom.toString();
                document.getElementById("left").value = right.toString();
                document.getElementById("right").value = left.toString();
                this.addAOI(bounds);
            },

            removeLayers(){
                this.layers.forEach((object, index) =>{
                    this.map.removeLayer(object);  
                });
                this.layers = [];
            },

            insertLayer(url, imageBounds, options) {
                var overlay = L.imageOverlay(url, imageBounds, options);
                this.layers.push(overlay);
                overlay.addTo(this.map);
            },

            returnToFirst(){
                this.ep2 = false;
                this.ep = true;
                this.free = 1;
                this.cleanRect();
                this.enableFirstScreen();
            },

            drawRecFromLL(){
                console.log("entra")
                let top = parseFloat(document.getElementById("top").value);
                let bottom = parseFloat(document.getElementById("bottom").value);
                let left = parseFloat(document.getElementById("left").value);
                let right = parseFloat(document.getElementById("right").value);
                console.log(top)
                console.log(bottom)

                top = (top && (top > bottom)) ? top : this.sTop
                bottom = (bottom && (top > bottom)) ? bottom : this.sBottom
                left = (left && (left > right)) ? left : this.sLeft
                right = (right && (left > right)) ? right : this.sRight

                document.getElementById("top").value = top
                document.getElementById("bottom").value = bottom
                document.getElementById("left").value = left
                document.getElementById("right").value = right

                if (!(this.rectangle === null)){
                    this.map.removeLayer(this.rectangle);
                }

                

                let bounds = [[top, left], [bottom, right]]
                console.log(bounds)
                this.rectangle = L.rectangle(bounds)
                this.map.addLayer(this.rectangle)
                this.free = 1;
            },

            selectRaster() {
                this.free = 1;
                this.cleanRect();
                this.disableButtons();
                this.ep2 = false;
                let options = {opacity: 0.7};
                this.removeLayers();
                
                document.getElementById("info-text2").innerHTML = this.selectedImage.name;

                ImageDA.doCheckFiles(this.selectedImage.path).then((res) =>{
                    console.log(res.data);
                    this.flag_Espera = true;
                    if(res.data["is_located"]){
                        this.imageData = res.data;
                        console.log(this.imageData);

                        let urlMask = this.imageData.mask.png_mask;
                        let urlImg = this.imageData.mask.png_raster;
                        let top = parseFloat(this.imageData.mask.bounding_box.top);
                        let bottom = parseFloat(this.imageData.mask.bounding_box.bottom);
                        let left = parseFloat(this.imageData.mask.bounding_box.left);
                        let right = parseFloat(this.imageData.mask.bounding_box.right);
                        
                        options.opacity = 1.0;
                        this.insertLayer("http://localhost:9997" + urlImg, [[right, bottom], [left, top]], options);
                        options.opacity = 0.4;
                        this.insertLayer("http://localhost:9997" + urlMask, [[right, bottom], [left, top]], options);
                        this.map.setView([(right + left) * 0.5, (bottom + top) * 0.5], 12);
                        this.enableButtons();
                        this.enableFirstScreen();
                        this.flag_Espera = false;
                    }
                    else{
                        ImageDA.doPredict(this.selectedImage.path).then((res2) =>{
                            this.imageData = res2.data;
                            console.log(this.imageData);

                            let urlMask = this.imageData.mask.png_mask;
                            let urlImg = this.imageData.mask.png_raster;
                            let top = parseFloat(this.imageData.mask.bounding_box.top);
                            let bottom = parseFloat(this.imageData.mask.bounding_box.bottom);
                            let left = parseFloat(this.imageData.mask.bounding_box.left);
                            let right = parseFloat(this.imageData.mask.bounding_box.right);
                            
                            options.opacity = 1.0;
                            this.insertLayer("http://localhost:9997" + urlImg, [[right, bottom], [left, top]], options);
                            options.opacity = 0.4;
                            this.insertLayer("http://localhost:9997" + urlMask, [[right, bottom], [left, top]], options);
                            this.map.setView([(right + left) * 0.5, (bottom + top) * 0.5], 12);
                            this.enableButtons();
                            this.enableFirstScreen();
                            this.flag_Espera = false;
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

            addAOI(bounds){
                console.log("Adding AOI");
                if(this.free == 1){
                    this.rectangle = L.rectangle(bounds)
                    console.log(this.rectangle)
                    this.map.addLayer(this.rectangle)
                }
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
                    let bounds = [[bb.right, bb.bottom],[bb.left, bb.top]]
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
                this.selectedImage.name = element.id;
                this.free = 0;
                element.style.backgroundColor = "green";
                this.prevSelected = element;
            },

            searchImagesByDateAndPosition() {
                //Disable all element on first screen
                this.disableFirstScreen();
                // Coordinates
                this.cleanRect();
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
                this.ep = false;
                this.flag_Espera =true;
                ImageDA.doSearchImages(top, bottom, left, right, startDate, endDate).then((res) => {
                    this.flag_Espera =false;
                    console.log(res.data);
                    console.log("Lista encontrada!");
                    this.append_json(res.data)
                    this.ep2 = true;
                }).catch(error =>{
                    console.log(error)
                    Swal.fire({
                        title: 'Error',
                        type: 'error',
                        text: 'Error en searchImages'
                    })
                    this.flag_Espera =false;
                    this.ep = true;
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
    // document.getElementById('end-date').value = new Date().toDateInputValue();

	// document.addEventListener('DOMContentLoaded', () => {
    //     let resizer = new ResizeObserver(handleResize);
    //     resizer.observe(document.querySelector('.col-left'));
    // });

    // function handleResize(entries) {
    //     console.log('resize called');
    //     let div = entries[0].target;
    //     if(entries[0].contentRect.width < 250){
    //         div.classList.add('small');
    //     }
    //     else{
    //         div.classList.remove('small');
    //     }
        
    // }

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
    
    .col-right{
        position: fixed;
        float:right;
        top: 0; 
        bottom: 5vh; 
        left: 550px; 
        right: 0; 
    }
    #map {
        position: relative;
        height: 100%;
        width: 100%; 
    }

    .col-left{
        position: fixed;
        height: 95%; 
        width:550px; 
        top: 0; 
        bottom: 5vh; 
        left: 0; 
        right: 0; 
        background-color: white;
	overflow: auto;
    }
    

    .col-left.small {
        background-color: rebeccapurple;
        width: 300px;
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
        background-color:#E0E0E0;
        border-radius: 10%;
        padding: 20px; 
        width: 90%;
        height: 350px;
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
        margin-bottom:0.5%;
    }
    
    .loc-form{
        border-radius: 25px;
        border: 1px solid #929292;
        width: 90%;
        height: 101.98px; 
        /* margin-left: 19px;
        margin-top: 8%; */
        margin:auto;
        margin-top: 8%;
    }
    .txt-sup{
        margin-top: 3%;
        margin-left:5%;
    }
    .txt-inf{
        margin-top: 3%;
        margin-left: 5%;
    }
    .sup-x{
        width: 25%;
        margin-left:7%;
    }
    .sup-y{
        margin-left:2%;
        width: 25%;
    }
    .inf-x{
        width: 25%;
        margin-left:10%;
    }
    .inf-y{
        margin-left:2%;
        width: 25%;
    }

    
    .time-title{
        font-size: 100%;
        font-family: 'Montserrat';
        position: absolute;
        background-color: #FFFFFF;
        margin-left: 13%;
        margin-top:4.5%;
        margin-bottom:0.5%;
    }
    .time-form{
        border-radius: 25px;
        border: 1px solid #929292;
        width: 90%;
        height: 101.98px; 
        margin:auto;
	margin-top: 8%; 
	margin-bottom: 7px;
    }
    .date-field{
        margin-left:50px;
        width: 50%;
    }
    .date-field-inf{
        margin-left:55px;
        width: 50%;
    }



    #table{ 
		border-collapse: collapse;
        table-layout: fixed;
	}

	td, th{
		border: 1px solid;
        /* width: 20px; */
		padding: 8px;
        /* width:20px; */
	}
	th{
        border-color: transparent black;
		font-weight: bold;
        background-color: #C0C0C0;
        font-size: 90%;
	}
    th:first-child{
		border-color: transparent black transparent transparent;
        border-radius:25px 0 0  0px;
        width: 354px;
	} 
	th:last-child{
		border-color: transparent transparent transparent black;
		border-radius:0px 25px 0  0px;
        width: 83px;
	}
	tr:hover{
        border-color: transparent;
		background-color: black;
		color:white
	}
	tbody{
			border-collapse: collapse;
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
        width: 440px;
        height: 40%;
        border-radius: 25px;
        overflow:auto;
        table-layout: fixed;
    }
    
    button{
        background-color: #090d4d;
        font-weight: 600;  
        width: 30%;
        margin-left: 35%;
    }
    button:hover{
        background-color: #b20004;
        opacity : 0.750;
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
    .btn3, .btn6{
        border-radius: 8px;
        border: 0px solid;
        margin-top:2%;
        margin-left: 0px;
        margin-right: 20px;
	height: 50px;
        width: 200px;
        font-family: 'Montserrat';
        font-weight: bold;   
    }
    .btn4, .btn5{
        border-radius: 8px;
        border: 0px solid;
        margin-top:2%;
        margin-left: 0px;
        margin-right: 20px;
	height: 50px;
        width: 200px;
        font-family: 'Montserrat';
        font-weight: bold;   
    }
    button:disabled{
        background-color: #a0a0a0;
    }

    .btn1:hover{
        background-color: #c0c0c0;
    }
    .btn2:hover{
        background-color: #c0c0c0;
    }
    .text-right{
        color:#CCCCCC;
        font-family: 'Montserrat';
        
    }

    #info-text, #info-text2{
        position: relative;
        text-align: center;
        color: #000000;
    }
      
    #footer{
        position: fixed;
        left : 0;
        bottom: 0;
        width: 100%;
        background-color: #1B3059;
        height: 5vh;
    }
    
    .help-button{
        width: 5px;
        height: 5px;
        position:absolute;
        margin:0;
        z-index: 10;
        /* left:90vw;
        bottom:90vh; */
        /* border-radius: 10px;
        -moz-border-radius: 10px;
        -webkit-border-radius: 10px; */
    }
    .loader {
        position: relative;
        border: 16px solid #f3f3f3; /* Light grey */
        border-top: 16px solid #090d4d; /* Blue */
        border-radius: 50%;
        width: 120px;
        height: 120px;
        animation: spin 2s linear infinite;
        margin-top:auto;
        margin-left:auto;
        margin-right:auto;
        margin-bottom:auto;
    }


    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
