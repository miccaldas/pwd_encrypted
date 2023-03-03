"""Module Docstring"""
import snoop
from snoop import pp
from db_decorator.db_information import db_information
from configs.config import tput_config
import os 
import subprocess
import sqlite3

def type_watch(source, value):
    return"type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


@db_information
@snoop
def update_db_call():
    """"""

    ident = input("ID to delete? ")

    # List declared here to avoid errors about being declared before assignment.
    split_lst = []
    if "," in ident:
        query = f"DELETE FROM ****PUT DATABASE NAME HERE**** WWHERE id IN ({ident})"
    if "-" in ident:
        if " - " in ident:
            answers = ident.replace(" ", "")
            split_lst = answers.split("-")
        else:
            split_lst = ident.split("-")
        query = (
            f"DELETE FROMW ****PUT DATABASE NAME HERE**** WHERE id BETWEEN {split_lst[0]} AND {split_lst[1]}"
        )
    if "," not in ident and "-" not in ident:
        query = f"DELETE FROM ****PUT DATABASE NAME HERE**** HERE id = '{ident}'"

    try:
        conn = connect(host="localhost", user="mic", password="xxxx", database="****PUT DATABASE NAME HERE****")
        cur = conn.cursor()
        query
        cur.execute(query)
        conn.commit()
        conn.close()
    except Error as e:
        err_msg = "Error while connecting to db", e
        print("Error while connecting to db", e)
        if err_msg:
            return query, err_msg

    return query




if __name__ == "__main__":
    update_db_call()

