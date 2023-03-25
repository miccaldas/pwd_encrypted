"""
Module to house the delete function of the app.
There are three functions in this module:
    1. Creation of the question window. Where
       we ask for the pwdid's values to delete.
    2. Database call. It'll delete entries.
    3. Creation of confirmation window. Assserts
       that the entry was deleted.
It's called by 'main'.
"""

import os
import sqlite3
import subprocess

import snoop
from db_decorator.db_information import db_information
from snoop import pp

from configs.config import tput_config


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


def del_question():
    """
    Generates a Tput window with a prompt to insert the id to delete.
    """

    cnf = tput_config()

    title_str = "WHO WILL WE OBLITERATE TODAY?"
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    with open("delete.bash", "w") as f:
        f.write("#!/usr/bin/env bash\n\n")
        f.write("tput clear\n\n")
        f.write(f"tput cup {cnf['init_height']} ")
        f.write(f"{title_width}\n")
        f.write(f"tput setaf {cnf['title_color']}\n")
        f.write("tput bold\n")
        f.write(f'echo "{title_str}"\n')
        f.write("tput sgr0\n\n")

        f.write(f"tput cup {cnf['separator_height']} {cnf['init_width']}\n")
        f.write(f"echo '{cnf['separator']}'\n")

        f.write(f"tput cup {cnf['separator_height'] + 3} {cnf['init_width']}\n")
        f.write('read -p "[>>»]: " choice\n')
        f.write('echo "${choice}" > delete.txt\n')

        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x delete.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./delete.bash", cwd=os.getcwd(), shell=True)


def db_call():
    """
    Makes the db call to delete an entry.
    """
    with open("delete.txt", "r") as f:
        dirty_srch = f.read()
        ident = dirty_srch.strip()

    split_lst = []
    if "," in ident:
        query = f"DELETE FROM pwd WWHERE pwdid IN ({ident})"
    if "-" in ident:
        if " - " in ident:
            answers = ident.replace(" ", "")
            split_lst = answers.split("-")
        else:
            split_lst = ident.split("-")
        query = (
            f"DELETE FROMW pwd WHERE pwdid BETWEEN {split_lst[0]} AND {split_lst[1]}"
        )
    if "," not in ident and "-" not in ident:
        query = f"DELETE FROM pwd WHERE pwdid = '{ident}'"

    try:
        sqlite3.enable_callback_tracebacks(True)
        conn = sqlite3.connect("pwd.db")
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        err_msg = "Error connecting to the db", e
        print("Error connecting to the db", e)
        if err_msg:
            return query, err_msg
    finally:
        if conn:
            conn.close()


def feedback_page():
    """
    Shows Tput page with a confirmation message.
    """
    with open("delete.txt", "r") as f:
        dirty_srch = f.read()
        ident = dirty_srch.strip()

    cnf = tput_config()

    title_str = "WHAT HAVE YOU DONE!!"
    conf_str = f"The database entry with the {ident} id was deleted."
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    with open("del_confirmation.bash", "w") as f:
        f.write("#!/usr/bin/env bash\n\n")
        f.write("tput clear\n\n")
        f.write(f"tput cup {cnf['init_height']} ")
        f.write(f"{title_width}\n")
        f.write(f"tput setaf {cnf['title_color']}\n")
        f.write("tput bold\n")
        f.write(f'echo "{title_str}"\n')
        f.write("tput sgr0\n\n")

        f.write(f"tput cup {cnf['separator_height']} {cnf['init_width']}\n")
        f.write(f"echo '{cnf['separator']}'\n")

        f.write(f"tput cup {cnf['separator_height'] + 3} {cnf['init_width']}\n")
        f.write(f'echo "{conf_str}"\n')
        f.write(f"tput cup {cnf['space_under_separator']} {cnf['init_width']}\n")
        f.write("read -p 'Press any key to exit. ' choice\n")
        f.write('echo "${choice}" > /dev/null\n')

        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x del_confirmation.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./del_confirmation.bash", cwd=os.getcwd(), shell=True)


def call_del():
    """
    Calls the previous functions.
    It's called by 'main'.
    """
    del_question()
    db_call()
    feedback_page()


if __name__ == "__main__":
    call_del()
