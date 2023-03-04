"""
Module that decrypts a column encrypted content
using the Themis module.
"""
import os
import pickle
import sqlite3
import subprocess
import sys

import snoop
from dotenv import load_dotenv
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError

from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()


@snoop
def decrypt_column():
    """
    Unpickles the themis key and the list of
    tuples the 'encrypt_column' made available
    through the 'decrypt_info.bin' file,
    decrypts it and turns the results to string.
    """

    # Variables defined in the .env file at the top
    # of the project tree.
    res_pth = os.getenv("PWD_SEC_LOC")
    enc_key = os.getenv("PWD_KEY_LOC")
    decinfo = os.environ.get("PWD_DECINFO_LOC")

    # Gets the 'pwd' database Themis key and creates
    # a 'cell' variable, needed for decrypting.
    with open(f"{enc_key}", "rb") as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)

    # Multiple entries to same pickle file, should be
    # done through list, dictionary or similar iterable.
    entries = []
    with open(f"{decinfo}", "rb") as f:
        while True:
            try:
                entries.append(pickle.load(f))
            # When iterating through Pickle, it sends a
            # an error message when it gets to end of the
            # list, and keeps sending it non-stop. This
            # avoids that situation.
            except EOFError:
                break
    # Pickles returns a list within a list. This flattens it.
    decrypt_info = [i for sublst in entries for i in sublst]

    pwd_bytes = []
    try:
        for tup in decrypt_info:
            dec = cell.decrypt(tup[0], tup[1])
            # Converts a bytes object to integer. Remmeber that
            # the context value was not encrypted, just turned
            # into a bytes object.
            decrypted_val = int.from_bytes(tup[1], sys.byteorder)
            pwd_bytes.append((dec, decrypted_val))
    except ThemisError as e:
        print(e)

    # As the system encoding is 'pt_latin-1', so as to write and
    # get a portuguese configurated keyboard, we can't use the
    # default 'utf-8' for it'll not be able to decrypt what was
    # written. Always use 'latin-1' while decoding.
    pwd_str = [(i.decode("latin-1"), t) for i, t in pwd_bytes]


if __name__ == "__main__":
    decrypt_column()
