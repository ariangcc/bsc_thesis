import json
import numpy as np

from PIL import Image
from io import BytesIO
import rasterio as rio
import os
UPLOAD_DIRECTORY = 'results/'

import resources.utils.model_utils as model_utils

from resources.utils.image_utils import preprocess_image

class WaterSegmentation(object):
    def __init__(self,model_path):
        self.model = model_utils.load_model(model_path)

    def image_loader(self, img):
        img = preprocess_image(img)
        return img

    def predict(self, image, save_flag):
        # patch_meta = {}
        # patch_meta['width'] = 512
        # patch_meta['height'] = 512
        # patch_meta['dtype'] = np.uint16
        # patch_meta['driver'] = 'GTiff'
        # patch_meta['count'] = 4
        # if save_flag:
        #     with rio.open(os.path.join(UPLOAD_DIRECTORY, 'patch.TIF'), 'w', **patch_meta) as outds:
        #         outds.write(image)
        
        img_input = self.image_loader(image)
        #print(img_input.shape, img_input.max(), img_input.min())
        trained_model = self.model
        response = model_utils.run_model(img_input,trained_model)
       	del trained_model
        return response
