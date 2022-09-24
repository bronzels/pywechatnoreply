# -*- coding: utf-8 -*-
import plotly.graph_objs as go
import plotly.figure_factory as ff
from bs4 import BeautifulSoup,Tag
import pandas as pd
import numpy as np
from libpycommon.common.modeltest import Classification_metrics
from sklearn.metrics import precision_recall_fscore_support
colnames=['销售咨询','学习规划','时间安排','上课工具','教师问题',
       '获利咨询','售后咨询','地址反馈','信息反馈','其他咨询',
       '打招呼','拒绝结束','考虑结束','结束-跟进','结束-不跟',
       '找帮忙','祝福鸡汤','纯广告','闲聊','其他']
testfile = 'modelout_and_flag.xlsx'
reportfile = 'data/corpus/test_report.html'#reportfile
pref4bi = 'class2'
pref4mul = 'class20'
flag = 'flag'
sep = "_"
traits = '1'
re_sh = 202
staff_id=20

df_bak = pd.read_excel(testfile, "Sheet1")
class Pic_data():
    def __init__(self):
        self.x=['有员工&剔除正则', '有员工&有正则', '无员工&无正则', '无员工&有正则']
        self.name={
            'precision':[],
            'recall':[],
            'fscore':[],
        }
    def update(self,prfs_df):
        for i in prfs_df.index[:3]:
            self.name[i].append(prfs_df[1][i])
def re_is_right(df:pd.DataFrame):
    list_dict={k:df[k].tolist() for k in df.columns}
    re_idx=[1 if b>=staff_id and b<re_sh and c!=d else 0 for a,b,c,d in zip(list_dict[pref4mul+sep+flag],
                               list_dict[pref4mul+sep+traits],
                               list_dict[pref4bi+sep+flag],
                               list_dict[pref4bi+sep+traits],
                               )]

    list_dict[pref4bi + sep + flag]=[_ if not change else 1-_ for _,change in zip(list_dict[pref4bi+sep+flag],re_idx)]
    return pd.DataFrame(list_dict)
picdata=Pic_data()

# 1,有staff无re
df = df_bak.copy()
df = df[df[pref4mul+sep+traits] < 100]
picdata.update(Classification_metrics(df[pref4bi+sep+flag],df[pref4bi+sep+traits]).get_prfs_score())

# 2,有staff有re
df = df_bak.copy()
df=re_is_right(df)
picdata.update(Classification_metrics(df[pref4bi+sep+flag],df[pref4bi+sep+traits]).get_prfs_score())

# 3,无staff无re
df = df_bak.copy()
df = df[df[f"class20_{traits}"] < 100]
df = df[df[f"class20_flag"] < staff_id]

picdata.update(Classification_metrics(df[pref4bi+sep+flag],df[pref4bi+sep+traits]).get_prfs_score())

Classification_metrics(df[pref4mul+sep+flag],df[pref4mul+sep+traits]).draw_html_bar(reportfile,flag_names=colnames,title='深度模型多类指标(剔除员工与正则样本)',start=0.35)

Classification_metrics(df[pref4mul+sep+flag],df[pref4mul+sep+traits]).draw_html_matrix(reportfile,flag_names=colnames,title='深度模型多类错误分布(剔除了结束跟进与否)',
                                                                                       only_errors=True,mask_tuples=[(13,14),(14,13)])

#4无staff有re
df=df_bak.copy()
df=re_is_right(df)
df=df[df[f"class20_flag"]!=staff_id]
picdata.update(Classification_metrics(df[pref4bi+sep+flag],df[pref4bi+sep+traits]).get_prfs_score())

trace = [go.Bar(
    x=picdata.x,
    y=picdata.name[key],
    name=key,
    text=[round(f, 3) for f in picdata.name[key]], textposition="auto")
    for _, key in enumerate(picdata.name.keys())]
fig=go.Figure(data=trace,layout=go.Layout(
        title='二分类按条件测试图',
        yaxis=dict(range=[0.85, 1.0])))
Classification_metrics.dump_file(reportfile,fig)