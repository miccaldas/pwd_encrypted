"""
Update functionality of the 'pwd' database.
"""
import os
import pickle
import sqlite3

import click

# import snoop
from dotenv import load_dotenv
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError

# from snoop import pp

from pwd_encrypted.configs.config import Efs


# def type_watch(source, value):
#     return f"type({source})", type(value)


# snoop.install(watch_extras=[type_watch])

load_dotenv()


# @snoop
def query_definition(answers):
    """
    Using the inofrmation gathered from
    'call_updt', it'll call the database
    and make the update.
    """

    # These are location variables, defined in '.env'.
    enc_key = os.getenv("PWD_KEY_LOC")
    res_pth = os.getenv("PWD_SEC_LOC")
    themis_key = os.getenv("PWD_KEY_LOC")
    fs = Efs()
    # 'res_path' is the path to the 'pwd' folder. If it's not
    # mounted, it'll appear empty.
    pwd_lst = os.listdir(f"{res_pth}")
    if pwd_lst == []:
        # Mounts the filesystem.
        fs.mount()
    with open(f"{enc_key}", "rb") as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)

    conn = sqlite3.connect("/home/mic/python/pwd_encrypted/pwd_encrypted/pwd.db")
    cur = conn.cursor()
    if answers[0] == "pwd":
        try:
            bval = int(answers[2]).to_bytes(2, "little")
            btri = bytes(answers[1], "latin-1")
            encrypted = cell.encrypt(btri, bval)
            answers.insert(4, encrypted)
            answers.insert(5, bval)
            query = "UPDATE pwd SET pwd = ?4, context = ?5 WHERE pwdid = ?3"
            query_execution(cur, query, answers, conn)
        except sqlite3.Error as e:
            print("Error while connecting to db", e)
    else:
        try:
            query = "UPDATE pwd SET ?1 = ?2 WHERE pwdid = ?3"
            query_execution(cur, query, answers, conn)
        except sqlite3.Error as e:
            print("Error while connecting to db ", e)


# Suggested by Sourcery
# @snoop
def query_execution(cur, query, answers, conn):
    """
    Centralizes the execution of the db call.
    """
    cur.execute(query, answers)
    conn.commit()
    conn.close()


@click.command()
@click.option("-i", "--pwdid", type=int)
@click.option("-c", "--column")
@click.option("-u", "--update")
# @snoop
def call_update(pwdid, column, update):
    """
    Invoked as 'pwdupdt', calls the previous functions.\n
    **Options:**\n
    -i   Id integer of the line to update.\n
    -c   Name of column to update.\n
    -u   Update text.
    """
    answers = [column, update, pwdid]
    query_definition(answers)

    fs = Efs()
    fs.unmount()


if __name__ == "__main__":
    call_update()
