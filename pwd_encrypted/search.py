"""
Module to house the search function of the app.
"""
import os
import pickle
import sqlite3

import click

# import snoop
from dotenv import load_dotenv
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from rich.console import Console
from rich.table import Table

# from snoop import pp

from pwd_encrypted.configs.config import Efs


# def type_watch(source, value):
#     return "type({})".format(source), type(value)


# snoop.install(watch_extras=[type_watch])

load_dotenv()


# @snoop
def db_call(search):
    """
    Using the inofrmation sent from 'srch_question' function,
    it'll call the database and, with this data, it'll encode
    the 'pwdid' value to int, so as to obtain the 'context'
    value used to encrypt the entry, decrypt the 'pwd' value,
    create a new list with the updated values and send it to
    a pickle file.
    """
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
    # Location of the database's encryption key.
    enc_key = os.getenv("PWD_KEY_LOC")

    with open(f"{enc_key}", "rb") as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)

    query = f"SELECT * FROM pwd_fts WHERE pwd_fts MATCH '{search}'"
    try:
        conn = sqlite3.connect("/home/mic/python/pwd_encrypted/pwd_encrypted/pwd.db")
        cur = conn.cursor()
        cur.execute(
            query,
        )
        records = cur.fetchall()
    except sqlite3.Error as e:
        print("Error while connecting to db", e)
    finally:
        if conn:
            conn.close()

    if records == []:
        print("There's no entry in the database with that name.")
        raise SystemExit

    pwd_bytes = []
    try:
        for tup in records:
            dec = cell.decrypt(tup[3], tup[6])
            # As it's not needed anymore, we don't collect the 'context' item from the list.
            pwd_bytes.append((tup[0], tup[1], tup[2], dec, tup[4], tup[5]))
    except ThemisError as e:
        print(e)
    # We convert the password value from bytes to strings.
    pwd_strs = [(a, b, c, d.decode("latin-1"), e, f) for a, b, c, d, e, f in pwd_bytes]

    with open("srch_db_call.bin", "wb") as g:
        pickle.dump(pwd_strs, g)

    return query


# @snoop
def srch_answer(query):
    """
    Generates a Rich table with the db's search results.
    """

    entries = []
    with open("srch_db_call.bin", "rb") as f:
        while True:
            try:
                entries.append(pickle.load(f))
            except EOFError:
                break
    results = [i for sublst in entries for i in sublst]

    vals = [(str(a), b, c, d, e, f) for a, b, c, d, e, f in results]
    columns = ["ID", "SITE", "USERNAME", "PASSWORD", "COMMENT", "TIME"]

    table = Table(title=f"{query}", highlight=True, border_style="#898121")
    rows = [[v[0], v[1], v[2], v[3], v[4], v[5]] for v in vals]
    for column in columns:
        table.add_column(column, justify="center")
    for row in rows:
        table.add_row(*row)

    console = Console()
    console.print("\n")
    console.print(table, justify="center")
    console.print("\n")


@click.command()
@click.argument("qry")
# @snoop
def srch_question(qry):
    """
    Gets search query through command line and calls the other functions.\n
    Accepts one string argument, the query, and its called with **pwdsrch**.
    """
    db_call(qry)
    srch_answer(qry)

    os.remove("srch_db_call.bin")


if __name__ == "__main__":
    srch_question()
