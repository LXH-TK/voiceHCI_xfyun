# -*- coding: utf-8 -*-
# 科大讯飞语音合成python3.1 @ MacOS(流式 WebAPI 接口)
# 必须设置白名单，http://www.ip138.com
# Author: TK

import requests
import time
import hashlib
import base64


URL = "http://api.xfyun.cn/v1/service/v1/tts"
# 音频编码（raw合成的音频格式pcm、wav，lame合成的音频格式MP3）
AUE = "raw"
# 应用APPID
APP_ID = "5d1473f7"
# 接口密钥
API_KEY = "ac9125c91e340e7b5864c948d8e582db"


# 组装http请求头
def get_header():
    cur_time = str(int(time.time()))
    # 相关参数JSON串经Base64编码后的字符串
    param = "{\"aue\":\"" + AUE + \
            "\",\"auf\":\"audio/L16;rate=16000\"," + \
            "\"voice_name\":\"xiaoyan\"," + \
            "\"engine_type\":\"intp65\"}"
    param_base64 = str(base64.b64encode(param.encode('utf-8')), 'utf-8')
    # 计算令牌
    m2 = hashlib.md5()
    m2.update((API_KEY + cur_time + param_base64).encode('utf-8'))
    check_sum = m2.hexdigest()
    # 返回请求头
    header = {
        'X-CurTime': cur_time,
        'X-Param': param_base64,
        'X-Appid': APP_ID,
        'X-CheckSum': check_sum
    }
    return header


# 要转为音频的文字
def get_body(file):
    with open(file, 'r') as f:
        text = f.read()
        data = {'text': text}
        return data


# 写为音频文件
def write_file(file, content):
    with open(file, 'wb') as f:
        f.write(content)


if __name__ == '__main__':
    # 待合成文本内容
    r = requests.post(URL, headers=get_header(), data=get_body("text2voice.txt"))
    # 接受信息
    contentType = r.headers['Content-Type']
    if contentType == "audio/mpeg":
        sid = r.headers['sid']
        if AUE == "raw":
            # 合成音频格式为pcm、wav并保存在根目录下
            # write_file(sid + ".wav", r.content)
            write_file("text2voice.wav", r.content)
        else:
            # 合成音频格式为mp3并保存在根目录下
            # write_file(sid + ".mp3", r.content)
            write_file("text2voice.mp3", r.content)
        print("### Write Voice Succeed ###")
    else:
        print("### Write Voice Failed ###")
