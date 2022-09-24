# -*- coding: utf-8 -*-

import re
import pandas as pd

class Hit_regs:
    def __init__(self,reg_dict):
        self.reg_dict=reg_dict
        self.pat_dict={k:re.compile(v) for k,v in reg_dict.items()}
        """
        #dict示意
        reg_dict={'有数字':r'\d',
                '有小写字母':r'[a-z]'}
        """
    def scan_strings(self,str_list,hits=None,return_df=False,none_label=''):
        if not hits:
            hits=self.pat_dict.keys()
        outlist=[{k:1 if re.search(self.pat_dict[k],_) else 0 for k in hits} for _ in str_list]
        if return_df:
            return pd.DataFrame(outlist)
        if none_label:
            return [self.find_label(_,none_label) for _ in outlist]
        return outlist
    def compress_redup(self,str_list,dup_words):pass

    def find_label(self,label_dict,none_label):
        for k,v in label_dict.items():
            if v:
                return k
        return none_label