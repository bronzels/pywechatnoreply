# -*- coding: utf-8 -*-
# EDA
import math
import jieba
import numpy as np
#import synonyms即会下载140M的词向量文件
import synonyms
import random
from random import shuffle
import pandas as pd
import re
import tqdm

#add_df=pd.DataFrame(columns=df.columns)
def get_synonyms(word,threshold=0.8):
    if word in single_words:
        return "",0
    res = synonyms.nearby(word)
    if not res[0]:
        return '',0.
    else:
        wp=[(w,p) for w,p in zip(res[0],res[1]) if p>threshold and w!=word]
    if wp:
        w,p=random.choice(wp)
        return w,p
    else:
        return '',0
    all_res.append((_,list()[1:4]))
    return synonyms.nearby(word)[0]
def do_eda(sentence,threshold=0.8,r=0.3):
    changed=0
    if sentence is np.nan:
        return ''
    seg_list = jieba.lcut(sentence)

    new_words = seg_list.copy()
    random_word_list = list(set([word for word in new_words if word not in stop_words and not re.search(r'[a-zA-Z\"\{\}【】\[\]\:\/]{1,}',word)]))
    #n_sr = max(1, math.ceil(random.random()*len(random_word_list)/5))
    #n_rd = max(1, math.ceil(random.random()*len(random_word_list)/5))
    for target_word in random_word_list:
        r_w,cos=get_synonyms(target_word)
        if cos>threshold and random.random()<r:
            new_words=[_ if _!=target_word else r_w for _ in new_words]
            changed+=1
        if target_word in stop_words and random.random()<r:
            new_words=[_ for _ in new_words if _!=target_word]
            changed+=1
    if changed>0:
        return ''.join(new_words)
    else:
        return ''

def do_del(sentence):
    changed=0
    if sentence is np.nan:
        return ''
    seg_list = jieba.lcut(sentence)

    new_words = seg_list.copy()
    out=''
    for _ in new_words:
        if re.search(r'[a-zA-Z\"\{\}【】\[\]\:\/]{1,}',_):
            out+=_
            continue

        if _ in stop_words and random.random()<0.3:
            changed+=1
            continue
        if random.random()<0.05:
            changed+=1
            continue
        else:
            out+=_
    if changed>0:
        return out
    else:
        return ''

if __name__ == '__main__':
    df = pd.read_excel('corpusfixed_0623.xlsx', sheet_name='Sheet1')
    # 停用词过滤减少计算时间，这里是用synonyms自带的词表
    stop_words = open(r'D:\softs\codes\anaconda\envs\py37test\lib\site-packages\synonyms\data\stopwords.txt',
                      encoding='utf8').readlines()
    stop_words = [_.strip() for _ in stop_words]
    # 手动添加不合适做同义词的词
    single_words = []
    df=df[df.source!='eda']
    df=df[~df.flag.isin(['多媒体','无意义','其他','其它','转换好友','删除好友','转好友','员工','员工聊撩','员工聊天',' 员工互聊','员工互聊'])]


    """
    #拿到所有的词,为了查看合适的阈值以及不适合做同义词的词
    allwords=set()
    for _ in tqdm.tqdm(df.stafftext.append(df.custtext)):
        if _ is np.nan:
            continue
        new_words = jieba.lcut(str(_))
        random_word_set = set([word for word in new_words if word not in stop_words and not re.search(r'[a-zA-Z0-9\.]{1,}',word)])
        allwords.update(random_word_set)


    all_res=[]
    for _ in tqdm.tqdm(allwords):#break
        res=synonyms.nearby(_)
        if not res[0]:
            continue
        all_res.append((_,list(zip(res[0],res[1]))[1:4]))

    res_df=pd.DataFrame(all_res)
    """



    #员工词
    stafftexts=[]
    for _ in df.stafftext:
        dts=str(_).split('$￥$')
        for dt in dts:
            try:
                d=eval(dt)
                if d.get('text',''):
                    stafftexts.append(dt)
                else:continue
            except:
                pass

    edas=[]
    for row in tqdm.tqdm(df.values):
        if row[3].startswith("赞同结束") and random.random()>0.005:
            continue
        if row[3] in '找帮忙祝福鸡汤纯广告闲聊' and random.random()>0.01:
            continue
        cust_eda=do_eda(row[2])
        if cust_eda:
            if row[1] is np.nan:
                edas.append((row[1],cust_eda,row[3]))
            else:
                staff_eda = do_eda(row[1])
                if staff_eda:
                    edas.append((staff_eda, cust_eda, row[3]))
                else:
                    edas.append((row[1], cust_eda, row[3]))
    #print('after replace',len(edas))
    for row in tqdm.tqdm(df.values):
        if row[3].startswith("赞同结束") and random.random()>0.005:
            continue
        if row[3] in '找帮忙祝福鸡汤纯广告闲聊' and random.random()>0.005:
            continue
        cust_eda=do_del(row[2])
        if cust_eda and random.random()>0.5:
            if row[1] is np.nan:
                edas.append((row[1],cust_eda,row[3]))
            else:
                staff_eda = do_del(row[1])
                if staff_eda:
                    edas.append((staff_eda, cust_eda, row[3]))
                else:
                    edas.append((row[1], cust_eda, row[3]))
    #print('after delete',len(edas))
    for row in tqdm.tqdm(df[df.flag.isin(['找帮忙','祝福鸡汤','纯广告'])].values):
        if row[1] is np.nan and random.random()<0.3:
            cust_eda = do_del(row[2])
            staff_eda= do_del(random.choice(stafftexts))
            edas.append((staff_eda, cust_eda, row[3]))
        else:
            pass
    #print('after ADS',len(edas))


    eda_df=pd.DataFrame(edas,columns=['stafftext','custtext','flag'])
    eda_df['source']='eda'
    eda_df['id']=[f"eda_{i:05d}" for i in range(1,len(eda_df)+1)]
    eda_df=eda_df[df.columns]
    eda_df=eda_df[eda_df.custtext.notna()]
    eda_df=eda_df[eda_df.custtext.str.len()>14]
    eda_df.to_csv('eda.csv',quoting=1)
    #手动审查后加入语料corpusfixed



