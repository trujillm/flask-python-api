from ast import While
from operator import pos
from flask import Flask, request
import requests
from flask import jsonify, make_response
from flask_caching import Cache
import json
import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


app = Flask(__name__)
# setup cache for in memory use
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

# Setup for retries
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
http = requests.Session()
http.mount('http://', HTTPAdapter(max_retries=retries))
http.mount("https://", adapter)
http.mount("http://", adapter)


# Request url
satellite_url = "http://localhost:3000"

# Validate data for post
def data_valid(request_data):
    try:
        frequency = request_data.json["frequency"]
    except KeyError as e:
        return False
    else:
        frequency = request_data.json["frequency"]
        if isinstance(frequency, int):
            return True
        else:
            return "False_int"

# Create poll for satellite create sensor
def create_sensor_post(url, request):
    try:
        post_create_sensor = http.post(url, json = request.json, timeout=20)
        response = make_response(
            post_create_sensor.text,
            200
            )
        return response
    except requests.exceptions.RequestException as e:
        return e

# Create poll for get sensorids
def get_sensorids_request():
    get_sensorids_route = '/sensor-ids'
    url = satellite_url + get_sensorids_route
    try:
       get_sensorids = http.get(url, timeout=20)

       if get_sensorids.text == "":
           return False

       return get_sensorids
    except requests.exceptions.RequestException as e:
        return e


# Create poll for get all sensors
def get_all_scensors(list_ids):
    poll = 0
    get_sensor_route = '/sensors/'
    url = satellite_url + get_sensor_route
    id_list = json.loads(list_ids.text)
    sensors = []
    current_time = {}
    for id in id_list:
        try:
            get_sensor = http.get(url + str(id), timeout=20)
            current_time = datetime.datetime.now()
            if get_sensor.status_code == 200:
                current_time = { "retrieved":str(current_time) }
                get_sensor = json.loads(get_sensor.text)
                get_sensor.update(current_time)
                sensors.append(get_sensor)
            elif get_sensor.status_code == 404:
                sensors.append(str(id) + " does not exist")
        except requests.exceptions.RequestException as e:
            return e

    if len(id_list) == len(sensors):
        return sensors
    else:
        return "Error, please check server logs", 500
        

@app.route("/")
def hello_world():
    return "Hello world!"


@app.route("/create-sensor", methods=["POST"])
def create_sensor():
    create_sensor_route = '/sensors'
    url = satellite_url + create_sensor_route

    # Validate data frequency
    check_data = data_valid(request)
    if check_data == False:
        return "frequency is absent", 400
    elif check_data == "False_int":
        return "frequency is invalid: must be int", 400
    else:
        frequency = request.json["frequency"]

    # Create post to satalite
    create_sensor = create_sensor_post(url, request)
        
    return create_sensor

@cache.memoize(timeout=172800)  # cache for 2 days
@app.route("/poll", methods=["GET"])
def poll():
    # Get all sensor ids
    sensorids = get_sensorids_request()
    if isinstance(sensorids, Exception):
        return sensorids
    elif sensorids == False:
        return "No ID's have been created on the server"
        
    # Get all sensors
    all_sensors_request = get_all_scensors(sensorids)
    if isinstance(sensorids, Exception):
        return sensorids
    
    cache.set("get_all_sensors", all_sensors_request)

    return json.dumps(all_sensors_request)

@app.route("/all-sensors")
def all_sensors():
    sensors = cache.get("get_all_sensors")
    # senors_formatted_str = json.dumps(sensors, indent=2)
    if not sensors or sensors == "":
        return "Sensors need to be updated, please poll"
        
    return json.dumps(sensors)
