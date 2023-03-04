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
import sys

import snoop
from db_decorator.db_information import db_information
from dotenv import load_dotenv
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from snoop import pp

from configs.config import tput_config


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()


@snoop
def srch_question():
    """
    Generates a Tput window with a question.
    """

    cnf = tput_config()

    title_str = "WHAT ARE YOU LOOKING FOR?"
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    with open("srch_q.bash", "w") as f:
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
    database. With this data it'll encode
    the 'pwdid' value to int, so as to
    obtain the 'context' value used to
    encrypt the entry, decrypt the 'pwd'
    value, create a new list with the
    updated value and send it to a pickle
    file.
    """

    # Location of the database's encryption key.
    enc_key = os.getenv("PWD_KEY_LOC")

    with open(f"{enc_key}", "rb") as g:
        sym_key = pickle.load(g)
        cell = SCellSeal(key=sym_key)

    # File produced by the prior question function.
    with open("srch_q_choice.txt", "r") as f:
        dirty_srch = f.read()
        search = dirty_srch.strip()

    query = f"SELECT pwdid, site, username, pwd, comment, time FROM pwd WHERE site LIKE '{search}%'"
    try:
        conn = sqlite3.connect("pwd.db")
        cur = conn.cursor()
        cur.execute(
            query,
        )
        records = cur.fetchall()
        conn.close()
    except sqlite3.Error as e:
        err_msg = "Error while connecting to db", e
        print("Error while connecting to db", e)
        if err_msg:
            return query, err_msg

    # Adds, after 'pwdid', another item that is 'pwdid' turned to bytes.
    # This is the 'context' value that was used to encrypt the entry.
    context_values = [
        (z, z.to_bytes(2, sys.byteorder), x, c, b, n, m) for z, x, c, b, n, m in records
    ]

    pwd_bytes = []
    try:
        for tup in context_values:
            dec = cell.decrypt(tup[4], tup[1])
            pwd_bytes.append((tup[0], tup[2], tup[3], dec, tup[5], tup[6]))
    except ThemisError as e:
        print(e)
    pwd_dec = [(a, b, c, d.decode("latin-1"), e, f) for a, b, c, d, e, f in pwd_bytes]
    pwd_strs = [(a, b, c, d.replace('"', '\\"'), e, f) for a, b, c, d, e, f in pwd_dec]

    with open("srch_db_call.bin", "wb") as g:
        pickle.dump(pwd_strs, g)

    return query


@snoop
def srch_answer():
    """
    Generates a Tput window with the db's search results.
    """

    cnf = tput_config()

    entries = []
    with open("srch_db_call.bin", "rb") as f:
        while True:
            try:
                entries.append(pickle.load(f))
            except EOFError:
                break
    results = [i for sublst in entries for i in sublst]
    title_str = "RESULTS"
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    with open("srch_results.bash", "w") as f:
        f.write("#!/usr/bin/env bash\n\n")
        f.write("tput clear\n\n")
        f.write(f"tput cup {cnf['init_height']} {title_width}\n")
        f.write(f"tput setaf {cnf['title_color']}\n")
        f.write("tput bold\n")
        f.write(f'echo "{title_str}"\n')
        f.write("tput sgr0\n\n")
        f.write(f"tput cup {cnf['separator_height']} {cnf['init_width']}\n")
        f.write(f"echo '{cnf['separator']}'\n")

        for i in range(len(results)):
            # The way the page was consructed was that each entry set would know the
            # last height position used, so as to be able to start printing after that
            # value. The first entry has no past, so it had to be dealt separately.
            if i == 0:
                new_length = len(results[i])
                rng = range(new_length)
                # List with all the numbers of rng range.
                rng_lst = [int(r) for r in rng]
                f.write(
                    f"tput cup {cnf['separator_height'] + (rng_lst[0] + 2)} {cnf['init_width']}\n"
                )
                f.write(f"echo 'ID. {results[i][0]}'\n")
                f.write(
                    f"tput cup {cnf['separator_height'] + (rng_lst[1] + 2)} {cnf['init_width']}\n"
                )
                f.write(f'echo "Site. {results[i][1]}"\n')
                f.write(
                    f"tput cup {cnf['separator_height'] + (rng_lst[2] + 2)} {cnf['init_width']}\n"
                )
                f.write(f'echo "Username. {results[i][2]}"\n')
                f.write(
                    f"tput cup {cnf['separator_height'] + (rng_lst[3] + 2)} {cnf['init_width']}\n"
                )
                f.write(f"echo 'Password. {results[i][3]}'\n")
                f.write(
                    f"tput cup {cnf['separator_height'] + (rng_lst[4] + 2)} {cnf['init_width']}\n"
                )
                f.write(f'echo "Comment. {results[i][4]}"\n')
                f.write(
                    f"tput cup {cnf['separator_height'] + (rng_lst[5] + 2)} {cnf['init_width']}\n"
                )
                f.write(f'echo "Time. {results[i][5]}"\n')
            else:
                # 'upper' represents the last height number used. So we know that we have to
                # use heights 'higher' than that value.
                up = rng_lst[-1]
                # We are using range() and len() functions to measure the length of results.
                # The problem with this is that range() counts from 0 to a limit, meaning
                # that if we create a list from a range, up to 4 for example, it'll have 5
                # entries, the numbers from 1 to 4 and the 0. But len() starts from 1, meaning
                # these numbers will create lists of uneven number of items. As is the number
                # entries in the result list that defines the number of loops, it'll count
                # also from 0 to limit, as this is how lists are numbered. As we defined our
                # 'rng' variable from the len() of the 'results' list, it's a 1 loop shorter
                # from the number of entries in 'results'. That's why we have to add 1 to the
                # value of 'rng_lst'.
                upper = int(up + 1)
                init_rng = range(upper + 2, (upper + 2 + len(results[i])))
                rng_lst = [i for i in init_rng]
                f.write('echo " "\n')
                f.write(
                    f"tput cup {cnf['separator_height'] + rng_lst[0] + 2} {cnf['init_width']}\n"
                )
                f.write(f"echo 'ID. {results[i][0]}'\n")
                f.write(
                    f"tput cup {cnf['separator_height'] + rng_lst[1] + 2} {cnf['init_width']}\n"
                )
                f.write(f"echo 'Site. {results[i][1]}'\n")
                f.write(
                    f"tput cup {cnf['separator_height'] + rng_lst[2] + 2} {cnf['init_width']}\n"
                )
                f.write(f"echo 'Username. {results[i][2]}'\n")
                f.write(
                    f"tput cup {cnf['separator_height'] + rng_lst[3] + 2} {cnf['init_width']}\n"
                )
                f.write(f'echo "Password. {results[i][3]}"\n')
                f.write(
                    f"tput cup {cnf['separator_height'] + rng_lst[4] + 2} {cnf['init_width']}\n"
                )
                f.write(f"echo 'Comment. {results[i][4]}'\n")
                f.write(
                    f"tput cup {cnf['separator_height'] + rng_lst[5] + 2} {cnf['init_width']}\n"
                )
                f.write(f"echo 'Time. {results[i][5]}'\n")
        f.write("echo ' '\n")
        f.write(f"tput cup {int(cnf['height'] + 1)} {cnf['init_width']}\n")
        f.write("read -p 'Press any key to exit. ' choice\n")
        f.write('echo "${choice}" > /dev/null\n')

        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x srch_results.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./srch_results.bash", cwd=os.getcwd(), shell=True)


@snoop
def call_srch():
    """
    Calls the previous functions.
    It's called by 'main'.
    """
    srch_question()
    db_call()
    srch_answer()


if __name__ == "__main__":
    call_srch()
