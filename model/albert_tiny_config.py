from libpycommon.common.misc import get_env
'''
vocab_path = '../data/vocab.txt'
config_path = '../data/albert_config.json'
weights_path = '../data/model.weights'
'''
BOOL_DEBUG_SWITCH = get_env('DEBUG_SWITCH', 'off') == 'on'
FILES_PATH_ROOT = None

if BOOL_DEBUG_SWITCH:
    from data.pywechatnoreply import albert_tiny

    path = albert_tiny.__file__
    FILES_PATH_ROOT = path[0:path.find('__init__.py')-1]
else:
    FILES_PATH_ROOT = '/data1/www/analysis_group/pywechatnoreply/albert_tiny'
model_rev = get_env('MODEL_REV')
if model_rev != '':
    FILES_PATH_ROOT = FILES_PATH_ROOT + '/' + model_rev
vocab_path = FILES_PATH_ROOT + '/vocab.txt'
config_path = FILES_PATH_ROOT + '/albert_config.json'
weights_path = FILES_PATH_ROOT + '/model.weights'
