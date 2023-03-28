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
from time import sleep

import snoop
from dotenv import load_dotenv
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from snoop import pp

from configs.config import Efs, tput_config


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

    title_str = "WHAT KNOWLEDGE WILL WE RIP OUT OF THE HANDS OF THE GODS, TODAY?"
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
    # In principle we already opened the filesystem in the
    # beginning of the module, but you never know.
    sleep(1)
    if len(pwd_lst) > 0:
        # Location of the database's encryption key.
        enc_key = os.getenv("PWD_KEY_LOC")

        with open(f"{enc_key}", "rb") as g:
            sym_key = pickle.load(g)
            cell = SCellSeal(key=sym_key)

        # File produced by the prior function.
        with open("srch_q_choice.txt", "r") as f:
            dirty_srch = f.read()
            search = dirty_srch.strip()

        query = f"SELECT * FROM pwd_fts WHERE pwd_fts MATCH '{search}'"
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

        if records == []:
            print("There's no entry in the database with that name.")
            sys.exit()

        pwd_bytes = []
        try:
            for tup in records:
                dec = cell.decrypt(tup[3], tup[6])
                # As it's not needed anymore, we don't collect the 'context' item from the list.
                pwd_bytes.append((tup[0], tup[1], tup[2], dec, tup[4], tup[5]))
        except ThemisError as e:
            print(e)
        # We convert the password value from bytes to strings.
        pwd_dec = [
            (a, b, c, d.decode("latin-1"), e, f) for a, b, c, d, e, f in pwd_bytes
        ]
        # As some passwords have double quotation marks that confuse bash, we escape them.
        pwd_strs = [
            (a, b, c, d.replace('"', '\\"'), e, f) for a, b, c, d, e, f in pwd_dec
        ]

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
    title_str = "THIS IS WHAT YOUR INSATIABLE CURIOSITY GETS YOU!"
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    # The id value has to be converted to string because, in the next step we'll look for
    # the length of every 'vals' element, and int() has no len() property.
    vls = [(str(a), b, c, d.replace(")", "\)"), e, f) for a, b, c, d, e, f in results]
    vas = [(str(a), b, c, d.replace("(", "\("), e, f) for a, b, c, d, e, f in vls]
    vals = [(str(a), b, c, f"'{d}'", e, f) for a, b, c, d, e, f in vas]
    # The line title names.
    names = ["id", "site", "user", "pwd", "comment", "time"]
    # List with the length of the values strings.
    lns_val = [
        (len(a), len(b), len(c), len(d), len(e), len(f)) for a, b, c, d, e, f in vals
    ]
    # Turns a list of tuples to a list. Most of the following code was written on the
    # basis that 'vals' and 'names' were pure lists. To conform to that expectation, we
    # change it from a list of tuples to list.
    lens_val = [item for t in lns_val for item in t]
    hi_ln_val = max(lens_val)
    # List with the length of the names.
    lens_nms = [len(nm) for nm in names]
    hi_ln_nms = max(lens_nms)
    # We do the same that we did to the lengths list, to 'vals'.
    valus = [item for t in vals for item in t]
    values = []
    for v in vals:
        values.append(
            [
                ("id", v[0]),
                ("site", v[1]),
                ("user", v[2]),
                ("pwd", v[3]),
                ("comment", v[4]),
                ("time", v[5]),
            ]
        )

    # This variable measures how big a line would be, if it was composed by the lengthiest
    # elements of each list, plus 3. To account for the spaces and separator between name and value.
    vh = int(hi_ln_val + hi_ln_nms + 3)
    # Variable of the character that'll be used to build the top and bottom table separators.
    sep = "-"
    # Creates a string, made of consecutive '-' characters. It'll repeat until reaching the 'vh' value.
    traces = "".join(sep * vh)
    # The border in ascii squares have '+' signs on their vertices and start two pixels before
    # the cell content, ending two pixels after its end. These characters are added to the start and end
    # of the separators:
    ntraces = f"+-{traces}-+"
    # The len() of ntraces'.
    ud_len = len(ntraces)

    with open("srch_results.bash", "w") as f:
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
        table_width = int(
            cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{ntraces}") / 2)
        )
        first_item_height = int(cnf["separator_height"] + 4)
        rng_values_lst = range(len(values))
        rng_lst = [int(r) for r in rng_values_lst]
        for r in rng_lst:
            n_id_len0 = int(hi_ln_nms - len(values[r][0][0]))
            v_id_len0 = int(hi_ln_val - len(values[r][0][1]))
            space_id_n0 = "".join(" " * n_id_len0)
            space_id_v0 = "".join(" " * v_id_len0)
            n_site_len0 = int(hi_ln_nms - len(values[r][1][0]))
            v_site_len0 = int(hi_ln_val - len(values[r][1][1]))
            space_site_n0 = "".join(" " * n_site_len0)
            space_site_v0 = "".join(" " * v_site_len0)
            n_username_len0 = int(hi_ln_nms - len(values[r][2][0]))
            v_username_len0 = int(hi_ln_val - len(values[r][2][1]))
            space_username_n0 = "".join(" " * n_username_len0)
            space_username_v0 = "".join(" " * v_username_len0)
            n_pwd_len0 = int(hi_ln_nms - len(values[r][3][0]))
            v_pwd_len0 = int(hi_ln_val - len(values[r][3][1]))
            space_pwd_n0 = "".join(" " * n_pwd_len0)
            space_pwd_v0 = "".join(" " * v_pwd_len0)
            n_comment_len0 = int(hi_ln_nms - len(values[r][4][0]))
            v_comment_len0 = int(hi_ln_val - len(values[r][4][1]))
            space_comment_n0 = "".join(" " * n_comment_len0)
            space_comment_v0 = "".join(" " * v_comment_len0)
            n_time_len0 = int(hi_ln_nms - len(values[r][5][0]))
            v_time_len0 = int(hi_ln_val - len(values[r][5][1]))
            space_time_n0 = "".join(" " * n_time_len0)
            space_time_v0 = "".join(" " * v_time_len0)

            if r == 0:
                f.write(f"tput cup {cnf['separator_height'] + 3} {table_width}\n")
                f.write(f"echo '{ntraces}'\n")
                f.write(f"tput cup {first_item_height} {table_width}\n")
                f.write(
                    f"echo '| {values[r][0][0]}{space_id_n0} | {values[r][0][1]}{space_id_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 1} {table_width}\n")
                f.write(
                    f"echo '| {values[r][1][0]}{space_site_n0} | {values[r][1][1]}{space_site_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 2} {table_width}\n")
                f.write(
                    f"echo '| {values[r][2][0]}{space_username_n0} | {values[r][2][1]}{space_username_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 3} {table_width}\n")
                f.write(
                    f"echo '| {values[r][3][0]}{space_pwd_n0} | {values[r][3][1]}{space_pwd_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 4} {table_width}\n")
                f.write(
                    f"echo '| {values[r][4][0]}{space_comment_n0} | {values[r][4][1]}{space_comment_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 5} {table_width}\n")
                f.write(
                    f"echo '| {values[r][5][0]}{space_time_n0} | {values[r][5][1]}{space_time_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 6} {table_width}\n")
                f.write(f"echo '{ntraces}'\n")
                f.write(f"tput cup {first_item_height + 7} {table_width}\n")
                f.write("echo ' '\n")
            else:
                f.write(pp(f"tput cup {first_item_height + 9 * r + 1} {table_width}\n"))
                f.write(f"echo '{ntraces}'\n")
                f.write(f"tput cup {first_item_height + 9 * r + 2} {table_width}\n")
                f.write(
                    f"echo '| {values[r][0][0]}{space_id_n0} | {values[r][0][1]}{space_id_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 9 * r + 3} {table_width}\n")
                f.write(
                    f"echo '| {values[r][1][0]}{space_site_n0} | {values[r][1][1]}{space_site_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 9 * r + 4} {table_width}\n")
                f.write(
                    f"echo '| {values[r][2][0]}{space_username_n0} | {values[r][2][1]}{space_username_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 9 * r + 5} {table_width}\n")
                f.write(
                    f"echo '| {values[r][3][0]}{space_pwd_n0} | {values[r][3][1]}{space_pwd_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 9 * r + 6} {table_width}\n")
                f.write(
                    f"echo '| {values[r][4][0]}{space_comment_n0} | {values[r][4][1]}{space_comment_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 9 * r + 7} {table_width}\n")
                f.write(
                    f"echo '| {values[r][5][0]}{space_time_n0} | {values[r][5][1]}{space_time_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 9 * r + 8} {table_width}\n")
                f.write(f"echo '{ntraces}'\n")
                f.write(f"tput cup {first_item_height + 9 * r + 9} {table_width}\n")
                f.write("echo ' '\n")

        f.write(f"tput cup {9 * len(rng_lst) + 12} {table_width}\n")
        f.write("read -p 'Press any key to exit. ' choice\n")
        f.write('echo "${choice}" > /dev/null\n')
        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x srch_results.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./srch_results.bash", cwd=os.getcwd(), shell=True)


# @snoop
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
