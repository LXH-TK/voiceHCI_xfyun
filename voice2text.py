# -*- coding：utf-8 -*-
# 科大讯飞语音听写python3.1 @ MacOS(流式 WebAPI 接口)
# Author: TK

import sys
import time
import json
import hmac
import base64
import hashlib
import websocket
from urllib.parse import quote
from email.utils import formatdate


host = "ws-api.xfyun.cn"
algorithm = "hmac-sha256"
request_line = "GET /v2/iat HTTP/1.1"
# 当前时间戳，RFC1123格式
date = formatdate(timeval=None, localtime=False, usegmt=True)
API_KEY = "7e0e6db2203637fbe0fbf177319fd60a"
API_SECRET = "1991ec578d7525e3aa9985e2c944bbaf"

# 每一帧的音频大小
frame_size = 122 * 8


# 计算授权码并返回
def assemble_auth_url():
    # signature原始字段
    signature_origin = "host: " + host + "\ndate: " + date + "\n" + request_line
    # hmac-sha256加密，参数为bytes格式
    signature_sha = hmac.new(key=bytes(API_SECRET, 'utf-8'),
                             msg=bytes(signature_origin, 'utf-8'),
                             digestmod=hashlib.sha256)
    # 最终signature，将bytes重新编解码
    # 因为3.x中字符都为unicode编码，而b64encode函数的参数为byte类型，所以必须先转码为utf-8的bytes
    signature = base64.b64encode(signature_sha.digest()).decode(encoding='utf-8')
    # 最后再对authorization_origin进行base64编码获得最终的authorization参数
    authorization_origin = "hmac username=\"" + API_KEY + \
                           "\",algorithm=\"hmac-sha256\",headers=\"host date request-line\",signature=\"" + \
                           signature + "\""
    authorization_final = base64.b64encode(bytes(authorization_origin, 'utf-8')).decode(encoding='utf-8')
    return authorization_final


# 按帧上传音频，每40ms发送122B
def upload():
    # 发送的音频帧{0:第一帧，1:中间的音频，2:最后一帧音频}
    send_status = 0
    # 按字节读取文件，122*8位=122字节
    f = open("voice2text.wav", 'rb')
    while 1:
        buffer = f.read(frame_size)
        if sys.getsizeof(buffer) < frame_size:
            send_status = 2

        buffer = base64.b64encode(buffer).decode(encoding='utf-8')
        # 发送每一帧
        if send_status == 2:
            print("发送最后一帧")
            ws.send(json.dumps({
                "data": {
                    "status": send_status,
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw",
                    "audio": buffer
                }
            }))
            break
        elif send_status == 0:
            print("发送第一帧")
            ws.send(json.dumps({
                "common": {
                    "app_id": "5d1473f7"
                },
                "business": {
                    "language": "zh_cn",
                    "domain": "iat",
                    "accent": "mandarin"
                },
                "data": {
                    "status": send_status,
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw",
                    "audio": buffer
                }
            }))
            send_status = 1
        else:
            ws.send(json.dumps({
                "data": {
                    "status": send_status,
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw",
                    "audio": buffer
                }
            }))
        # 间隔
        time.sleep(0.04)
    f.close()


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### WebSocket Closed ###")


def on_open(ws):
    print("### WebSocket Open ###")
    upload()


if __name__ == '__main__':
    checkSum = assemble_auth_url()
    # 请求地址，url编码规则
    url = "wss://ws-api.xfyun.cn/v2/iat?authorization=" + checkSum + \
          "&date=" + quote(date) + \
          "&host=" + host
    # 握手，这一句会输出服务/客户端的对话
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
