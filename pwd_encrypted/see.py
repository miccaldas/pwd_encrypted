"""
Shows all entries in the database.
"""
import os
import pickle
import sqlite3

import click
import snoop
from dotenv import load_dotenv
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from rich.console import Console
from rich.table import Table
from snoop import pp

from pwd_encrypted.configs.config import Efs


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()
pwdfldr = os.getenv("PWD_LOC")


# @snoop
def db_call():
    """
    Collects all entries in db, decrypts the passwords,
    cleans the data and stores the result in a pickle file.
    """
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
    # Location of the database's encryption key.
    enc_key = os.getenv("PWD_KEY_LOC")

    with open(f"{enc_key}", "rb") as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)

    query = "SELECT * FROM pwd"
    try:
        conn = sqlite3.connect("pwd.db")
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

    pwd_bytes = []
    try:
        for tup in records:
            dec = cell.decrypt(tup[3], tup[6])
            # As it's not needed anymore, we don't collect the 'context' item from the list.
            pwd_bytes.append((tup[0], tup[1], tup[2], dec, tup[4], tup[5]))
    except ThemisError as e:
        print(e)
    # We convert the password value from bytes to strings. We delete the quotation marks in
    # the comments, as it'll create problems when serving it has a bash file.
    pwd_strs = [(a, b, c, d.decode("latin-1"), e, f) for a, b, c, d, e, f in pwd_bytes]
    pp(pwd_strs)
    with open(f"{pwdfldr}/see_db_call.bin", "wb") as g:
        pickle.dump(pwd_strs, g)


# @snoop
def see_answer():
    """
    Generates a Rich table with the db's search results.
    """

    entries = []
    with open(f"{pwdfldr}/see_db_call.bin", "rb") as f:
        while True:
            try:
                entries.append(pickle.load(f))
            except EOFError:
                break
    results = [i for sublst in entries for i in sublst]

    vals = [(str(a), b, c, d, e, f) for a, b, c, d, e, f in results]
    columns = ["ID", "SITE", "USERNAME", "PASSWORD", "COMMENT", "TIME"]

    table = Table(highlight=True, border_style="#898121")
    rows = []
    for v in vals:
        rows.append([v[0], v[1], v[2], v[3], v[4], v[5]])

    for column in columns:
        table.add_column(column, justify="center")
    for row in rows:
        table.add_row(*row)

    console = Console()
    console.print("\n")
    console.print(table, justify="center")
    console.print("\n")


# @snoop
def call_see():
    """
    Invoked as 'pwdall', calls the previous functions to show the whole of the db.
    """
    db_call()
    see_answer()
    fs = Efs()
    fs.unmount()
    os.remove(f"{pwdfldr}/see_db_call.bin")


if __name__ == "__main__":
    call_see()
