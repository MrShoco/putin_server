import json
import os
import requests
from datetime import datetime
from tqdm import tqdm
import lxml.etree as ET

def convert_timestamp(timestamp):
    timestamp = str(timestamp)[:-3]
    time = datetime.fromtimestamp(float(timestamp))
    return datetime.strftime(time, '%Y-%m-%dT%H:%M:%SZ')

def build_gpx(track):
    if 'features' not in track:
        return None
    gpx = ET.Element('gpx')
    first_time = track['features'][0]['properties']['deviceTime']
    ET.SubElement(gpx, 'time').text = convert_timestamp(first_time)
    trk = ET.SubElement(gpx, 'trk')
    trkseg = ET.SubElement(trk, 'trkseg')

    for point in track['features']:
        lat, lon = point['geometry']['coordinates'][:2]
        props = point['properties']
        time = convert_timestamp(props['deviceTime'])
        trkpt = ET.SubElement(trkseg, 'trkpt', lat=str(lat), lon=str(lon))
        ET.SubElement(trkpt, 'time').text = time

    return ET.tostring(gpx, xml_declaration=True, encoding='utf-8')

def request_graphhopper(gpx, host='35.156.134.217', port=8080):
    response = requests.post('http://{}:{}/match'.format(host, port),
                             params={'vehicle' : 'car',
                                     'debug' : True,
                                     'points_encoded' : False},
                             headers={'Content-Type' : 'application/gpx+xml'},
                             data=gpx)
    if response.ok:
        return response.json()
    return None

def process_json(file):
    # TODO: check if file.open needed
    gpx = build_gpx(json.loads(file.read().decode()))
    return request_graphhopper(gpx)

def process_gpx(file):
    return request_graphhopper(file)
