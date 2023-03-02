"""
Module to house the search function of the app.
There are three functions in this module:
    1. Creation of the question window. Where
       we define content and look of the search
       query window. It'll return the user's
       search choice.
    2. Database call. It'll look in the db for
       the term chosen in the previous function.
    3. Creation of answer window. Generates a
       window with the results of the db query
       done in the previous function.
It's called by 'main'.
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
    with open("/home/mic/themis_key/key.bin", "rb") as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)
        with open("cell.bin", "wb") as y:
            pickle.dump(cell, y)

    update_info = []
    sqlite3.enable_callback_tracebacks(True)
    conn = sqlite3.connect("pwd.db")
    cur = conn.cursor()
    query = "SELECT pwdid, pwd FROM pwd"
    for row in cur.execute(
        query,
    ):
        if row[1] is None:
            lst = list(row)
            lst[1] = "null"
            row = tuple(lst)
            stri = row[1]
        if len(row[1]) > 1:
            stri = row[1]
        ints = row[0]
        if type(stri) != bytes:
            btri = bytes(stri, "utf-8")
        else:
            btri = stri
        bval = ints.to_bytes(2, "little")
        encrypted = cell.encrypt(btri, bval)
        decrypt_info = (encrypted, bval)
        with open("decript_info.bin", "ab") as v:
            pickle.dump(decrypt_info, v)
        nrow = (encrypted, ints)
        update_info.append(nrow)
        with open("update_info.bin", "wb") as o:
            pickle.dump(update_info, o)


@db_information
@snoop
def update_pwd():
    """"""

    lst_in_lst = []
    with open("update_info.bin", "rb") as r:
        while True:
            try:
                lst_in_lst.append(pickle.load(r))
            except EOFError:
                break

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
def db_select():
    """"""
    with open("cell.bin", "rb") as p:
        cell = pickle.load(p)

    # for  tup in lst:
    #     try:
    #         decrypted = cell.decrypt(
    #             tup[0], tup[1]
    #         )
    #         print(f"Decrypt is {decrypted.decode()}")
    #     except ThemisError:
    #         print(ThemisError)


@snoop
def srch_question():
    """
    Generates a Tput window with a question.
    """

    cnf = tput_config()

    title_width = int(
        cnf["init_width"]
        + (len(cnf["separator"]) / 2)
        - (len("WHAT ARE YOU LOOKING FOR") / 2)
    )

    title_str = "[»»] - What are you looking for? "

    with open("srch_q.bash", "w") as f:
        f.write("#!/usr/bin/env bash\n\n")
        f.write("tput clear\n\n")
        f.write(f"tput cup {cnf['init_height']} ")
        f.write(f"{title_width}\n")
        f.write(f"tput setaf {cnf['title_color']}\n")
        f.write("tput bold\n")
        f.write('echo "WHAT ARE YOU LOOKING FOR?"\n')
        f.write("tput sgr0\n\n")

        f.write(f"tput cup {cnf['separator_height']} {cnf['init_width']}\n")
        f.write(f"echo '{cnf['separator']}'\n")

        f.write(f"tput cup {cnf['separator_height'] + 3} {cnf['init_width']}\n")
        f.write('read -p "[>>»]: " choice\n')
        f.write('echo "${choice}" > srch_q_choice.txt\n')

        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x srch_q.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./srch_q.bash", cwd=os.getcwd(), shell=True)


@db_information
@snoop
def db_call():
    """
    Using the inofrmation gathered from
    'srch_q_choice.txt', it'll call the
    database and query it in fulltext.
    """

    # with open("srch_q_choice.txt", "r") as f:
    #     dirty_srch = f.read()
    #     search = dirty_srch.strip()

    # aeskey = os.environ["AES_MYSQL_KEY"]
    # answers1 = [search]
    # answers2 = [aeskey]
    # query1 = f"SELECT pwdid FROM pwd WHERE MATCH(site, username, comment) AGAINST('{search}')"
    # query2 = f"SET @key_str = SHA2('{aeskey}', 512)"
    # queries = []
    # try:
    #     conn = connect(
    #         host="localhost",
    #         user="mic",
    #         password="xxxx",
    #         database="pwd",
    #         auth_plugin="mysql_native_password",
    #     )
    #     cur = conn.cursor()
    #     cur.execute(
    #         query1,
    #     )
    #     records = cur.fetchall()
    #     idss = [i for t in records for i in t]
    #     id_str = str(idss)
    #     ids = id_str[1:-1]
    #     cur.execute(
    #         query2,
    #     )
    #     conn.commit()
    #     query3 = f"SELECT pwdid, site, username, pwd, comment, time, CAST(AES_DECRYPT(pwd, @key_str) AS CHAR(80)) FROM pwd WHERE pwdid IN ('{ids}')"
    #     cur.execute(
    #         query3,
    #     )
    #     records1 = cur.fetchall()
    #     conn.close()
    #     queries = [query1, query2, query3]
    # except Error as e:
    #     err_msg = "Error while connecting to db", e
    #     print("Error while connecting to db", e)
    #     if err_msg:
    #         return queries, err_msg

    # with open("srch_db_call.bin", "wb") as g:
    #     pickle.dump(records1, g)

    # return queries


@snoop
def call_srch():
    """
    Calls the previous functions.
    It's called by 'main'.
    """
    # srch_question()
    # db_call()


if __name__ == "__main__":
    call_srch()
