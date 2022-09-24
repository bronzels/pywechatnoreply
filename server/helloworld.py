#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import time
from concurrent import futures
import grpc
from proto.data_pb2_grpc import add_ClassifyDataServicer_to_server, \
    ClassifyDataServicer
from proto.data_pb2 import Output, OutputRecord
from libpycommon.common.misc import get_env
# from libpytext.common.myreg import Hit_regs
# from model.myreg import *
# from model.text_process import regfilter
# from model import rbt3
# from model.rbt3_config import rbt3_mul_conf,rbt3_bi_conf
from libpycommon.common import mylog


_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = '0.0.0.0'
_PORT = '8080'
class MyServe(ClassifyDataServicer):
    def __init__(self, model_mul=None,model_bi=None):
        # self.model_mul = model_mul
        # self.model_bi = model_bi
        # self.hit_regs=Hit_regs(formed_regs)
        # self.id2bi={
        #     0:[_ for _ in range(self.model_mul.conf['num_classes']) if yes_no_map[_] == 0],
        #     1:[_ for _ in range(self.model_mul.conf['num_classes']) if yes_no_map[_] == 1]
        # }
        pass

    # 这里实现我们定义的接口
    def Do(self, request, context):
        s = time.time()
        mylog.logger.info(f'dostart@:{time.time() - s}s')
        records_input = request.records
        tup_records=[(record.id,*(record.text.split("$|$"))) for record in records_input]
        mylog.logger.info(f'readingrecords=>:{time.time() - s}s,batchsize:{len(tup_records)}')
        s = time.time()
        #arr1, arr2 = regfilter(tup_records, hiter=self.hit_regs,labelmap=formed_regs_map)
        #mylog.logger.info(f'calc_re=>:{time.time() - s}s,arr1_num:{len(arr1)},arr2_num:{len(arr2)}')
        #text_l = [record.text for record in records_input]
        # id_arr2=[_[0] for _ in  arr2.tolist()]
        # if id_arr2:
        #     s = time.time()
        #     classifier_mul,classifier_mul_arr = self.model_mul.predict([_[1:] for _ in  arr2.tolist()],sparse=False)
        #     mylog.logger.info(f'mul_modelout=>:{time.time() - s}s')
        #     s = time.time()
        #
        #     classifier_bi = self.model_bi.predict([_[1:] for _ in  arr2.tolist()])
        #     mylog.logger.info(f'bi_modelout=>:{time.time() - s}s')
        #     s = time.time()
        #
        #     #纠偏
        #     classifier_mul2bi=[yes_no_map[_] for _ in classifier_mul]
        #     for i,(cmul,cbi) in enumerate(zip(classifier_mul2bi,classifier_bi)):
        #         if cmul==cbi:
        #             pass
        #         else:
        #             classifier_mul_arr[i,self.id2bi[cmul]]=0.
        #     classifier_arr2=classifier_mul_arr.argmax(-1).tolist()
        #     mylog.logger.info(f'checkout=>:{time.time() - s}s')
        #
        # else:
        #     classifier_arr2=[]

        records_output=[]
        # if arr1.tolist():
        #     records_output+=[OutputRecord(id=str(idx), classifier=int(flag),rawclassifier=int(flag)) for idx,flag in arr1.tolist()]
        # if id_arr2:
        #     records_output+=[OutputRecord(id=str(idx), classifier=int(flag), rawclassifier=int(rawflag)) for idx,flag,rawflag in zip(id_arr2,classifier_arr2,classifier_mul)]
        records_output+=[OutputRecord(id=str(idx), classifier=len(str(flag)), rawclassifier=len(str(rawflag))) for idx,flag,rawflag in tup_records]

        print("records_output: " + str(records_output))
        return Output(records=records_output)



def serve(model_mul,model_bi):
    # 这里通过thread pool来并发处理server的任务
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    # 将对应的任务处理函数添加到rpc server中
    add_ClassifyDataServicer_to_server(MyServe(model_mul,model_bi), grpcServer)

    grpcServer.add_insecure_port(_HOST + ':' + _PORT)
    grpcServer.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)

def entry():
    #model = Model()
    # albert_tiny
    # str_mul_model_assigned_fmt = '{}.Model(rbt3_mul_conf)'
    # model_mul = eval(str_mul_model_assigned_fmt.format(get_env('MODEL_NAME')))
    # str_bi_model_assigned_fmt = '{}.Model(rbt3_bi_conf)'
    # model_bi = eval(str_bi_model_assigned_fmt.format(get_env('MODEL_NAME')))

    serve(None,None)#model_mul,model_bi

if __name__ == '__main__':
    entry()
    pass
    #print(get_env('MODEL_NAME'))


# from concurrent import futures
# import time
# import grpc
# from proto import helloworld_pb2
# from proto import helloworld_pb2_grpc
#
# _ONE_DAY_IN_SECONDS = 60 * 60 * 24
#
#
# class Greeter(helloworld_pb2_grpc.GreeterServicer):
#     # 工作函数
#     def SayHello(self, request, context):
#         print(request.name)
#         message = "hello \" " + request.name + " \""
#         print(message)
#         return helloworld_pb2.HelloReply(message = message)
#
#
# def serve():
#     # gRPC 服务器
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
#     helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
#     server.add_insecure_port('0.0.0.0:8080')
#     print("sever is opening ,waiting for message...")
#     server.start()  # start() 不会阻塞，如果运行时你的代码没有其它的事情可做，你可能需要循环等待。
#     try:
#         while True:
#             time.sleep(_ONE_DAY_IN_SECONDS)
#     except KeyboardInterrupt:
#         server.stop(0)
#
# def entry():
#     serve()
