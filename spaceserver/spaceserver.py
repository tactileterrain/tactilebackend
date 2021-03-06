from flask import Flask, jsonify
import math
import random
import requests
from PIL import Image
import tempfile
import io
import numpy as np
from collections import namedtuple
import datetime

app = Flask(__name__)


LatLng = namedtuple('LatLng', ['lat', 'lng'])
Coords = namedtuple('Coords', ['x', 'y'])
Tile = namedtuple('Tile', ['x', 'y', 'z'])
Bounds = namedtuple('Bounds', ['sw', 'ne'])
Layer = namedtuple('Layer', ['product', 'tile_matrix_set', 'date', 'epsg', 'ext'])

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


iter_date = datetime.date(2020, 1, 1)


layers = {
    'temp': Layer('AIRS_L2_Temperature_500hPa_Day', None, None, None, None),
    'particulate': Layer('Particulate_Matter_Below_2.5micrometers_2010-2012', None, None, None, None),
    'rain': Layer('A2_RainOcn_NRT', None, None, None, None),
    'wind': Layer('AMSR2_Wind_Speed_Day', None, None, None, None),
    'albedo': Layer('MERRA2_Surface_Albedo_Monthly', None, None, None, None),
    'elevation': Layer('ASTER_GDEM_Color_Index', None, None, None, None),
    'soil_moisture': Layer('Aquarius_Soil_Moisture_Daily', None, None, None, None),
    'pressure': Layer('MERRA2_Surface_Pressure_Monthly', None, None, None, None),
    'population': Layer('GPW_Population_Density_2020', None, None, None, None),
    'air_mass': Layer('GOES-West_ABI_Air_Mass', None, None, None, None),
    'clouds': Layer('MODIS_Terra_CorrectedReflectance_TrueColor', '250m', None, '4326', 'jpg')
}

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
        'pixel_data': get_image(seattle_top_left, seattle_bottom_right, 4, mid)
    })


def degToBin(lon, lat):
    return ((lon+180) / 360.0 * 256, (lat+90) / 180.0 * 256)
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

seattle_top_left = LatLng(43.3992, -125.2586)
seattle_bottom_right =  LatLng(43.9992, -116.6586)

def flip(x):
    return x[1], x[0]

def find_tile(lat_lon_1, lat_lon_2):
    for level in range(7):
        coords1 = deg2num(lat_lon_1[0], lat_lon_1[1], level)
        coords2 = deg2num(lat_lon_2[0], lat_lon_2[1], level)
        print('Level', level)
        print('top left', coords1)
        print('bottom right', coords2)

find_tile(flip(seattle_top_left), flip(seattle_bottom_right))

def url_for(epsg_code, product, time, matrix_set, tile, ext):
    return f'https://gibs.earthdata.nasa.gov/wmts/epsg{epsg_code}/best/{product}/default/{time}/{matrix_set}/{tile.z}/{tile.y}/{tile.x}.{ext}'

def get_image(top_left, bottom_right, zoom, mid):
    global iter_date
    merc = Mercator()
    tile = merc.getTileAtLatLng(top_left, zoom)
    # bottom_right_tile = merc.getTileAtLatLng(bottom_right, zoom)

    layer = layers[mid]

    today = '2020-10-01'

    product = layer.product
    tile_matrix_set = layer.tile_matrix_set or 'GoogleMapsCompatible_Level6'
    date = layer.date
    if date is None:
        if iter_date > datetime.date.today():
            iter_date = datetime.date(2020, 1, 1)
        else:
            iter_date = iter_date + datetime.timedelta(days=1)
        date = iter_date.strftime('%Y-%m-%d')

    epsg = layer.epsg or '3857'
    ext = layer.ext or 'png'


    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    url = url_for(epsg, product, date, tile_matrix_set, tile, ext)
    print(url)
    r = requests.get(url)
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
        if i.mode == 'P':

            return [
                [
                    [int(pic[i, j]), int(pic[i, j]), int(pic[i, j])] for i in range(32)
                ] for j in range(32)
            ]
        if i.mode == 'RGB':
            return [
                [
                    [int(pic[i, j, 0]), int(pic[i, j, 1]), int(pic[i, j, 2])] for i in range(32)
                ] for j in range(32)
            ]
    return 'Download Failed'

@app.route('/layers')
def get_layer_list():
    return jsonify([
        {
            'lid': 'layer_id1',
            'layer_name': 'Air Quality',
            'source': 'https://google.com/'
        }
    ])


class Mercator():
    def __init__(self):
        pass
    def fromLatLngToPoint(self, lat_lng):
        siny = min(max(math.sin(lat_lng.lat* (math.pi / 180)), -.9999), .9999)

        return Coords(
            128 + lat_lng.lng * (256/360), 
            128 + math.log((1 + siny) / (1 - siny)) * -(256 / (2 * math.pi))
        )

    def fromPointToLatLng(self, point):
        return LatLng(
            (2 * math.atan(math.exp((point.y - 128) / -(256 / (2 * math.PI)))) -
                    math.pi / 2)/ (math.pi / 180),
            (point.x - 128) / (256 / 360)
        )
    
    def getTileAtLatLng(self, lat_lng, zoom):
        t = math.pow(2,zoom)
        s = 256/t
        p = self.fromLatLngToPoint(lat_lng)
        return Tile(
            math.floor(p.x/s),
            math.floor(p.y/s),
            zoom
        )
    
    def nomalizeTile(self, tile):
        t = math.pow(2,tile.z)
        tile.x = ((tile.x%t)+t)%t
        tile.y = ((tile.y%t)+t)%t
        return tile
    
    def getTileBounds(self, tile):
        tile = self.normalizeTile(tile)
        t = math.pow(2,tile.z)
        s = 256/t
        sw = Coords(
            tile.x*s,
            (tile.y*s)+s
        )
        ne = Coords(
            tile.x*s+s,
            (tile.y*s)
        )
        return Bounds(
            self.fromPointToLatLng(sw),
            self.fromPointToLatLng(ne)
        )

