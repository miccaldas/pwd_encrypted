"""
It was created in the 'pwd' database, a new column, 'pwd', that
cloned of the "passwd" column, with the objective of housing the
new Themis encrypted, passwords. This module will do said
encryprion and update the database.
As this is a one off event, it's called by no one.
"""

import os
import pickle
import sqlite3
import subprocess

import snoop
from db_decorator.db_information import db_information
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from pythemis.skeygen import GenerateSymmetricKey
from snoop import pp

from configs.config import tput_config


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


@snoop
def encrypt():
    """
    We iterate through the passwords values in
    the datbase and create a '.bin' file with
    the id's and encrypted password of each
    entry. This file will be used in the next
    function as the source of a global update.
    """

    # Location of the Themis key.
    with open("/home/mic/themis_key/key.bin", "rb") as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)
        # We make available the 'cell' object, as it will
        # be necessary for any decryption duty.
        with open("cell.bin", "wb") as y:
            pickle.dump(cell, y)

    update_info = []
    # Sqlite3 prints callback on errors.
    sqlite3.enable_callback_tracebacks(True)
    conn = sqlite3.connect("pwd.db")
    cur = conn.cursor()
    query = "SELECT pwdid, pwd FROM pwd"
    for row in cur.execute(
        query,
    ):
        # Taking in account the existence of
        # null values in the 'pwd' column.
        if row[1] is None:
            # 'row' is a tuple, and tuples are immutable.
            # As we need to change the value of 'pwd' to
            # 'none', to avoid an error message, we need
            # to first convert it to a list, do the change,
            # and convert it back to tuple.
            lst = list(row)
            lst[1] = "null"
            row = tuple(lst)
            stri = row[1]
        if len(row[1]) > 1:
            stri = row[1]
        ints = row[0]
        # We are converting the old password strings to
        # encrypted bytes objects. As there were already
        # in the db, some entries with encrypted pwds,
        # an error message was being produced. This 'if'
        # clause avoids setting the message on.
        if type(stri) != bytes:
            btri = bytes(stri, "utf-8")
        else:
            btri = stri
        # Themis' decryption functions, consume
        # two separate information entities,
        # one supplied by the user, the other
        # generated by the encryption function:
        # 1. Context. Context is an optional value
        #    that somehow identifies and marks the
        #    encrypted entry. For example, in this
        #    case, the context used was the 'pwdid'
        #    value. Now, when decrypting, it'll
        #    that added bit of information to do the
        #    decrypting. Otherwise it produces an exception.
        # 2. Encrypted. Or any other name that you want
        #    to give to the variable that identifies Themis'
        #    encryption process.
        bval = ints.to_bytes(2, "little")
        encrypted = cell.encrypt(btri, bval)
        decrypt_info = (encrypted, bval)
        # This will be used by, 'update', 'search'...
        with open("decript_info.bin", "ab") as v:
            pickle.dump(decrypt_info, v)
        # We need to create a new list with the encrypted
        # passwords and an integer version of 'pwdid', as
        # the one in 'decrypt_info.bin' is bytes, to be
        # used in Sqlite's databaase connection.
        nrow = (encrypted, ints)
        update_info.append(nrow)
        with open("update_info.bin", "wb") as o:
            pickle.dump(update_info, o)


@db_information
@snoop
def update_pwd():
    """
    Reads the list of tuples, '(encrypted_pwd, pwdid)'
    and sends it to the datbase to update.
    """

    lst_in_lst = []
    with open("update_info.bin", "rb") as r:
        while True:
            try:
                lst_in_lst.append(pickle.load(r))
            except EOFError:
                break

    # 'update_info.bin' is a list of tuples inside another
    # list. This comprehension flattens it out.
    lst = [i for sublst in lst_in_lst for i in sublst]
    sqlite3.enable_callback_tracebacks(True)
    conn = sqlite3.connect("pwd.db")
    cur = conn.cursor()
    for tup in lst:
        query = "UPDATE pwd SET pwd = ?1 WHERE pwdid = ?2"
        cur = conn.execute(query, tup)
        conn.commit()
    conn.close()

    return query


@snoop
def call_srch():
    """
    Calls the previous functions.
    """
    encrypt()
    update_pwd()


if __name__ == "__main__":
    call_srch()
