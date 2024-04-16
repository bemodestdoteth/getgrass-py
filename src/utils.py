from dotenv import load_dotenv
from os import getenv
from requests import get
from models import Device, User
from json import dumps
from typing import List

load_dotenv()

TOKEN = getenv('TOKEN')
CERT_PATH = getenv('CERT_PATH')

headers = { 'Authorization': TOKEN }

def getDevices() -> List[Device]:
    params = { "input": dumps( { "limit": 100 }) }
    result = get('https://api.getgrass.io/devices', params=params, headers=headers).json()
    return [Device.from_json(dumps(device)) for device in result['result']['data']['data']]


def getDeviceInfo(devices: List[Device], deviceId: str) -> Device: 
    for device in devices:
        if deviceId == device.deviceId:
            return device
        
    return None


def getUser() -> User:
    result = get('https://api.getgrass.io/retrieveUser', headers=headers, verify=False).json()
    return User.from_json(dumps(result['result']['data']))