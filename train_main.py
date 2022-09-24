# -*- coding: utf-8 -*-
# little change
import os
from trainer.main import entry
import argparse
PARSER = argparse.ArgumentParser()
PARSER.add_argument('--out_path')
PARSER.add_argument('--mul_gpu')
PARSER.add_argument('--num_class')
PARSER.add_argument('--model_type')
PARSER.add_argument('--gpu_id')

if __name__ == "__main__":
    args = PARSER.parse_args()
    entry(args.out_path,args.mul_gpu=='true',int(args.num_class),args.model_type,int(args.gpu_id))
    pass
"""
os.environ['TF_KERAS']='1'
os.environ['DEBUG_SWITCH']='on'
os.environ['MODEL_NAME']='rbt3'
os.environ['MODEL_MUL_REV']='mul_rel_202106240256'
os.environ['MODEL_BI_REV']='bi_rel_202106240256'
"""