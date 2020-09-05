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

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
UPLOAD_DIRECTORY = "results/"

def transform_function():
	image_transform = DualCompose([
			CenterCrop(512),
			ImageOnly(Normalize(mean=[0.11555246, 0.10432396, 0.1150794,  0.14246734], 
								std=[0.08946183, 0.06699049, 0.05742599, 0.11001556]))
			])
	return image_transform

def preprocess_image(img):
    img=img.transpose((1, 2, 0))
    image_transform = transform_function()
    img_for_model = image_transform(img)[0]
    img_for_model = Variable(to_float_tensor(img_for_model),requires_grad=False)
    img_for_model = img_for_model.unsqueeze(0).to(device)

    return img_for_model

def create_patches(dataset):
    coordinates='{}-{},{}-{}'
    patches = []

    def get_tiles(ds, width=512, height=512):
        nols, nrows = ds.meta['width'], ds.meta['height']
        offsets = product(range(0, nols, width), range(0, nrows, height))
        big_window = windows.Window(col_off=0, row_off=0, width=nols, height=nrows)
        for col_off, row_off in  offsets:
            window =windows.Window(col_off=col_off, row_off=row_off, width=width, height=height).intersection(big_window)
            transform = windows.transform(window, ds.transform)  #split
            yield window, transform

    meta = None
    with dataset as inds:
        tile_width, tile_height = 512, 512
        meta = inds.meta.copy()

        for window, transform in get_tiles(inds):
            if((int(window.width)==512) and (int(window.height)==512)):  
                array=inds.read(window=window)
                patches.append(array)
                #coordinates2= str(coordinates.format(int(window.row_off),int(window.row_off)+int(window.width),int(window.col_off),int(window.col_off)+int(window.height))) 
                #print(coordinates2)
    return patches, meta

def reconstruct_image(masks, metadata, img_shape):
    pos = 0
    #C, H, W
    mask = np.zeros(shape=(1, img_shape[1], img_shape[2]))
    # rows = floor(H / 512), cols = floor(W / 512)
    '''
        xxxxxxxxxxxxx
        xxxxxxxxxxxxx
        xxxxxxxxxxxxx
        xxxxxxxxxxxxx
        xxxxxxxxxxxxx
        xxxxxxxxxxxxx
    '''

    for j in range(img_shape[2] // 512):
        for i in range(img_shape[1] // 512):
            #print(pos)
            cur_mask = masks[pos,0,:,:,:]
            for k in range(512):
                for l in range(512):
                    mask[0, i * 512 + k, j * 512 + l] = cur_mask[0,k,l]
            pos += 1
    
    #print(mask.shape)
    h, w = mask.shape[1], mask.shape[2]
    #print(mask[0, h//2 -8 : h//2 +8 , w // 2 - 8 : w // 2 + 8])
    #print(mask.max(), mask.min())
    binary_mask = np.zeros(shape=mask.shape, dtype=np.uint8)
    for y in range(mask.shape[1]):
        for x in range(mask.shape[2]):
            binary_mask[0,y,x] = (mask[0,y,x] > 0.5)
    mask = binary_mask
    #print(mask.shape)
    h, w = mask.shape[1], mask.shape[2]
    #print(mask[0, h//2 -8 : h//2 +8 , w // 2 - 8 : w // 2 + 8])
    
    metadata['count'] = 1
    metadata['height'] = mask.shape[1]
    metadata['width'] = mask.shape[2]
    metadata['dtype'] = mask.dtype
    now = datetime.now()
    filename = "IMG"
    #filename = "IMG_{}".format(now.strftime('%Y%m%d%H%M%S'))
    mask_filename = filename + "_MASK.TIF"
    with rio.open(os.path.join(UPLOAD_DIRECTORY, mask_filename), 'w', **metadata) as outds:
        outds.write(mask)
    
    return mask_filename

