# -*- coding: utf-8 -*-
import glob
from bert4keras.tokenizers import load_vocab,Tokenizer
def get_subwords(text,vocab_path,word_maxlen=21128):
    token_dict=load_vocab(vocab_path)
    def word_piece(word):
        if len(word) > word_maxlen:
            return [word]

        tokens, start, end = [], 0, 0
        while start < len(word):
            end = len(word)
            while end > start:
                sub = word[start:end]
                if start > 0:
                    sub = '##' + sub
                if sub in token_dict:
                    break
                end -= 1
            if start == end:
                return [word]
            else:
                tokens.append(sub)
                start = end
        return tokens
    spaced = ''
    for ch in text:
        if Tokenizer._is_punctuation(ch) or Tokenizer._is_cjk_character(ch):
            spaced += ' ' + ch + ' '
        elif Tokenizer._is_space(ch):
            spaced += ' '
        elif ord(ch) == 0 or ord(ch) == 0xfffd or Tokenizer._is_control(ch):
            continue
        else:
            spaced += ch
    tokens = []
    for word in spaced.strip().split():
        tokens.extend(word_piece(word))
    return tokens


def checkpoint_finder(path:str):
    files=glob.glob(path+'/*')
    vocab_file=[_ for _ in files if _.endswith('txt')][0]
    json_file=[_ for _ in files if _.endswith('json')][0]
    weight_file=[_ for _ in files if '.weights.' in _ or '.ckpt.' in _][0].rsplit('.',1)[0]
    return vocab_file,json_file,weight_file