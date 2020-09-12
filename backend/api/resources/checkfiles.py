from flask_restful import Resource
from flask import request, jsonify, render_template, send_file
import status, json
import os, sys

UPLOAD_DIRECTORY = "results/"

class checkFileResource(Resource):
    def post(self):
        '''Verifica si existe una máscara ya procesada y almacenada con el nombre brindado.'''

        if 'name' not in request.args:
           response = {'error': 'No filename given'}
           return response, status.HTTP_400_BAD_REQUEST

        filename = request.args['name'][:request.args['name'].find('.')] + '_MASK.TIF'
        # Como las máscaras se almadenan con el sufijo _MASK, de existir la máscara ya procesada, estaría con el nombre original + el sufijo

        preprocessed_masks = os.listdir(UPLOAD_DIRECTORY)
        isLocated = (filename in preprocessed_masks)
        
        response = {'isLocated': isLocated, 'filename': ((UPLOAD_DIRECTORY + filename) if isLocated else ' ')}

        return response, status.HTTP_200_OK