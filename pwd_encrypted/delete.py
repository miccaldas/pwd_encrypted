"""
Cli accessed delete methods for pwd.
"""
import sqlite3

import click
import snoop
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


# @snoop
def db_call(dlt):
    """
    Makes the db call to delete one or more entries.
    """
    split_lst = []
    if "," in dlt:
        lst = dlt.split(",")
        # Splitting creates spaces. Delete them.
        nlst = [i.strip() for i in lst]
        # Present tuple.
        nt = tuple(nlst)
        query = f"DELETE FROM pwd WWHERE pwdid IN ({nt})"
    if "-" in dlt:
        if " - " in dlt:
            answers = dlt.replace(" ", "")
            split_lst = answers.split("-")
        else:
            split_lst = dlt.split("-")
        query = f"DELETE FROM pwd WHERE pwdid BETWEEN {split_lst[0]} AND {split_lst[1]}"
    if "," not in dlt and "-" not in dlt:
        query = f"DELETE FROM pwd WHERE pwdid = '{dlt}'"

    try:
        sqlite3.enable_callback_tracebacks(True)
        conn = sqlite3.connect("/home/mic/python/pwd_encrypted/pwd_encrypted/pwd.db")
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        # It's here because it was creating 'unboundlocalerror' in the 'finally' clause.
        conn.close()
    except sqlite3.Error as e:
        print("Error connecting to the db", e)


@click.command()
@click.argument("dlt")
# @snoop
def call_del(dlt):
    """
    Collects search query, calls the previous functions.
    Function that deletes one, several or
    range of entries in the 'pwd' database.\n
    You can call it with 'pwddlt', and use it in the following form:\n
    1. Delete non sequential entries. Surround the ids with quotation
       marks and separate them with a comma:\n
       pwddlt '435,436', for example.\n
    2. Delete sequential entries. Envelop first and last ids with quotation
       marks and separate them with a dash:\n
       pwddlt '437-439'.\n
       You may include spaces, but they'll be deleted by the application.\n
    3. Delete single entry. Write the id:\n
       pwddlt 66
    """
    db_call(dlt)


if __name__ == "__main__":
    call_del()
