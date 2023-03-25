"""
This module, based in 'add.py', will re-encrypt all passwords.
This is necessary because we're using Encfs that forces a different
security structure, and we need to create the 'context' values for
the passwords, that weren't used before.
"""
import os
import pickle
import sqlite3
import sys

import snoop
from Cryptodome.Random.random import randrange
from db_decorator.db_information import db_information
from dotenv import load_dotenv
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from snoop import pp

from configs.config import Efs


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()


@db_information
@snoop
def get_pwds():
    """
    Collects unencrypted passwords and ids. Stores them in a pickle file.
    """

    sqlite3.enable_callback_tracebacks(True)
    conn = sqlite3.connect("pwd.db")
    cur = conn.cursor()
    query = "SELECT pwdid, passwd FROM pwd"
    cur.execute(
        query,
    )
    results = cur.fetchall()

    with open("results.bin", "wb") as f:
        pickle.dump(results, f)

    return query


@db_information
@snoop
def encpwds():
    """
    Encrypts passwords collected in last function.
    """

    with open("results.bin", "rb") as f:
        results = []
        while True:
            try:
                results.append(pickle.load(f))
            except EOFError:
                break

    for x in range(len(results[0])):
        passwd = results[0][x][1]
        ids = results[0][x][0]
        # These are location variables, defined in '.env'.
        enc_key = os.getenv("PWD_KEY_LOC")
        res_pth = os.getenv("PWD_SEC_LOC")
        themis_key = os.getenv("PWD_KEY_LOC")
        # Declaring the class, kept in 'configs/config.py',
        # that controls the behaviour of Encfs, the
        # encrypted virtual  filesystem used to encrypt the
        # folder with the databases' more sensitive information.
        fs = Efs()
        # 'res_path' is the path to the 'pwd' folder. If it's not
        # mounted, it'll appear empty.
        pwd_lst = os.listdir(f"{res_pth}")
        if pwd_lst == []:
            # Mounts the filesystem.
            fs.mount()

        with open(f"{enc_key}", "rb") as b:
            sym_key = pickle.load(b)
        cell = SCellSeal(key=sym_key)
        # Turns string to bytes()
        bpasswd = passwd.encode("latin-1")
        # 'randrange' chooses a number between 100 and 1000.
        cont = randrange(100, 1000)
        # Convert resulting integer of last operation, to a bytes type object.
        con = cont.to_bytes(2, sys.byteorder)
        # We encrypt it with Themis.
        encrypted = cell.encrypt(bpasswd, con)

        try:
            query = "UPDATE pwd SET pwd = ?1, context = ?2 WHERE pwdid = ?3"
            answers = [encrypted, con, ids]
            sqlite3.enable_callback_tracebacks(True)
            conn = sqlite3.connect("pwd.db")
            cur = conn.cursor()
            cur.execute(query, answers)
            conn.commit()
        except sqlite3.Error as e:
            err_msg = "Error connecting to db", e
            print("Error connecting to db", e)
            if err_msg:
                return query, err_msg
        finally:
            if conn:
                conn.close()

    fs.unmount()


if __name__ == "__main__":
    encpwds()
