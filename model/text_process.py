# -*- coding: utf-8 -*-
import json
import os
import re
import numpy as np
from model.rbt3_config import *
from libpytext.model.mybert4keras import get_subwords
from libpytext.common.myreg import *
from libpytext.common.mystring import *
from model.myreg import *
from model.rbt3_config import rbt3_mul_conf,asr_cache
from libpytext.common import iflyasr


def p_token(fromsymbol='[]',tosymbol='【】',nohit='表情',sp_words=sp_words,vocab_path=rbt3_mul_conf['vocab_path'])->list:
    def inner(s:str):
        reg=f'(\{fromsymbol[0]}.*?\{fromsymbol[-1]})'
        txts=re.split(reg,s)
        toks=[]
        for _ in txts:
            if not _:
                continue
            elif _[0]==fromsymbol[0] and _[-1]==fromsymbol[1]:
                if _[1:-1].lower() in sp_words:
                    toks.append(tosymbol[0]+_[1:-1]+tosymbol[-1])
                elif _[1:-1].lower() in emoji_tab:
                    toks.append(tosymbol[0]+nohit+tosymbol[-1])
                else:
                    toks += get_subwords(_,vocab_path)
            else:
                toks+=get_subwords(_,vocab_path)
        return toks
    return inner


def unsolved_idx(df,target='predict'):
    return df[df[target] == tbd_label].index.tolist()

def do_regs(datalist):
    unsolved_data = [(_[0], strT2S(strQ2B(_[1]))) for _ in datalist]
    for i, (idx, text) in enumerate(unsolved_data):
        # sub_regs
        for k, v in sub_regs.items():
            text = re.sub(v, k, text)
        # overlap_reg
        text = re.sub(overlap_reg, r'\1', text)
        text = re.sub(overlap_emoji, r'\1', text)
        # none_reg
        text = re.sub(none_reg, "", text)
        text = re.sub(';+', ";", text)

        unsolved_data[i] = (idx, text.strip().strip('，。；:;,~…!、').lower())
    return unsolved_data



def find_txt_from_frag(frag_text,start=9):
    segs=re.split('|'.join(msg_keys),frag_text)
    for _ in segs:
        if 'text' in _:
            return _[start:].strip()
    return ''

def map_urls(url):
    if url:
        return f'[媒体]'#{url}
    else:
        return ''

def text_scene_detecter(s:str,d:dict,role=None):
    for _ in d:
        if re.search(d[_][0],s) and len(s)>d[_][1]:
            if not role:
                return _
            elif role=='custtext':
                continue
            elif role == 'stafftext':
                return _
            else:pass
    return s



def matchedscene(d:dict,scene:str):
    scenes = scene.split('|')
    if set(d.keys())==set(scenes):
        return True
    else:return False


def summary_scene(d:dict,role=None):
    keys=d.keys()
    if matchedscene(d,'url'):
        txt=d.get('url','')
        if '.qpic.' in txt:
            return '[独立表情]'
        if re.search('^http.*?mp3$',txt):#这里是微信音频应该
            asres=iflyasr.get_asr(txt,asr_cache)
            if not asres:
                return '[音频]'
            else:
                return asres
        if re.search('mp4$',txt):
            return '[视频]'
        if re.search('(png|jpg|gif)$',txt):
            return '[图片]'
        if not txt:
            return ''
        return '[独立链接]'
    if matchedscene(d,'text|url'):
        if re.search(r'^'+sub_regs['[链接]']+r'$',d.get('text','')):
            return summary_scene({'url':d.get('text','')})
        else:
            return d.get('text','')
    if matchedscene(d,'des|title|type'):
        return d.get('title','')

    #这里要加入纯文本场景的识别
    if matchedscene(d,'text'):
        tmp_text=d.get('text','')
        if 'href=' in tmp_text:
            tmp_text = re.sub('&lt;.*?&gt', "", tmp_text)
        return text_scene_detecter(tmp_text,pure_text_map,role)

    if matchedscene(d,'attachtype|text|thumb'):
        if d.get('thumb',''):
            return summary_scene({'url':d.get('thumb','')})
        else:
            return ''

    if matchedscene(d,'comment|text'):
        return ''


    if matchedscene(d,'attachtype|text|thumb|url'):
        if d.get('url').endswith('mp4'):
            return '[视频]'
        # if 'qc-20181213.oss-cn-shenzhen.aliyuncs.com' in d.get('url'):
        #     return '[阿索卡图片]'
        return '[图片]'

    if 'alias' in keys and 'certflag' in keys:
        return '[名片]'
    if 'fee' in keys or 'feedesc' in keys:
        return '[红包转账]'
    if d.get('message','').startswith('您领取了'):
        return '[红包转账]'
    if matchedscene(d,'href|imgSrc|text|type') or\
    matchedscene(d,'amount|headTitle|recAmount|sendId|statusMess|totalAmount|totalNum|type') or \
    matchedscene(d,'nativeurl|paymsgid|sendertitle'):
        return '[红包转账]'


    if matchedscene(d,'attachtype|text|url'):
        return '[截图]'

    if matchedscene(d,'chatusr|content|displayname|fromusr|svrid|title'):
        return '[引用]【'+d.get('title','')+'】'
    if matchedscene(d,'appname|attachUrl|des|sourceusername|title|totalLen|type|url|weappinfotype') or\
        matchedscene(d,'appname|des|title|totalLen|type|url|weappinfotype') or\
            matchedscene(d,'appname|attachUrl|des|sourcedisplayname|title|totalLen|type|url|weappinfotype') or\
            matchedscene(d,'appname|attachUrl|des|title|totalLen|type|url|weappinfotype'):
        return d.get('title')


    if 'fromUsername' in keys or 'location' in keys:
        return '[位置共享]'
    if d.get('weappiconurl','') or matchedscene(d,'title|type|url'):
        getitle=d.get('title','')
        if re.search('[a-zA-Z0123456789\-]{36}',getitle) or re.search('[a-zA-Z0123456789]{32}',getitle):
            return '[文件]【】'
        else:
            return '[文件]【'+getitle+'】'
    if matchedscene(d,'type|url'):
        if d.get('type','') in (6,'6'):
            try:
                getitle = d.get('url','').split('/')[-1].split('.')[0]
                if re.search('[a-zA-Z0123456789\-]{36}', getitle) or re.search('[a-zA-Z0123456789]{32}', getitle):
                    return '[文件]【】'
                else:
                    return '[文件]【'+getitle+'】'
            except:
                pass
        else:
            return ''
    if matchedscene(d,'msgsource|text'):
        return d.get('text','')
    if 'url' in '|'.join(keys).lower():
        return '[独立链接]'

    if 'text' in keys and d.get('text',''):
        return d.get('text','')
    else:
        return ''



def dict_parser(long_text:str,sep='$￥$',order=1,role=None):
    textlist=[]
    long_text=str(long_text).strip()
    text_dicts = long_text.split(sep)[::order]
    for text_dict in text_dicts:
        try:
            #tmpdict=eval(text_dict)
            tmpdict=json.loads(text_dict.replace('\n','\\n').replace('\r','\\r').replace('\t','\\t'))
            tmptext=summary_scene(tmpdict,role)
            #tmptext=tmpdict.get('text', '')
            if not tmptext and tmpdict.get('url', '') :
                tmptext=map_urls(tmpdict.get('url', ''))
        except:
            if 'href=' in text_dict:
                text_dict=re.sub('&lt;.*?&gt',"", text_dict)
            tmptext=find_txt_from_frag(text_dict)
        if tmptext:
            textlist.append(tmptext)
    return textlist



def regfilter(batch_list,list_batch=True,labelmap=None,raw=False,with_flag=False,hiter=None):
    cols=['id','stafftext','custtext','flag'] if with_flag else ['id','stafftext','custtext']
    #cols=['id','custtext','stafftext','flag'] if with_flag else ['id','custtext','stafftext']
    if list_batch:
        df=pd.DataFrame(batch_list,columns=cols)
    else:
        df=batch_list
        df.columns=cols
    textslist = [dict_parser(_) for _ in df.custtext]
    df['predict'] = hiter.scan_strings([_[-1] if _ else "" for _ in textslist],
                                       hits=['拉黑','招呼','无意','通话','红包转账','拒接','企微转友'],
                                       none_label=tbd_label)

    text_data={
        'custtext':[],
        'stafftext':[]
    }

    for c in text_data:
        unsolved_index = unsolved_idx(df)
        textslist = [dict_parser(_,role=c) for _ in df.iloc[unsolved_index][c]]
        for i, _ in zip(unsolved_index, textslist):
            results = hiter.scan_strings(_, none_label='保留')
            text_data[c].append(
                (i, (';'.join([j if i == '保留' else "[" + i + "]" for i, j in zip(results, _)])).strip()))
        text_data[c] = do_regs(text_data[c])
        if c == 'custtext':
            df.loc[[_[0] for _ in text_data[c] if re.match(no_text_reg, _[1])], "predict"] = '无文本'
            df.loc[[_[0] for _ in text_data[c] if re.match(senseless_reg, _[1])], "predict"] = '无意'
            df.loc[[_[0] for _ in text_data[c] if re.match(senseless_regs, _[1])], "predict"] = '无意'

    # unsolved_index = unsolved_idx(df)
    # unsolved_data=[]
    # #特殊文本体替换
    # for i in unsolved_index:
    #     results = hiter.scan_strings(textslist[i], none_label='保留')
    #     unsolved_data.append((i, (';'.join([j if k == '保留' else "[" + k + "]" for k, j in zip(results, textslist[i])])).strip()))
    #
    #
    # unsolved_data = do_regs(unsolved_data)##节点
    #
    # df.loc[[_[0] for _ in unsolved_data if re.match(senseless_reg, _[1])], "predict"] = '无意'
    # #df.loc[[_[0] for _ in unsolved_data if re.match(r'^[(\[媒体\])|\s\;\.\,\~\"\'。，…]{0,}\[媒体\][(\[媒体\])|\s\;\.\,\~\"\'。，…]{0,}$',_[1])], "predict"] = '媒体'
    # #cant_solved_data_staff
    # df.loc[[_[0] for _ in unsolved_data if re.match(no_text_reg, _[1])], "predict"] = '无文本'

    #返回为能里处理的结果
    # unsolved_index = unsolved_idx(df)
    # #只要这部分的客服发言
    # textslist = [dict_parser(_) for _ in df.iloc[unsolved_index].stafftext]
    # unsolved_data_staff=[]
    # for i,_ in zip(unsolved_index,textslist):
    #     results = hiter.scan_strings(_, none_label='保留')
    #     unsolved_data_staff.append((i, (';'.join([j if i == '保留' else "[" + i + "]" for i, j in zip(results, _)])).strip()))
    #
    # unsolved_data_staff = do_regs(unsolved_data_staff)##节点

    if not raw:#这里的raw只是消息体格式的raw
        df.loc[unsolved_index,'custtext']=np.array([_[1] for _ in text_data['custtext'] if _[0] in unsolved_index])
        df.loc[unsolved_index,'stafftext']=np.array([_[1] for _ in text_data['stafftext']])


    arr_reg=df[df.predict!=tbd_label].drop(['custtext','stafftext'],axis=1)
    if labelmap:
        arr_reg['predict']=arr_reg['predict'].map(labelmap)

    arr_tbd=df[df.predict==tbd_label].drop('predict',axis=1)

    return arr_reg.to_numpy(),arr_tbd.to_numpy()




if __name__ == '__main__':
    h=Hit_regs(formed_regs)
    sample=[
        #['a','{"text":"你好，请问是想咨询英语选课问题吗？"}','{"text":"yes"}',],
     ['b',
'{"text":"618年中大促，狂欢购课节\n活动时间：2012.6.4~6.18\n活动期间，购课实付满3000元起，100/200/300礼品卡免费送，\n活动期间   购满3000元可参与抽奖好礼享不停，\n活动期间   京东购买课程享额外优惠卷\n活动期间   报名可以参与0利息0首付教育分期   花呗信用卡京东白条分期免息\n活动期间   即可延迟到半年之内任意时间段开课\n火爆6月，让流利口语说出来\n试听请回复：1\n报名请回复：2\n续课请回复：3\n（群发若有打扰请见谅，已经报名或续课请忽略此消息）详情请私聊\n活动时间：6.18最后一天，过期不候","url":"618年中大促，狂欢购课节\n活动时间：2012.6.4~6.18\n活动期间，购课实付满3000元起，100/200/300礼品卡免费送，\n活动期间   购满3000元可参与抽奖好礼享不停，\n活动期间   京东购买课程享额外优惠卷\n活动期间   报名可以参与0利息0首付教育分期   花呗信用卡京东白条分期免息\n活动期间   即可延迟到半年之内任意时间段开课\n火爆6月，让流利口语说出来\n试听请回复：1\n报名请回复：2\n续课请回复：3\n（群发若有打扰请见谅，已经报名或续课请忽略此消息）详情请私聊\n活动时间：6.18最后一天，过期不候"}',
'{"text":"618年中大促，狂欢购课节\n活动时间：2012.6.4~6.18\n活动期间，购课实付满3000元起，100/200/300礼品卡免费送，\n活动期间   购满3000元可参与抽奖好礼享不停，\n活动期间   京东购买课程享额外优惠卷\n活动期间   报名可以参与0利息0首付教育分期   花呗信用卡京东白条分期免息\n活动期间   即可延迟到半年之内任意时间段开课\n火爆6月，让流利口语说出来\n试听请回复：1\n报名请回复：2\n续课请回复：3\n（群发若有打扰请见谅，已经报名或续课请忽略此消息）详情请私聊\n活动时间：6.18最后一天，过期不候","url":"618年中大促，狂欢购课节\n活动时间：2012.6.4~6.18\n活动期间，购课实付满3000元起，100/200/300礼品卡免费送，\n活动期间   购满3000元可参与抽奖好礼享不停，\n活动期间   京东购买课程享额外优惠卷\n活动期间   报名可以参与0利息0首付教育分期   花呗信用卡京东白条分期免息\n活动期间   即可延迟到半年之内任意时间段开课\n火爆6月，让流利口语说出来\n试听请回复：1\n报名请回复：2\n续课请回复：3\n（群发若有打扰请见谅，已经报名或续课请忽略此消息）详情请私聊\n活动时间：6.18最后一天，过期不候"}',
     #['c','{"text":"开启了朋友验证，你还不是他（她）朋友。请先发送朋友验证请求，对方验证通过后，才能聊天"}','{"text":"yes"}']
            ]]
    arr1,arr2=regfilter(sample,hiter=h,labelmap=formed_regs_map)
    print(arr2)
    # from model.rbt3 import Model
    # m=Model()
    # m.predict([_[1:] for _ in arr2.tolist()])
    pass