import json
import uuid
import time
import socket
import hashlib
from loguru import logger
from dotenv import load_dotenv
from os import getenv
from random import random as rand
from random import randint
from websocket import WebSocketApp
import ssl
import utils
import asyncio
import requests

from fake_useragent import UserAgent

load_dotenv()

USER_ID = getenv('USER_ID')
HASH_STR = getenv('HASH_STR')
KEY = getenv('KEY')
PROXY_HOST = getenv('PROXY_HOST')
PROXY_USERNAME = getenv('PROXY_USERNAME')
PROXY_PASSWORD = getenv('PROXY_PASSWORD')
PROXY_PORT = getenv('PROXY_PORT')
TOKEN = getenv('TOKEN')
API_URL = getenv('API_URL')
URL = "wss://proxy.wynd.network:4650/"


def getUserAgent():
    return UserAgent().random

def hash_string(label: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(label.encode('utf-8'))
    return sha256.hexdigest()

def pingIPServer():
    try:
        # Send the request to the server along with the signature and timestamp
        response = requests.get(url=f'{API_URL}/ping')
        return response
    except requests.RequestException as e:
        logger.error(f"[Exception] {str(e)}")
        return False

def checkIP(ip: str):
    # Generate a signature using the secret key and the current Unix timestamp
    current_timestamp = str(int(time.time()))
    signature = hash_string(HASH_STR + current_timestamp)

    try:
        # Send the request to the server along with the signature and timestamp
        response = requests.post(
            url='{API_URL}/api/ipAddrAdd',
            json={
                'ip': ip,
                'port': PROXY_PORT,
                'key': KEY
            },
            headers={'X-Signature': signature, 'X-Timestamp': current_timestamp}
        )
        if response.status_code == 200:
            logger.info(f"IP check complete")
            return True
        else:
            logger.error(f"[{response.status_code}] {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"[Exception] {str(e)}")
        return False

def removeIP():
    # Generate a signature using the secret key and the current Unix timestamp
    current_timestamp = str(int(time.time()))
    signature = hash_string(HASH_STR + current_timestamp)

    url = f'{API_URL}/api/ipAddrRemove'

    try:
        # Send the request to the server along with the signature and timestamp
        response = requests.post(
            url=url,
            json={
                'port': PROXY_PORT,
                'key': KEY
            },
            headers={'X-Signature': signature, 'X-Timestamp': current_timestamp}
        )
        if response.status_code == 200:
            logger.info(f"IP removal complete")
            return True
        else:
            logger.error(f"[{response.status_code}] {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"[Exception] {str(e)}")
        return False    

def main():
    useragent = getUserAgent()
    deviceId = str(uuid.uuid3(uuid.NAMESPACE_DNS, getUserAgent()))
    logger.info(useragent)
    logger.info(deviceId)
    ipScores = []

    def getAuthMessage(message):
        return {
            "id": message["id"],
            "origin_action": "AUTH",
            "result": {
                "browser_id": deviceId,
                "user_id": USER_ID,
                "user_agent": useragent,
                "timestamp": int(time.time()),
                "device_type": "extension",
                "version": "2.5.0"
            }
        }
    
    def getPingMessage():
        logger.warning('Getting ping message')
        return {
            "id": str(uuid.uuid4()),
            "version": "1.0.0",
            "action": "PING",
            "data": {}
        }
    
    def sendMessage(payload):
        s = json.dumps(payload)
        logger.info(f'<<< {s}')
        ws.send(s)

    def onMessage(ws, message):
        message = json.loads(message)
        logger.info(f">>> {message}")

        if (message.get('action') == 'AUTH'):
            payload = getAuthMessage(message)
            sendMessage(payload)

    def onOpen(ws):
        logger.info(pingIPServer())
        logger.info('Connected')

    def onCLose(ws, _, __):
        logger.warning('Closed')

    def onPing(ws):
        logger.info(f"Ping")
        sendMessage(getPingMessage())
    
    def onPong(ws, message):
        logger.info(f"Pong {message}")
        sendMessage(getPingMessage())
        checkState()

    def onError(ws, error):
        logger.warning(f"Error {error}")

    def checkState():
        device = utils.getDeviceInfo(utils.getDevices(), deviceId)

        if not checkIP(device.ipAddress):
            ws.close()
            exit()

        ipScores.append(str(device.ipScore))
        logger.info(f"Device score {device.ipScore}")

        if len(ipScores) >= 5 and device.ipScore <= 74:
            logger.warning(f'Device score is too low ({" ".join(ipScores)}), exitting')
            ws.close()
            exit()
        
    user = utils.getUser()

    logger.info(f"Email {user.email}; Username {user.username}; UserId {user.userId}")

    time.sleep(randint(1, 10))

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    ws = WebSocketApp(
        URL,
        header={ 'User-Agent': useragent },
        on_message=onMessage,
        on_open=onOpen,
        on_close=onCLose,
        on_ping=onPing,
        on_pong=onPong,
        on_error=onError,
    )

    ws.run_forever(
        http_proxy_host=PROXY_HOST,
        http_proxy_auth=(PROXY_USERNAME, PROXY_PASSWORD),
        http_proxy_port=PROXY_PORT, 
        proxy_type="socks5",
        ping_interval=20,
        ping_timeout=5,
        ping_payload=json.dumps(getPingMessage()),
        sslopt={"cert_reqs": ssl.CERT_NONE},
    )
    
    removeIP()

main()