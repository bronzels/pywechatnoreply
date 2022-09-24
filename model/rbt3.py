# -*- coding: utf-8 -*-
import os
from bert4keras.backend import keras, set_gelu
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer,load_vocab
from tensorflow.keras.layers import Lambda, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
from model.rbt3_config import *
from model.text_process import p_token
from model.rbt3_config import rbt3_mul_conf,rbt3_bi_conf
#maxlen = 128,num_classes=21
class Model():
    def __init__(self,conf={}):
        self.conf = conf
        self.tokenizer = Tokenizer(conf['vocab_path'], do_lower_case=True,pre_tokenize=p_token(sp_words=sp_words,vocab_path=conf['vocab_path']))
        self.model = self._get_model()
    def _get_model(self):
        set_gelu('tanh')
        bert = build_transformer_model(
            config_path=self.conf['config_path'],
            checkpoint_path=None,
            model='roberta',
            return_keras_model=False,
        )
        output = Lambda(lambda x: x[:, 0], name='CLS-token')(bert.model.output)
        output = Dense(
            units=self.conf['num_classes'],
            activation='softmax',
            kernel_initializer=bert.initializer
        )(output)
        model = keras.models.Model(bert.model.input, output)
        model.load_weights(self.conf['weights_path'])
        return model

    def _get_tensor(self, inputs):
        tup=[self.tokenizer.encode(text1,text2, maxlen=self.conf['maxlen']) for text1,text2 in inputs]
        return [pad_sequences([_[0] for _ in tup], maxlen=self.conf['maxlen'], padding='post'),
                pad_sequences([_[1] for _ in tup], maxlen=self.conf['maxlen'], padding='post')]

    def _get_mulclassifier(self, arr):
        return arr.argmax(-1).tolist()


    def predict(self,inputs,sparse=True):
        predicted = self.model.predict(self._get_tensor(inputs))
        if sparse:
            return self._get_mulclassifier(predicted)
        else:
            return self._get_mulclassifier(predicted),predicted


if __name__ == '__main__':#01
    # model = Model(conf=rbt3_mul_conf)
    # #print(model.predict(['你好，请问是想咨询英语选课问题吗？$|$yes','$|$yes']))
    # a,b=model.predict([['你好，请问是想咨询英语选课问题吗？','yes']],sparse=False)
    pass
