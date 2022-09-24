# -*- coding: utf-8 -*-
import sys
import os
projpath=os.path.abspath(__file__+'../../../')
sys.path.append(projpath)
import unittest
import re
import pandas as pd
from model.myreg import formed_regs,sub_regs,overlap_reg,overlap_emoji,pure_text_map
from libpytext.common.myreg import Hit_regs
from model.text_process import regfilter
from libpycommon.common import htmltest
class MyclassTest(unittest.TestCase):

    def test01_formed_regs(self):
       # df=pd.read_excel(os.path.basename(corpus)+'/corpusfixed.xlsx')
        df=pd.DataFrame({
            'id':['拉黑','招呼','无意','通话','红包转账','拒接','提示','企微转友','忽略'],
            'stafftext':['']*9,
            'custtext':['{"text":"邓留兴开启了朋友验证，你还不是他（她）朋友。请先发送朋友验证请求，对方验证通过后，才能聊天。"}',
                        '{"text":"以上是打招呼的内容"}',
                        '{"text":"邱雅惠 将此好友从 lolo@acadsoc.com(邱雅惠) 转给 Ulrica@acadsoc.com(肖雲键),附言","comment":""}',
                        '{"text":"voip_content_voice聊天时长 02:18"}',
                        '{"text":"好的"}￥$￥{"href":"weixin://weixinhongbao/opendetail?sendid=1000039901202104216129800725198","imgSrc":"SystemMessages_HongbaoIcon.png","text":"听语、领取了你的红包","type":1}',
                        '{"text":"voip_content_voice已拒绝"}',
                        '{"text":"好的"}￥$￥{"text":"对方帐号异常，已被限制登录，消息无法送达"}',
                        '{"text":"由于工作变更，$heirname$将在24小时后添加为你的企业微信联系人，接替 $originname$ 继续为你提供服务。\n$switch$"}',
                        '{"text":"我说了什么不重要，重要的是不要回复"}'
                        ],
        })
        tup_records=[(row[0],row[1],row[2])for row in df.values]
        hit_regs=Hit_regs(formed_regs)
        arr1, _ = regfilter(tup_records, hiter=hit_regs)
        #df['reg_result']=df.id.map({i:j for i,j in arr1.values})
        self.assertTrue((arr1[:,0]==arr1[:,1]).sum(),len(df))
    def test02_sub_regs(self):
        text="你好,分享一个资料链接:http://pan.baidu.com/s/1jI9BrQA 提取码:a6rv，"
        for k, v in sub_regs.items():break
        text = re.sub(v, k, text)
        self.assertIn(k,text)
        #print(text)
    def test03_overlap_regs(self):
        text1="=========##########!!!!!!!!!!!!!!!!!!!"
        text2='[微笑][微笑][微笑][微笑][微笑][抱拳][抱拳][抱拳][抱拳][抱拳]'
        self.assertTrue(len(re.sub(overlap_reg,r'\1',text1))==len(set(text1)))
        self.assertTrue(len(re.sub(overlap_emoji,r'\1',text2).split(']['))==len(set(text2.strip('[]').split(']['))))
    def test04_pure_text_regs(self):
        text="你好,𝙂𝙤𝙤𝙙 𝙢𝙤𝙧𝙣𝙞𝙣𝙜,已为您预约了英语课程，请注意查看，需要的可以回复：1，告诉我" \
             "这是群发短信，如果打扰，请多多见谅，字数补丁字数补丁字数补丁字数补丁字数补丁字数补丁" \
             "字数补丁字数补丁字数补丁字数补丁字数补丁字数补丁字数补丁字数补丁字数补丁字数补丁字数补丁"
        for reg, minlen in pure_text_map.values():
            self.assertTrue(re.search(reg,text) and len(text)>minlen)


#添加Suite
def Suite():
    #定义一个单元测试容器
    suiteTest = unittest.TestSuite()
    suiteTest.addTest(MyclassTest("test01_formed_regs"))
    suiteTest.addTest(MyclassTest("test02_sub_regs"))
    suiteTest.addTest(MyclassTest("test03_overlap_regs"))
    suiteTest.addTest(MyclassTest("test04_pure_text_regs"))
    return suiteTest

if __name__ == '__main__':
    # suite = unittest.TestSuite()
    # suite.addTests([MyclassTest('test01_formed_regs'),MyclassTest('test02_sub_regs'),MyclassTest('test03_overlap_regs')])
    filePath =projpath+'/data/corpus/test_report.html'
    fp = open(filePath,'wb')
    runner = htmltest.HTMLTestRunner(
        stream=fp,
        title='模型自测报告',
        tester='cenix'
        )
    runner.run(Suite())
    fp.close()