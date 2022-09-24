# -*- coding: utf-8 -*-
import zhconv
def strT2S(traditional_words):
    return zhconv.convert(traditional_words,'zh-cn')

def strQ2B(ustring):
    rstring = ''
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring