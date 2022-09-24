from libpycommon.common.misc import get_env
import linecache
from libpytext.model.mybert4keras import checkpoint_finder
import os
import json
BOOL_DEBUG_SWITCH = get_env('DEBUG_SWITCH', 'off') == 'on'
FILES_PATH_ROOT = None
if BOOL_DEBUG_SWITCH:
    from data.pywechatnoreply import rbt3

    path = rbt3.__file__
    FILES_PATH_ROOT = path[0:path.find('__init__.py')-1]
else:
    FILES_PATH_ROOT = '/data1/www/analysis_group/pywechatnoreply/rbt3'
model_mul_rev = get_env('MODEL_MUL_REV')
model_bi_rev = get_env('MODEL_BI_REV')
if model_mul_rev != '':
    FILES_MUL_PATH_ROOT = FILES_PATH_ROOT + '/' + model_mul_rev
if model_bi_rev != '':
    FILES_BI_PATH_ROOT = FILES_PATH_ROOT + '/' + model_bi_rev

rbt3_mul_conf={k:v for k,v in zip(['vocab_path','config_path','weights_path'],checkpoint_finder(FILES_MUL_PATH_ROOT))}
rbt3_mul_conf.update({'batch_size':32,'num_classes':20,'maxlen':256})

rbt3_bi_conf = {k: v for k, v in zip(['vocab_path', 'config_path', 'weights_path'], checkpoint_finder(FILES_BI_PATH_ROOT))}
rbt3_bi_conf.update({'batch_size': 32, 'num_classes': 2,'maxlen':256})

tbd_label='TBD'

sp_words = [linecache.getline(rbt3_mul_conf['vocab_path'],_).strip()[1:-1] for _ in range(1,101) if linecache.getline(rbt3_mul_conf['vocab_path'],_)[0]=='【']

if os.path.exists('data/corpus/asr.json'):
    asr_cache=json.load(open("data/corpus/asr.json",'r'))
else:
    asr_cache=None

