from websocket import WebSocketApp
import json
import uuid
import time
from loguru import logger
from dotenv import load_dotenv
from os import getenv
from random import randint
import ssl
import utils

from fake_useragent import UserAgent

load_dotenv()

USER_ID = getenv('USER_ID')
PROXY_HOST = getenv('PROXY_HOST')
PROXY_USERNAME = getenv('PROXY_USERNAME')
PROXY_PASSWORD = getenv('PROXY_PASSWORD')
PROXY_PORT = getenv('PROXY_PORT')
TOKEN = getenv('TOKEN')
URL = "wss://proxy.wynd.network:4650/"

def getUserAgent():
    return UserAgent().random

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
        ipScores.append(str(device.ipScore))
        logger.info(f"Device score {device.ipScore}")

        if len(ipScores) >= 5 and device.ipScore <= 75:
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

main()