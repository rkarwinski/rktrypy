# -*- coding: utf-8 -*-

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import json
import requests
import re

app = FastAPI()

def get_configs():
    with open("config.json", encoding='utf-8') as config:
        config_all = json.load(config)
        
    return config_all 

configs = get_configs()
api_key = configs['apikey']

class Trip(BaseModel):
    firstAddress: str
    lastAddress: str
    consumption: float
    fuelCost: float
    passengers: Optional[int] = 1
    roundTrip: Optional[int] = 1

@app.get("/")
def read_root():
    return False

@app.post("/trip")
def read_item(trip: Trip):
    return calculate_trip(trip)

def get_info_maps(a, b):
    url = "https://maps.googleapis.com/maps/api/directions/json?origin=" + str(a) + "&destination=" + str(b) + "&key="+api_key

    payload={}
    headers={}

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)


def calculate_trip(trip):
    total = 0
    cost = 0
    kms = 0
    multiple = 1

    if trip.roundTrip == 1:
        multiple = 2

    trip_maps = get_info_maps(trip.firstAddress, trip.lastAddress)
    kms = float(re.sub('[^0-9]', '', str(trip_maps['routes'][0]['legs'][0]['distance']['text'])))
    time_travel = trip_maps['routes'][0]['legs'][0]['duration']['text']
    #additional_cost = float(trip_maps['cost']) api gmaps não tem valor pedagio

    total = round((((kms* multiple)/trip.consumption) * trip.fuelCost), 2)
    cost = round(total/trip.passengers, 2)

    value = {
        'cost': cost,
        'total': total,
        'kms': kms,
        'time': time_travel,
        'fullAddress': trip.firstAddress + " -> " + trip.lastAddress
    }
    
    return value