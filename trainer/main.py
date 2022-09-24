# -*- coding: utf-8 -*-
import os
import shutil
from trainer.uilts import *
import tensorflow as tf
def entry(out_path,mul_gpu,num_class,model_type,gpu_id):
    if gpu_id>-1:
        gpus = tf.config.experimental.list_physical_devices(device_type='GPU')
        tf.config.experimental.set_visible_devices(devices=gpus[gpu_id], device_type='GPU')

    out_path=DATA_PATH + f'/pretrainedmodel/out/{model_type}/{out_path}/'
    shutil.copy(vocab_path, out_path)
    shutil.copy(config_path, out_path)

    df = get_corpus()
    df.fillna('', inplace=True)

    train_data = df.sample(frac=1)
    if num_class == 2:
        train_data['flag'] = train_data['flag'].map(yes_no_map)
    if mul_gpu:
        dataset, val_dataset = get_train_data(train_data,mul_gpu=mul_gpu,num_class=num_class)
        model=get_model_mul(loss=tf.losses.categorical_crossentropy,
            num_classes=num_class,config_path=config_path)
        saver = Saver(model, out_path)
        model.fit(
            dataset,
            validation_data=val_dataset,
            steps_per_epoch=2000,
            epochs=epochs,
            callbacks=[saver],
        )
    else:
        train_gen, test_gen = get_train_data(train_data, False,num_class=num_class)
        model = get_model_single(
            loss=mul_focal(2., 0.25),
            learning_rate=5e-5,
            lr_schedule={len(train_gen) * 1: 1, len(train_gen) * 3: 0.1},
            num_classes=num_class,
            model='roberta',
            config_path=config_path
        )
        evaluator = Evaluator(test_gen, model, out_path, ifidx=False)
        model.fit(
            train_gen.forfit(),
            steps_per_epoch=len(train_gen),
            epochs=epochs,
            callbacks=[evaluator],
        )





if __name__ == '__main__':
    entry()

