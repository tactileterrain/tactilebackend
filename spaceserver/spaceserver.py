from flask import Flask, jsonify
import math
import random

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
    return None # pi_image

@app.route('/map/<mid>/stl')
def get_map_stl(mid):
    return None # stl

@app.route('/map/<mid>/data')
def get_map_data(mid):
    return jsonify({
        'pixel_data': [
            [
                [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
                for _ in range(32)
            ]
            for _ in range(32)
        ]
    })


@app.route('/layers')
def get_layer_list():
    return jsonify([
        {
            'lid': 'layer_id1',
            'layer_name': 'Air Quality',
            'source': 'https://google.com/'
        }
    ])