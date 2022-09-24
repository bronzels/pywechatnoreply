# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
testfile='test5.xlsx'
pref4bi='class2'
pref4mul='class20'
flag='flag'
sep="_"
traits=7
re_sh=202
out_path='data/corpus/'
sure_re=21
unsure_re=22
def dump_metrics(df,out_path='',suff="",with_re=False,with_staff=False):
    results = []
    for mode in [pref4bi,pref4mul]:
        for trait in range(1,traits+1):
            y_flag=[_ if _<re_sh else unsure_re for _ in df[f'{mode}{sep}{flag}'].tolist()]
            y_pred=[_ if _<re_sh else unsure_re for _ in df[f'{mode}{sep}{trait}'].tolist()]
            y_flag=[_ if _<100 else sure_re for _ in y_flag]
            y_pred=[_ if _<100 else sure_re for _ in y_pred]
            y_flag=[sure_re if prd==sure_re else gt for gt,prd in zip(y_flag,y_pred)]
            maxflag=max(y_flag+y_pred)+1
            prfs = precision_recall_fscore_support(y_flag,y_pred)
            result = {}
            for i, _ in enumerate(zip(*prfs)):
                result[i] = _
            result_df = pd.DataFrame(result)#,columns=['acc','recall','f1','sup']
            result_df.index = [f'{suf}_trait{trait}' for  suf in ['acc','recall','f1','sup']]
            results.append(result_df)
            if mode==pref4mul:
                tmp_df=None
                #errors_df=df[df[f'{mode}{sep}{flag}']!=df[f'{mode}{sep}{trait}']][[f'{mode}{sep}{flag}',f'{mode}{sep}{trait}']]
                errors_df=[(gt,prd) for gt,prd in zip(y_flag,y_pred) if gt!=prd]
                tmp_arr=np.zeros((maxflag,maxflag))
                for GT,PRD in errors_df:
                    tmp_arr[GT,PRD]+=1
                tmp_df=pd.DataFrame(tmp_arr)
                tmp_df.index=[f'flag_{_}' for _ in range(maxflag)]
                tmp_df.columns=[f'pred_{_}' for _ in range(maxflag)]
                if with_staff and with_re:
                    tmp_df.to_excel(out_path+f'trait{trait}_errors.xlsx')
    df_mul=pd.concat([_ for _ in results if _.shape[1]>2])
    df_bi=pd.concat([_ for _ in results if _.shape[1]==2])
    df_mul.sort_index().to_excel(out_path+f'df_mul_arfs{suff}.xlsx')
    df_bi.sort_index().to_excel(out_path+f'df_bi_arfs{suff}.xlsx')
if __name__ == '__main__':

    df_bak=pd.read_excel(testfile,"Sheet1")
    #1,有staff无re
    df=df_bak.copy()
    df=df[df[f"class20_{traits}"]<100]
    dump_metrics(df,out_path=out_path,suff='_staff',with_staff=True)
    #2,有staff有re
    df=df_bak.copy()
    dump_metrics(df,out_path=out_path,suff='_staff_re',with_re=True,with_staff=True)
    #3,无staff有re
    df=df_bak.copy()
    df=df[df[f"class20_flag"]!=20]
    dump_metrics(df,out_path=out_path,suff='_re',with_re=True)
    #4,无staff无re
    df=df_bak.copy()
    df=df[df[f"class20_{traits}"]<100]
    df=df[~df[f"class20_flag"]!=20]
    dump_metrics(df,out_path=out_path,suff='')


