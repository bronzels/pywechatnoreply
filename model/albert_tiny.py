# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import os
os.environ['TF_KERAS']='1'
from bert4keras.backend import keras, set_gelu
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from tensorflow.keras.layers import Lambda, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences

from model.albert_tiny_config import *

class Model():
    def __init__(self, is_batch=False):
        self.tokenizer = Tokenizer(vocab_path, do_lower_case=True, word_maxlen=256)
        self.model = self._get_model()
        self.is_batch = is_batch

    def _get_model(self):
        set_gelu('tanh')
        bert = build_transformer_model(
            config_path=config_path,
            model='roberta',
            return_keras_model=False,
        )
        output = Lambda(lambda x: x[:, 0], name='CLS-token')(bert.model.output)
        output = Dense(
            units=4,
            activation='softmax',
            kernel_initializer=bert.initializer
        )(output)
        model = keras.models.Model(bert.model.input, output)
        model.load_weights(weights_path)
        return model


    def _get_tensor(self, input):
        if self.is_batch:
            tup=[self.tokenizer.encode(_[0],_[1], maxlen=256) for _ in input]
        else:
            tup=[self.tokenizer.encode(input[0],input[1], maxlen=256)]

        return [pad_sequences([_[0] for _ in tup], maxlen=256, padding='post'),
                pad_sequences([_[1] for _ in tup], maxlen=256, padding='post')]

    def _get_biclassifier_it(self, tuple,sh=0.3):
        #print(tuple)
        a = tuple[0]
        b = tuple[1]
        if a > 0.9:
            return 0
        elif b > 0.9:
            return 1
        else:
            return -1

    def _get_biclassifier_single(self, output):
        #print(output)
        return self._get_biclassifier_it(output[0])

    def _get_biclassifier_batch(self, output):
        print(output)
        return [self._get_biclassifier_it(tuple) for tuple in output]

    def predict(self, input):
        predicted = self.model.predict(self._get_tensor(input))
        if self.is_batch:
            return self._get_biclassifier_batch(predicted)
        else:
            return self._get_biclassifier_single(predicted)


if __name__ == '__main__':#01
    model = Model()
    print(model.predict('{"text":"你好，请问是想咨询英语选课问题吗？"}'))

    print(model.predict('{"text":"开启了朋友验证，你还不是他（她）朋友。请先发送朋友验证请求，对方验证通过后，才能聊天"}'))
    print(model.predict('{"text":"好的"}'))
    model = Model(True)
    print(model.predict(['{"text":"你好，请问是想咨询英语选课问题吗？"}',
                         '{"text":"开启了朋友验证，你还不是他（她）朋友。请先发送朋友验证请求，对方验证通过后，才能聊天"}',
                         '{"text":"好的"}']))
    """
    [[0.04619871 0.9538013 ]]
    """
    # inpt=[np.array([[101, 2940, 741, 6206, 3724, 2145, 2787, 5632, 2346, 6934, 2164,
    #          1168, 1266, 776, 8024, 1045, 6934, 6589, 2218, 4685, 2496, 754,
    #          741, 6589, 8024, 6820, 3300, 2553, 6206, 2940, 1408, 8024, 3173,
    #          743, 671, 3315, 679, 3291, 1962, 1408, 8024, 872, 812, 6821,
    #          3416, 4638, 3302, 1218, 2523, 6375, 782, 1927, 3307, 511, 102,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0],
    #         [101, 722, 1184, 671, 4684, 4761, 6887, 1744, 2110, 722, 7028,
    #          6206, 8024, 738, 4692, 749, 679, 2208, 741, 8024, 852, 3221,
    #          5632, 794, 2458, 1993, 6438, 6821, 3315, 741, 722, 1400, 8024,
    #          2798, 3918, 3918, 1765, 2697, 6230, 1168, 1071, 2141, 1744, 2110,
    #          3221, 1963, 3634, 4638, 2487, 1920, 4638, 1557, 8013, 2769, 4385,
    #          1762, 6438, 1920, 753, 8024, 809, 1184, 6438, 4638, 1744, 2110,
    #          6598, 3160, 1920, 1914, 6963, 3221, 2418, 802, 5440, 6407, 8024,
    #          852, 3221, 6821, 3315, 8024, 6438, 6629, 3341, 1146, 1912, 3300,
    #          2697, 6230, 511, 4638, 4802, 8024, 741, 704, 6382, 4638, 6887,
    #          4415, 2523, 1914, 1071, 2141, 3221, 6929, 720, 4638, 100, 5042,
    #          1296, 100, 8024, 852, 3221, 6206, 976, 1168, 8024, 2553, 7557,
    #          794, 3680, 671, 1921, 976, 6629, 102]]),
    #  np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])]
