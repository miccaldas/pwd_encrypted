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


# @snoop
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

        query = f"SELECT pwdid, site, username, pwd, comment, time, context FROM pwd WHERE site LIKE '{search}%'"
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


# @snoop
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
    # We do the same that we did to the lengths list, to 'vals'.
    values = [item for t in vals for item in t]
    # The next loop will ascertain from each of the last two lists, which element has the
    # bigger length. That way we know that the table cell of the respective line, will
    # have to have at, least, the width of its longer element. The loop compares each
    # result to a 'standard', which, by convention, is the first element of each list.
    # The next two variables initiate those values.
    val_vals = lens_val[0]
    val_nms = lens_nms[0]
    # Initiating lists needed for the loop. They'll collect the
    # the highest length value of each list.
    hi_ln_val = []
    hi_ln_nms = []
    # This two are here because I was getting an annoying 'unbound local error' error.
    # This was the simplest way of dealing with it.
    hi_len_val = ""
    hi_len_nms = ""

    # The loop to calculate the bigger element of each list.
    # This one is specific to values lengths.
    for lt in lens_val:
        if lt > val_vals:
            val_vals = lt
            hi_ln_val.append(val_vals)
    # The loop should, but doesn't, return just one value, it returns all values higher
    # than the 'standard' value. It returns str(), if it found just one value, and
    # returns list, if finds several values. If its the latter, we run the 'max' function.
    if len(hi_ln_val) == 1:
        hi_len_val = hi_ln_val[0]
    if len(hi_ln_val) > 1:
        hi_len_val = max(hi_ln_val)
    # This loop is the same as the last one, but now for 'names'.
    for ln in lens_nms:
        if ln > val_nms:
            val_nms = ln
            hi_ln_nms.append(val_nms)
    if len(hi_ln_nms) == 1:
        hi_len_nms = hi_ln_nms[0]
    if len(hi_ln_nms) > 1:
        hi_len_nms = max(hi_ln_nms)

    # This variable measures how big a line would be, if it was composed by the lengthiest
    # elements of each list, plus 3. To account for the spaces and separator between name and value.
    vh = int(hi_len_val + hi_len_nms + 3)
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

        # This centers the table below the separator. All table elements will have this width.
        table_width = int(
            cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{ntraces}") / 2)
        )
        # The top separator line isn't part of the ('name', 'value') list that'll be used to fill
        # the table, so we print it before the start of the loop.
        f.write(f"tput cup {cnf['separator_height'] + 3} {table_width}\n")
        f.write(f"echo '{ntraces}'\n")
        # We're using a range() value that starts at 1, so the loop count starts at the same value as
        # the length of the list we'll create inside the loop. As the list will start at 1, we print
        # what would've been its index[0] element, before the loop.
        first_item_height = int(cnf["separator_height"] + 4)
        lst_zip = list(zip(names, values))
        rng_lst_zip = range(1, len(lst_zip))
        # Creates a list where its elements are the integers inside the range of lst_zip. Necessary
        # for subsequent list iterations.
        rng_lst = [int(r) for r in rng_lst_zip]
        # These are, specifically, dimensions for index[0] line.
        # The other dimensions are defined inside the loop.
        n_len0 = int(hi_len_nms - len(lst_zip[0][0]))
        v_len0 = int(hi_len_val - len(lst_zip[0][1]))
        space_n0 = "".join(" " * n_len0)
        space_v0 = "".join(" " * v_len0)
        # Printing index[0]
        f.write(f"tput cup {first_item_height} {table_width}\n")
        f.write(f"echo '| {lst_zip[0][0]}{space_n0} | {lst_zip[0][1]}{space_v0} |'\n")
        # The loop, counting from lst_zip[1], starts here.
        for v in rng_lst:
            n_len = int(hi_len_nms - len(lst_zip[v][0]))
            v_len = int(hi_len_val - len(lst_zip[v][1]))
            space_n = "".join(" " * n_len)
            space_v = "".join(" " * v_len)
            # We add to the height of last printed element, 'first_item_height', the value of 'v'.
            # Since the range is starting at 1, it puts the string one line below the other.
            f.write(f"tput cup {cnf['separator_height'] + v + 4} {table_width}\n")
            f.write(f"echo '| {lst_zip[v][0]}{space_n} | {lst_zip[v][1]}{space_v} |'\n")
        # As we want this element to be under the iterated list, we add 1 to its length, because len()
        # starts at 0, to that we add 1 again so it's one line under the end of loop lines. To this we
        # add another 2 lines, one for each element that is part of the table but outside the loop.
        # That is, the top seprator, and index[0].
        f.write(
            f"tput cup {cnf['separator_height'] + len(lst_zip) + 4} {table_width}\n"
        )
        f.write(f"echo '{ntraces}'\n")
        f.write(f"tput cup {cnf['space_under_separator']} {table_width}\n")
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
