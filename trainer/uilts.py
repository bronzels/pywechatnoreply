# -*- coding: utf-8 -*-
import time
import os
os.environ['TF_KERAS']='1'
import linecache
import tensorflow as tf
import pandas as pd

from bert4keras.models import build_transformer_model
from bert4keras.optimizers import Adam, extend_with_piecewise_linear_lr
from bert4keras.tokenizers import Tokenizer
from bert4keras.backend import set_gelu

from tensorflow import keras
from tensorflow.keras.layers import Lambda, Dense
from bert4keras.snippets import DataGenerator,sequence_padding
from libpytext.model.mybert4keras import checkpoint_finder
from model.text_process import p_token
from model.text_process import regfilter
from model.myreg import formed_regs,yes_no_map
from libpytext.common.myreg import Hit_regs

from common.const import *
DATA_PATH=os.path.abspath(__file__+'../../../'+'data')

"""
#roberta3下载地址
https://github.com/ymcui/Chinese-BERT-wwm
模型：RBTL3, Chinese
"""
vocab_path,config_path,checkpoint_path=checkpoint_finder(DATA_PATH+'/pretrainedmodel/rbt3')
sp_words = [linecache.getline(vocab_path,_).strip()[1:-1] for _ in range(1,101) if linecache.getline(vocab_path,_)[0]=='【']
corpus=DATA_PATH+'/corpus/noreplycorpus_0701.csv'
fixed_corpus=DATA_PATH+'/corpus/corpusfixed_0623.xlsx'

batch_size=32
test_rate=0.05
epochs=15
max_len=256



def load_dfdata(df,startcol=1,span=2):
    return [tuple(_[startcol:startcol+span]) for _ in df.values.tolist()]
class Batch_Generator(DataGenerator):
    def __init__(self,data,batch_size,tokenizer,sparse=True,maxlen=256,num_classes=20):
        super(Batch_Generator, self).__init__(data, batch_size, buffer_size=None)
        self.tokenizer=tokenizer
        self.sparse=sparse
        self.maxlen=maxlen
        self.num_classes=num_classes
    def __iter__(self, random=False):
        batch_token_ids, batch_segment_ids, batch_labels = [], [], []
        for is_end, (text1, text2,label) in self.sample(random):
            token_ids, segment_ids = self.tokenizer.encode(first_text=text1,second_text=text2, maxlen=self.maxlen)
            batch_token_ids.append(token_ids)
            batch_segment_ids.append(segment_ids)
            if self.sparse:
                batch_labels.append([label])
            else:
                batch_labels.append([1 if _==label else 0 for _ in range(self.num_classes)])
            if len(batch_token_ids) == self.batch_size or is_end:
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                batch_labels = sequence_padding(batch_labels)
                yield [batch_token_ids, batch_segment_ids], batch_labels
                batch_token_ids, batch_segment_ids, batch_labels = [], [], []


def preparedata4mul(df,num_classes,sparse=False):
    tokenizer = Tokenizer(vocab_path, do_lower_case=True,
                          pre_tokenize=p_token(sp_words=sp_words, vocab_path=vocab_path))
    token_ids,segment_ids,labels=[],[],[]
    for _ in df.values:
        token_id,segment_id=tokenizer.encode(first_text=_[0], second_text=_[1], maxlen=max_len)
        token_ids.append(token_id)
        segment_ids.append(segment_id)
        if not sparse:
            labels.append([1 if i == _[2] else 0 for i in range(num_classes)])
        else:
            labels.append([_[2]])
    token_ids=sequence_padding(token_ids,length=max_len)
    segment_ids=sequence_padding(segment_ids,length=max_len)
    return  token_ids,segment_ids,labels



def get_model_single(loss='sparse_categorical_crossentropy',
                model_path=None,
                learning_rate=1e-5,
                lr_schedule={1000: 1,3000: 0.1},
                num_classes=20,
                config_path=config_path,
                model='roberta'):
    set_gelu('tanh')
    bert = build_transformer_model(
        config_path=config_path,
        checkpoint_path=checkpoint_path if not model_path else None,
        model=model,
        return_keras_model=False,
    )
    output = Lambda(lambda x: x[:, 0], name='CLS-token')(bert.model.output)
    output = Dense(
        units=num_classes,
        activation='softmax',
        kernel_initializer=bert.initializer
    )(output)
    model = keras.models.Model(bert.model.input, output)
    if model_path:
        model.load_weights(model_path)
        return model
    AdamLR = extend_with_piecewise_linear_lr(Adam, name='AdamLR')
    model.compile(
        #loss='sparse_categorical_crossentropy',
        loss=loss,
        optimizer=AdamLR(learning_rate=learning_rate, lr_schedule=lr_schedule),
        metrics=['accuracy'],
    )
    return model

def get_model_mul(loss='sparse_categorical_crossentropy',
                  num_classes=20,
                  lr_schedule={1000: 1,3000: 0.1},
                  config_path=config_path,):
    set_gelu('tanh')
    strategy = tf.distribute.MirroredStrategy()
    with strategy.scope():
        bert = build_transformer_model(
            config_path=config_path,
            model='roberta',
            return_keras_model=False,
        )

        output = Lambda(lambda x: x[:, 0], name='CLS-token')(bert.model.output)
        output = Dense(
            units=num_classes,
            activation='softmax',
            kernel_initializer=bert.initializer,
            name='Output'
        )(output)
        model = keras.models.Model(bert.model.input, output)
        AdamLR = extend_with_piecewise_linear_lr(Adam, name='AdamLR')
        model.compile(
            loss=loss,
            optimizer=AdamLR(learning_rate=1e-5, lr_schedule=lr_schedule),
            metrics=['accuracy'],
        )
        bert.load_weights_from_checkpoint(checkpoint_path)
    return model

def get_train_data(train_data,mul_gpu=True,num_class=2):
    if mul_gpu:
        token_ids, segment_ids, labels = preparedata4mul(train_data[['stafftext', 'custtext', 'flag']], num_class)
        tot=len(token_ids)
        val_dataset=tf.data.Dataset.from_tensor_slices(({
        "Input-Token": token_ids[:int(tot*test_rate)],
        "Input-Segment": segment_ids[:int(tot*test_rate)],
        },labels[:int(tot*test_rate)]))
        dataset=tf.data.Dataset.from_tensor_slices(({
        "Input-Token": token_ids[int(tot*test_rate):],
        "Input-Segment": segment_ids[int(tot*test_rate):],
        },labels[int(tot*test_rate):]))
        dataset=dataset.shuffle(999).batch(batch_size).repeat(-1)
        val_dataset=val_dataset.batch(batch_size)
        return dataset,val_dataset
    else:
        test_data = train_data[:int(train_data.__len__() * test_rate)]
        train_data = train_data[int(train_data.__len__() * test_rate):]
        train_data = load_dfdata(train_data, span=3)
        test_data = load_dfdata(test_data, span=3)
        tokenizer = Tokenizer(vocab_path, do_lower_case=True,
                              pre_tokenize=p_token(sp_words=sp_words, vocab_path=vocab_path))
        train_gen = Batch_Generator(train_data, batch_size, tokenizer, sparse=False, maxlen=max_len,
                                    num_classes=num_class)
        test_gen = Batch_Generator(test_data, batch_size, tokenizer, sparse=False, maxlen=max_len,
                                   num_classes=num_class)
        return train_gen,test_gen

def get_corpus(excel_path=fixed_corpus):
    if not os.path.exists(corpus):
        df = pd.read_excel(excel_path)
        df = df[['id', 'stafftext', 'custtext', 'flag']]
        arr1, arr2 = regfilter(df, list_batch=False, labelmap=None, raw=False, with_flag=True,
                               hiter=Hit_regs(formed_regs))
        df = pd.DataFrame(arr2)
        df.columns = ['id', 'stafftext', 'custtext', 'flag']

        if flagmap:
            def str2int(s: str):
                for key in flagmap:
                    if s in flagmap[key]:
                        return key
                return s

            df['flag'] = df['flag'].map(str2int)
            df = df[df.flag.isin(flagmap.keys())]
            df.flag = df.flag.astype('int')
        df.to_csv(corpus, quoting=1, index=None)
    else:
        df = pd.read_csv(corpus)
    return df


def evaluate(data,model,ifidx=True):
    total, right = 0., 0.
    for x_true, y_true in data:
        y_pred = model.predict(x_true).argmax(axis=1)
        if ifidx:
            y_true = y_true[:, 0]
        else:
            y_true = y_true.argmax(-1)
        total += len(y_true)
        right += (y_true == y_pred).sum()
    return right / total

class Evaluator(keras.callbacks.Callback):
    def __init__(self,test_generator,model,out_path,ifidx=True):
        self.best_val_acc = 0.
        self.test_generator=test_generator
        self.model=model
        self.ifidx=ifidx
        self.out_path=out_path
    def on_epoch_end(self, epoch, logs=None):
        s=time.time()
        test_acc = evaluate(self.test_generator,self.model,self.ifidx)
        if test_acc > self.best_val_acc:
            self.best_val_acc = test_acc
            self.model.save_weights(self.out_path+f'model_e{epoch}.weights')
        s=time.time()-s
        print(f'best_val_acc:{self.best_val_acc:.4f}, test_acc: {test_acc:.4f},usetime:{s:.4f}')



class Saver(keras.callbacks.Callback):
    def __init__(self,model,out_path):
        self.model=model
        self.out_path=out_path
    def on_epoch_end(self, epoch, logs=None):
        self.model.save_weights(self.out_path+f'model_e{epoch}.weights')
        print(f'model_e{epoch} has been saved')


def mul_focal(gamma=2., alpha=.25):

    epsilon = 1.e-7
    gamma = float(gamma)
    alpha = tf.constant(alpha, dtype=tf.float32)

    def multi_category_focal_loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.clip_by_value(y_pred, epsilon, 1. - epsilon)

        alpha_t = y_true * alpha + (tf.ones_like(y_true) - y_true) * (1 - alpha)
        y_t = tf.multiply(y_true, y_pred) + tf.multiply(1 - y_true, 1 - y_pred)
        ce = -tf.math.log(y_t)
        weight = tf.math.pow(tf.subtract(1., y_t), gamma)
        fl = tf.multiply(tf.multiply(weight, ce), alpha_t)
        loss = tf.reduce_mean(fl)
        return loss

    return multi_category_focal_loss
flagmap={
    SUB_CLASSIFIER_xiaoshou:['销售相关咨询'],
    #1:['投诉'],
    SUB_CLASSIFIER_guihua:['学习规划','学习计划'],
    SUB_CLASSIFIER_shijian:['课程时间安排',' 课程时间安排'],
    SUB_CLASSIFIER_gongju:['上课工具'],
    SUB_CLASSIFIER_jiaoshi:['教师问题','教室问题'],
    SUB_CLASSIFIER_huoli:['客户获利咨询','客户福利咨询'],
    SUB_CLASSIFIER_shouhou:['售后相关咨询','售后'],
    SUB_CLASSIFIER_dizhi:['地址信息反馈'],
    SUB_CLASSIFIER_geren:['个人信息反馈'],
    SUB_CLASSIFIER_zixun:['其他咨询','其它咨询'],
    SUB_CLASSIFIER_dazhaohu:['打招呼'],
    SUB_CLASSIFIER_jujue:['拒绝结束'],
    SUB_CLASSIFIER_kaolv:['考虑结束'],
    SUB_CLASSIFIER_zantongke:['赞同结束-可跟进','赞同结束-可根据'],
    SUB_CLASSIFIER_zantongbu:['赞同结束-不需跟进','赞同结束-无需跟进','赞同结束无需回复'],
    SUB_CLASSIFIER_bangmang:['找帮忙'],
    SUB_CLASSIFIER_jitang:['祝福鸡汤'],
    SUB_CLASSIFIER_ad:['纯广告'],
    SUB_CLASSIFIER_xianliao: ['闲聊'],
    SUB_CLASSIFIER_qita:['多媒体','无意义','其他','其它'],
#    SUB_CLASSIFIER_qita:['多媒体','无意义','其他','其它','转换好友','删除好友','转好友','员工','员工聊撩','员工聊天',' 员工互聊'],
}
if __name__ == '__main__':
    pass