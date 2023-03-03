"""Module Docstring"""
import os
import pickle
import sqlite3
import subprocess
import sys

import snoop
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from pythemis.skeygen import GenerateSymmetricKey
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


# @db_information
@snoop
def test():
    """"""
    with open("/home/mic/themis_key/key.bin", "rb") as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)

    with open("/home/mic/themis_key/pwd/decrypt_info.bin", "rb") as g:
        decrypt_info = pickle.load(g)
    with open("decript_info.bin", "rb") as g:
        dec_info = pickle.load(g)

    try:
        dec = cell.decrypt(dec_info[0], dec_info[1])
        dec_val = dec_info[1].decode("latin-1")
        decrypted = cell.decrypt(decrypt_info[0], decrypt_info[1])
        decrypted_val = int.from_bytes(decrypt_info[1], sys.byteorder())
    except ThemisError as e:
        print(e)

    pwd_str = decrypted.decode("UTF-8")


if __name__ == "__main__":
    test()
