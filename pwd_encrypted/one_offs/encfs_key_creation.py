"""
Module that created the key that encrypts the 'pwd' folder.
Not to be confused with the key in PWD_KEY_LOC, that is to
used for encrypting password data. This is to encrypt the
folder where PWD_KEY_LOC exists.
This module already ran and the key is kept in PWD_FLD_KEY.
"""
import os
import pickle
import sqlite3
import subprocess
import sys

import snoop
from db_decorator.db_information import db_information
from dotenv import load_dotenv
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()

enc_key = os.getenv("PWD_KEY_LOC")
# This variable no longer exists. It was needed just to create the key.
pwd_id = os.getenv("PWD_DB_ID")


@db_information
@snoop
def encrypt():
    """
    Most of this module code doesn't work afer the
    creation of PWD_FLD_KEY. The very same key that
    was created by this function. 'enc_key' now is
    encrypted and a new workflow is in place. We
    leave it here for documentation purposes.
    """

    # Location of the Themis key.
    with open(
        f"{enc_key}",
        "rb",
    ) as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)

    # Value to encrypt. Usually a string.
    try:
        conn = sqlite3.connect("pwd.db")
        cur = conn.cursor()
        query = "SELECT passwd from pwd WHERE pwdid = ?"
        answers = [pwd_id]
        cur.execute(query, answers)
        record = cur.fetchone()
        conn.close()
    except sqlite3.Error as e:
        err_msg = "Error while connecting to db ", e
        print("Error while connecting to db ", e)
        if err_msg:
            return query, err_msg

    tup0 = record[0]
    val = tup0.encode("latin-1")
    cont = int(pwd_id)
    # # Context value. Adds another layer of security.
    context = cont.to_bytes(2, sys.byteorder)
    # # Encryption command.
    try:
        encrypted = cell.encrypt(val, context)
    except ThemisError as e:
        print(e)

    values = [encrypted, context]
    with open("test.bin", "wb") as f:
        pickle.dump(values, f)

    try:
        conn = sqlite3.connect("pwd.db")
        cur = conn.cursor()
        query = "UPDATE pwd SET pwd = ?1 WHERE pwdid = ?2"
        answers = [encrypted, cont]
        cur.execute(query, answers)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        err_msg = "Error while connecting to db ", e
        print("Error while connecting to db ", e)
        if err_msg:
            return query, err_msg


@snoop
def decrypt():
    """
    This function was cerated just o test if 'encrypt()' did
    its job correctly. It's code, as per the reasons given in
    'encrypt()', doesn't work anymore.
    Here for documentation purposes.
    """

    with open(
        f"{enc_key}",
        "rb",
    ) as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)

    try:
        conn = sqlite3.connect("pwd.db")
        cur = conn.cursor()
        query = "SELECT pwdid, pwd FROM pwd WHERE pwdid = ?"
        answers = [pwd_id]
        cur.execute(query, answers)
        records = cur.fetchall()
    except sqlite3.Error as e:
        err_msg = "Error while connecting to db ", e
        print("Error while connecting to db ", e)
        if err_msg:
            return query, err_msg
    finally:
        if conn:
            conn.close()

    # Decryption command.
    cont = records[0][0].to_bytes(2, sys.byteorder)
    try:
        dec = cell.decrypt(records[0][1], cont)
    except ThemisError as e:
        print(e)

    nstr = dec.decode("latin-1")
    print(nstr)
