import os
from resources.utils.transformsdata import CenterCrop, DualCompose, ImageOnly, Normalize, Normalize2
from torch.autograd import Variable
from rasterio import windows
from io import BytesIO
from rasterio.io import MemoryFile
import rasterio as rio
from itertools import product
import numpy as np
import torch
from resources.utils.dataset import to_float_tensor
from datetime import datetime
import progressbar

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
UPLOAD_DIRECTORY = "results/"

def transform_function():
        '''Función de normalización para una imagen satelital.'''
        image_transform = DualCompose([CenterCrop(512), ImageOnly(Normalize(mean=[0.11555246, 0.10432396, 0.1150794,  0.14246734], std=[0.08946183, 0.06699049, 0.05742599, 0.11001556]))])
        return image_transform

def preprocess_image(img):
    '''Normaliza y transforma la imagen en un tensor apto para ser procesado por la red neuronal de segmentación de cuerpos de agua.
    Dimensiones:
    entrada: (4,512,512);
    salida: (1,4,512,512)
    '''
    img=img.transpose((1, 2, 0))
    image_transform = transform_function()
    img_for_model = image_transform(img)[0]
    img_for_model = Variable(to_float_tensor(img_for_model),requires_grad=False)
    img_for_model = img_for_model.unsqueeze(0).to(device)

    return img_for_model

def create_patches(dataset):
    '''Genera bloques de (4,512,512) píxeles a partir de una imagen satelital.
    Argumentos:
    dataset: lector de conjunto de datos ráster
    '''
    coordinates='{}-{},{}-{}'
    patches = []

    def get_tiles(ds, width=512, height=512):
        nols, nrows = ds.meta['width'], ds.meta['height']
        offsets = product(range(0, nols, width), range(0, nrows, height))
        big_window = windows.Window(col_off=0, row_off=0, width=nols, height=nrows)

        idx = 0
        # La barra se muestra así [=========         ] X%

        for col_off, row_off in  offsets:
            window =windows.Window(col_off=col_off, row_off=row_off, width=width, height=height).intersection(big_window)
            transform = windows.transform(window, ds.transform)  #split

            idx += 1

            yield window, transform

    meta = None
    with dataset as inds:
        tile_width, tile_height = 512, 512
        meta = inds.meta.copy()

        for window, transform in get_tiles(inds):
            if((int(window.width)==512) and (int(window.height)==512)):  
                array=inds.read(window=window)
                patches.append(array)
    return patches, meta

def reconstruct_image(masks, metadata, img_shape, filename):
    '''Combina un conjunto de bloques de (4,512,512) píxeles para generar una máscara de segmentación de cuerpos de agua y guarda el resultado localmente.

    Argumentos:
    masks: lista de máscaras - arrays -  de (4,512,512) píxeles;
    metadata: diccionario con los metadatos de la imagen satelital original;
    img_shape: dimensiones de la imagen satelital original;
    filename: nombre del archivo que contenía a la imagen original
    '''
    pos = 0
    #C, H, W
    mask = np.zeros(shape=(1, img_shape[1], img_shape[2]))
    # rows = floor(H / 512), cols = floor(W / 512)

    for j in range(img_shape[2] // 512):
        for i in range(img_shape[1] // 512):
            #print(pos)
            cur_mask = masks[pos,0,:,:,:]
            for k in range(512):
                for l in range(512):
                    mask[0, i * 512 + k, j * 512 + l] = cur_mask[0,k,l]
            pos += 1
    
    h, w = mask.shape[1], mask.shape[2]
    binary_mask = np.zeros(shape=mask.shape, dtype=np.uint8)
    for y in range(mask.shape[1]):
        for x in range(mask.shape[2]):
            binary_mask[0,y,x] = (mask[0,y,x] > 0.5)
    mask = binary_mask
    h, w = mask.shape[1], mask.shape[2]
    
    metadata['count'] = 1
    metadata['height'] = mask.shape[1]
    metadata['width'] = mask.shape[2]
    metadata['dtype'] = mask.dtype
    now = datetime.now()
    filename = filename[:filename.find('.')]
    mask_filename = filename + "_MASK.TIF"
    with rio.open(os.path.join(UPLOAD_DIRECTORY, mask_filename), 'w', **metadata) as outds:
        outds.write(mask)
    
    return mask_filename

