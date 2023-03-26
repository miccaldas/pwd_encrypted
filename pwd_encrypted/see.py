"""
Shows all entries in the database.
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

from configs.config import Efs, tput_config


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()


@db_information
# @snoop
def db_call():
    """
    Collects all entries in db, decrypts the passwords,
    cleans the data and stores the result in a pickle file.
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

    query = "SELECT * FROM pwd"
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
    pwd_dec = [
        (a, b, c, d.decode("latin-1"), e.replace("'", ""), f)
        for a, b, c, d, e, f in pwd_bytes
    ]
    # As some passwords have double quotation marks that confuse bash, we escape them.
    # And, as before, we delete double quotation marks in the commments.
    pwd_strs = [
        (a, b, c, d.replace('"', '\\"'), e.replace('"', ""), f)
        for a, b, c, d, e, f in pwd_dec
    ]

    with open("see_db_call.bin", "wb") as g:
        pickle.dump(pwd_strs, g)

    return query


# @snoop
def see_answer():
    """
    Generates a Tput window with the db's search results.
    """

    cnf = tput_config()

    entries = []
    with open("see_db_call.bin", "rb") as f:
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
    vals = [(str(a), b, c, d, e, f) for a, b, c, d, e, f in results]
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
    # List with the length of the names.
    lens_nms = [len(nm) for nm in names]
    # # We create a list of lists of tuples, with variable name and value.
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
    # The next loop will ascertain from each of the last two lists, which element has the
    # bigger length. That way we know that the table cell of the respective line, will
    # have to have at, least, the width of its longer element.
    hi_ln_val = max(lens_val)
    hi_ln_nms = max(lens_nms)
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

    with open("see_results.bash", "w") as f:
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
        # This centers the table below the separator. All table elements will have this width.
        table_width = int(
            cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{ntraces}") / 2)
        )
        first_item_height = int(cnf["separator_height"] + 4)
        rng_values_lst = range(len(values))
        rng_lst = [int(r) for r in rng_values_lst]

        # As we have to account for width and height for each entry column, we'll iterate through
        # the results...
        for r in rng_lst:
            # We find the length the name string by subtracting its length from the length of the
            # longest variable name. This will help us calculate the space needed for its celll in
            # the table. This is for the 'id' variable.
            n_id_len0 = int(hi_ln_nms - len(values[r][0][0]))
            # The same, only for the values.
            v_id_len0 = int(hi_ln_val - len(values[r][0][1]))
            # We calculate the remaining empty space needed in the cell, so as they'll always be as
            # big as their longest member.
            space_id_n0 = "".join(" " * n_id_len0)
            space_id_v0 = "".join(" " * v_id_len0)
            # The 'site' column.
            n_site_len0 = int(hi_ln_nms - len(values[r][1][0]))
            v_site_len0 = int(hi_ln_val - len(values[r][1][1]))
            space_site_n0 = "".join(" " * n_site_len0)
            space_site_v0 = "".join(" " * v_site_len0)
            # The 'username' column.
            n_user_len0 = int(hi_ln_nms - len(values[r][2][0]))
            v_user_len0 = int(hi_ln_val - len(values[r][2][1]))
            space_user_n0 = "".join(" " * n_user_len0)
            space_user_v0 = "".join(" " * v_user_len0)
            # The 'pwd' column.
            n_pwd_len0 = int(hi_ln_nms - len(values[r][3][0]))
            v_pwd_len0 = int(hi_ln_val - len(values[r][3][1]))
            space_pwd_n0 = "".join(" " * n_pwd_len0)
            space_pwd_v0 = "".join(" " * v_pwd_len0)
            # The 'comment' column.
            n_com_len0 = int(hi_ln_nms - len(values[r][4][0]))
            v_com_len0 = int(hi_ln_val - len(values[r][4][1]))
            space_com_n0 = "".join(" " * n_com_len0)
            space_com_v0 = "".join(" " * v_com_len0)
            # The 'time' column.
            n_tmp_len0 = int(hi_ln_nms - len(values[r][5][0]))
            v_tmp_len0 = int(hi_ln_val - len(values[r][5][1]))
            space_tmp_n0 = "".join(" " * n_tmp_len0)
            space_tmp_v0 = "".join(" " * v_tmp_len0)

            # As always it's needed to separate the first entry from the rest. The remaining entries
            # will be counted from the initial entry values onward.
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
                    f"echo '| {values[r][2][0]}{space_user_n0} | {values[r][2][1]}{space_user_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 3} {table_width}\n")
                f.write(
                    f"echo '| {values[r][3][0]}{space_pwd_n0} | {values[r][3][1]}{space_pwd_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 4} {table_width}\n")
                f.write(
                    f"echo '| {values[r][4][0]}{space_com_n0} | {values[r][4][1]}{space_com_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 5} {table_width}\n")
                f.write(
                    f"echo '| {values[r][5][0]}{space_tmp_n0} | {values[r][5][1]}{space_tmp_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 6} {table_width}\n")
                f.write(f"echo '{ntraces}'\n")
                f.write("echo ' '\n")
            else:
                # Here are all entries after the first one. We have 6 columns plus an empty line that were used after
                # the 'first_item_height', that corresponds to line 15. We add these values and multiply it by the
                # current loop value. This way the second entry will be printed at line (15 + 7) * 1. For each column
                # we add 1, so as to keep them under each other. The third entry will be place at (15 + 7) * 2, and so
                # on and so forth.
                f.write(pp(f"tput cup {first_item_height + 7 * r + 1} {table_width}\n"))
                f.write(f"echo '{ntraces}'\n")
                f.write(f"tput cup {first_item_height + 7 * r + 2} {table_width}\n")
                f.write(
                    f"echo '| {values[r][0][0]}{space_id_n0} | {values[r][0][1]}{space_id_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 7 * r + 3} {table_width}\n")
                f.write(
                    f"echo '| {values[r][1][0]}{space_site_n0} | {values[r][1][1]}{space_site_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 7 * r + 4} {table_width}\n")
                f.write(
                    f"echo '| {values[r][2][0]}{space_user_n0} | {values[r][2][1]}{space_user_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 7 * r + 5} {table_width}\n")
                f.write(
                    f"echo '| {values[r][3][0]}{space_pwd_n0} | {values[r][3][1]}{space_pwd_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 7 * r + 6} {table_width}\n")
                f.write(
                    f"echo '| {values[r][4][0]}{space_com_n0} | {values[r][4][1]}{space_com_v0} |'\n"
                )
                f.write(f"tput cup {first_item_height + 7 * r + 7} {table_width}\n")
                f.write(
                    f"echo '| {values[r][5][0]}{space_tmp_n0} | {values[r][5][1]}{space_tmp_v0} |'\n"
                )
                f.write(pp(f"tput cup {first_item_height + 7 * r + 8} {table_width}\n"))
                f.write(f"echo '{ntraces}'\n")
                f.write("echo ' '\n")

        f.write(f"tput cup {cnf['space_under_separator']} {table_width}\n")
        f.write("read -p 'Press any key to exit. ' choice\n")
        f.write('echo "${choice}" > /dev/null\n')
        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x see_results.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./see_results.bash", cwd=os.getcwd(), shell=True)


# @snoop
def call_see():
    """
    Calls the previous functions.
    It's called by 'main'.
    """
    db_call()
    see_answer()
    fs = Efs()
    fs.unmount()


if __name__ == "__main__":
    call_see()
