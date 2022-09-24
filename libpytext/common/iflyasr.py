# -*- coding: utf-8 -*-
import asyncio
import pydub
import websocket
import datetime
import requests
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
from io import BytesIO
from subprocess import Popen, PIPE
import os
from mykey.me import package_key_res_path
from libpycommon.common.misc import get_env_encrypted
from common.const import STATUS_FIRST_FRAME,STATUS_CONTINUE_FRAME,STATUS_LAST_FRAME
from model.rbt3_config import asr_cache

class Ws_Param(object):
    # 初始化
    def __init__(self,AudioFile):
        self.APPID = get_env_encrypted('XUNFEI_APPID', package_key_res_path)
        self.APIKey = get_env_encrypted('XUNFEI_APIKEY', package_key_res_path)
        self.APISecret = get_env_encrypted('XUNFEI_APISECRET', package_key_res_path)
        self.AudioFile = AudioFile

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":0,"vad_eos":10000}
        self.ASR_result=''
        self.openf=open(AudioFile, "rb") if isinstance(AudioFile,str) else AudioFile

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "iat-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "iat-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        return url
def get_asr(url,cache=None):
    def dump_pcm(bytes_io_file):
        bytes_io_file.seek(0)
        content = bytes_io_file.getvalue()
        cmd="ffmpeg -n -i pipe: -acodec pcm_s16le -f s16le -ac 1 -ar 16000 pipe:".split()
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
        out, _ = p.communicate(input=content)
        p.stdin.close()
        return BytesIO(out)
    # 收到websocket消息的处理
    def on_message(ws, message):
        try:
            # print('got msg')
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

            else:
                data = json.loads(message)["data"]["result"]["ws"]
                # print(json.loads(message))
                result = ""
                for i in data:
                    for w in i["cw"]:
                        result += w["w"]
                        wsParam.ASR_result += w["w"]
                #print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
        except Exception as e:
            print("receive msg,but parse exception:", e)

    # 收到websocket错误的处理
    def on_error(ws, error):
        print("### error:", error)

    # 收到websocket关闭的处理
    def on_close(ws):
        print("### closed ###")

    # 收到websocket连接建立的处理
    def on_open(ws):
        def run(*args):
            frameSize = 16000  # 每一帧的音频大小
            intervel = 0.04  # 发送音频间隔(单位:s)
            status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧
            with wsParam.openf as fp:
                while True:
                    buf = fp.read(frameSize)
                    # 文件结束
                    if not buf:
                        status = STATUS_LAST_FRAME
                    # 第一帧处理
                    # 发送第一帧音频，带business 参数
                    # appid 必须带上，只需第一帧发送
                    if status == STATUS_FIRST_FRAME:

                        d = {"common": wsParam.CommonArgs,
                             "business": wsParam.BusinessArgs,
                             "data": {"status": 0, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    # 中间帧处理
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        ws.send(json.dumps(d))
                    # 最后一帧处理
                    elif status == STATUS_LAST_FRAME:
                        d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        ws.send(json.dumps(d))
                        time.sleep(1)
                        break
                    # 模拟音频采样间隔
                    time.sleep(intervel)
            ws.close()

        thread.start_new_thread(run, ())

    if cache:
        if url in cache.keys():
            return cache.get(url,'')

    if url.startswith("http"):
        res=requests.get(url)
        url=dump_pcm(BytesIO(res.content))
        mp3=pydub.AudioSegment.from_file(BytesIO(res.content), "mp3")
        if mp3.duration_seconds>59:
            return ''


    wsParam = Ws_Param(AudioFile=url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close,on_open = on_open)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return wsParam.ASR_result

if __name__ == "__main__":
    # 测试时候在此处正确填写相关信息即可运行
    get_asr('https://qc-20181213.oss-cn-shenzhen.aliyuncs.com/ap/m/in/20210622/100588/chat/303f4ac3-7ed2-463e-b96f-351782341ac2.mp3')
    # if asr_cache:
    #     for k in asr_cache:
    #         asr_cache[k]=get_asr(k)
    #
    #     new_cache={}
    #     for k,v in asr_cache.items():
    #         if k not in new_cache and v:
    #             new_cache[k]=v
    #
    #     json.dump(new_cache, open('data/corpus/asr.json', 'w'), ensure_ascii=False)
    # else:pass