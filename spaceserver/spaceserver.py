from flask import Flask, jsonify
import math
import random
import requests
from PIL import Image
import tempfile
import io
import numpy as np

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/user/<uid>')
def get_user(uid):
    return jsonify({
        'user_name': 'spaceapps',
        'uid': uid,
        'maps': ['map_id1']
    })

@app.route('/map/<mid>')
def get_map(mid):
    return jsonify({
        'mid': mid,
        'layers': ['layer_id1']
    })

@app.route('/map/<mid>/layer/<lid>')
def get_layer(mid, lid):
    return jsonify({
        'lid': lid,
        'layer_name': 'Air Quality',
        'source': 'some API'
    })

@app.route('/map/<mid>/pi')
def get_pi_image(mid):
    get_image()
    return None # pi_image

@app.route('/map/<mid>/stl')
def get_map_stl(mid):
    return None # stl

@app.route('/map/<mid>/data')
def get_map_data(mid):
    return jsonify({
        'pixel_data': get_image()
    })


def get_image():
    
    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    r = requests.get('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Aerosol/default/2014-04-09/GoogleMapsCompatible_Level6/1/1/1.png')
    if r.status_code == 200:
        downloaded = 0
        filesize = int(r.headers['content-length'])
        print('download started')
        for chunk in r.iter_content():
            downloaded += len(chunk)
            buffer.write(chunk)
        print('download done')
        buffer.seek(0)
        i = Image.open(io.BytesIO(buffer.read()))
        print(i.mode)
        print(i.size)
        pic = np.array(i)
        print(pic.size)
    return [
        [
            [int(pic[i, j]), int(pic[i, j]), int(pic[i, j])] for i in range(32)
        ] for j in range(32)
    ]

@app.route('/layers')
def get_layer_list():
    return jsonify([
        {
            'lid': 'layer_id1',
            'layer_name': 'Air Quality',
            'source': 'https://google.com/'
        }
    ])