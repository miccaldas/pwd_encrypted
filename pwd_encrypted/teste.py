"""Module Docstring"""
import pickle
import random
import string

import snoop
from cryptography.fernet import Fernet
from db_decorator.db_information import db_information
from english_words import get_english_words_set
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


@db_information
@snoop
def teste():
    """"""
    word_lst = get_english_words_set(["gcide"])
    wordlst = list(word_lst)
    print(len(word_lst))
    print(type(word_lst))
    punctuation = string.punctuation
    print(len(punctuation))
    print(type(punctuation))

    wds = random.choices(wordlst, k=4)
    print(wds)
    pct = random.choices(punctuation, k=3)
    print(pct)
    sam = wds + pct
    print(sam)
    samp = random.sample(sam, 6)
    sampe = " ".join(samp)
    sample = sampe.replace(" ", "")
    print(sample)


# if __name__ == "__main__":
#  teste()


@db_information
@snoop
def crypto():
    master_key = Fernet.generate_key()
    with open("mk.bin", "wb") as f:
        pickle.dump(master_key, f)

