from flask_restful import Resource
from flask import request, jsonify, render_template, send_file
from PIL import Image
from datetime import datetime
import status, json
import base64
from resources.utils.image_utils import create_patches, reconstruct_image
from resources.utils.segmenter import WaterSegmentation
import numpy as np
import os
from rasterio.io import MemoryFile
import random, time

UPLOAD_DIRECTORY = "results/"
MODEL_PATH = 'models/model_40epoch_100_percent_UNet11_fold0.pth'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

model = WaterSegmentation(MODEL_PATH)
ALLOWED_EXTENSIONS = {'tif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class PredictResource(Resource):
    def post(self):
        start = time.time()
        print("Recibiendo imagen...")
        if 'file' not in request.files:
            response = {'error': 'No file part'}
            return response, status.HTTP_400_BAD_REQUEST
        file = request.files['file']
        data = file.read()
        reading = time.time()
        print("Imagen recibida, tiempo transcurrido: {}s".format(str(round(reading - start, 2))))
        print("Abriendo la imagen...")
        memfile = MemoryFile(data)
        dataset = memfile.open()
        img_npy = dataset.read()
        opening = time.time()
        print("Imagen abierta, tiempo transcurrido: {}s".format(str(round(opening - reading, 2))))
        print("Dimensiones de la imagen: {}".format(str(img_npy.shape)))
        print("Minimo: {} | Maximo: {}".format(str(img_npy.min()), str(img_npy.max())))
        #print(img_npy.max(), img_npy.min(), img_npy.mean(), img_npy.std())
        print("Creando bloques de 4 x 512 x 512...")
        patches, meta = create_patches(dataset)
        splitting = time.time()
        print("Bloques de 4 x 512 x 512 creados, tiempo transcurrido: {}s".format(str(round(splitting - opening, 2))))
        masks = []
        randpos = random.randint(0, len(patches) - 1)
        idx = 0
        print("Obteniendo las máscaras por cada bloque...")
        for patch in patches:
            prediction = model.predict(patch, (randpos == idx))
            masks.append(prediction.data.cpu().numpy())
            #print(masks[len(masks) - 1].max(), masks[len(masks) - 1].min())
            idx += 1
            print("Numero de bloques procesados: {}/{}".format(str(idx), str(len(patches))))
            #print(len(masks))
        predicting = time.time()
        print("Mascaras obtenidas! Tiempo transcurrido: {}s".format(str(round(predicting - splitting, 2))))
        masks = np.asarray(masks)
        #print(masks.shape)
        print("Construyendo la mascara final + metadata...")
        mask_filename = reconstruct_image(masks, meta, img_npy.shape)
        mask_file = open(os.path.join(UPLOAD_DIRECTORY, mask_filename), 'rb')
        constructing = time.time()
        print("Mascara construida! Tiempo transcurrido: {}s".format(str(round(constructing - predicting, 2))))
        end = time.time()
        img_encoded = base64.b64encode(mask_file.read()).decode('utf-8')
        response = {'mask' : img_encoded}
        print("Tiempo total: {}s".format(str(round(end - start, 2))))
        return response, status.HTTP_200_OK
