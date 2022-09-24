# -*- coding: utf-8 -*-
import os

import pandas as pd
import math
import numpy as np
from bert4keras.tokenizers import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import precision_recall_fscore_support


from libpytext.model.mybert4keras import checkpoint_finder
from model.text_process import p_token
from trainer.uilts import DATA_PATH,get_model_single
from model.myreg import *
#查区别
target_corpus=DATA_PATH+'/corpus/test.csv'
target_model_path=DATA_PATH+'/pywechatnoreply/rbt3/mul_rel_202106170256'
vocab_path,config_path,checkpoint_path=checkpoint_finder(target_model_path)
num_class=2 if target_model_path.split('/')[-1].startswith("bi") else 20
maxlen=int(target_model_path[-3:])
def do_predict(df,bz=500,maxlen=maxlen):
    steps=math.ceil(df.shape[0]/bz)
    predicts=[]
    for _ in range(steps):
        tmplist=df.values[bz*_:bz*_+bz,1:3].tolist()
        tups = [tokenizer.encode(text1, text2, maxlen=maxlen) for text1, text2 in tmplist]
        tups=[pad_sequences([_[0] for _ in tups], maxlen=maxlen, padding='post'),
        pad_sequences([_[1] for _ in tups], maxlen=maxlen, padding='post')]

        res=model.predict(tups).argmax(-1).tolist()
        predicts+=res
    df['predict']=predicts


if __name__ == '__main__':
    model = get_model_single(model_path= checkpoint_path,num_classes=num_class)
    tokenizer = Tokenizer(vocab_path, do_lower_case=True, pre_tokenize=p_token(sp_words=sp_words,vocab_path=vocab_path))
    df = pd.read_csv(target_corpus)
    df.fillna('', inplace=True)
    do_predict(df)
    result={}
    prfs = precision_recall_fscore_support(df.predict.tolist(), df.flag.tolist())
    for i, _ in enumerate(zip(*prfs)):
        result[i] = _
    result_df = pd.DataFrame(result)
    errors_df=df[~df.flag==df.predict]
    result_df.to_csv(target_corpus.replace('.csv','_shooter.csv'),quoting=1,index=None,encoding='utf8')
    errors_df.to_csv(target_corpus.replace('.csv','_error.csv'),quoting=1,index=None,encoding='utf8')



