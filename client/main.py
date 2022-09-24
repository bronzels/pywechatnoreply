#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import grpc
import sys
import logging
sys.path.append('..')

from libpycommon.common import mylog

from proto.data_pb2 import *
from proto.data_pb2_grpc import ClassifyDataStub

_HOST = 'localhost'
_PORT = '8080'
# _PORT= '30001'
# _HOST= '10.15.67.2'
def sent_single(id,txt):
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = ClassifyDataStub(channel=conn)
    input = Input()
    record = input.records.add()
    record.id = '{}'.format(id)
    record.text = txt
    output = client.Do(input)
    conn.close()
    return output
def entry():
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = ClassifyDataStub(channel=conn)
    input = Input()
    texts = [
        '{"text":"你好，请问是想咨询什么"}$|${"text":"我想冻结剩下的课没时间上了"}',
        '{"text":"#"}$|${"text":"撤回了一条消息"}',
        # '{"text":"你好，请问是想咨询什么？"}$|${"text":"你们这个课怎么卖"}',
        # '{"text":"我帮孩子调整了一下教材"}$|${"text":"教材就不换了，我在试试"}',
        # '$|${"text":"老师准时上课吗?"}',
        # '{"text":"你好，请问是想咨询什么？"}$|${"text":"对方未添加你为朋友"}',
        # '{"text":"你好，请问是想咨询什么？"}$|${"text":"与对方发生资金往来可能存在风险"}',
        # '{"text":"你好，请问是想咨询什么？"}$|${"text":"voip_content_voice聊天时长"}',
    ]
#    texts=texts*30
    for i in range(len(texts)):
        record = input.records.add()
        record.id = '{}'.format(i)
        record.text = texts[i]
    print(str(input))
    #log.log(logging.INFO, msg='dostart' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    output = client.Do(input)
    #log.log(logging.INFO, msg='doend' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    conn.close()
    print("output: " +str(output.records))

if __name__ == '__main__':
    log = mylog.get_logger()
    s=time.time()
    entry()
    log.log(logging.INFO, msg=f'heart@[{time.time()-s}]s')

    #log.log(logging.INFO, msg='calc' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
