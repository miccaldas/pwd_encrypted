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


@snoop
def update_question():
    """
    Generates a Tput window with a question.
    """

    cnf = tput_config()

    title_str = "UPDATE"
    id_str = "[»»] - What is the id of the line you want to update?"
    col_str = "[»»] - What is the column you want to update?"
    updt_str = "[»»] - What is your update?"
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    with open("update_q.bash", "w") as f:
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
        f.write(f'read -p "{id_str}  " choice\n')
        f.write('echo "${choice}" > update_id_choice.txt\n')
        f.write(f"tput cup {cnf['separator_height'] + 5} {cnf['init_width']}\n")
        f.write(f'read -p "{col_str}  " choice\n')
        f.write('echo "${choice}" > update_col_choice.txt\n')
        f.write(f"tput cup {cnf['separator_height'] + 7} {cnf['init_width']}\n")
        f.write(f'read -p "{updt_str}  " choice\n')
        f.write('echo "${choice}" > update_updt_choice.txt\n')

        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x update_q.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./update_q.bash", cwd=os.getcwd(), shell=True)


@db_information
@snoop
def db_call():
    """
    Using the inofrmation gathered from
    'update_q_choice.txt', it'll call the
    database. With this data it'll encode
    the 'pwdid' value to int, so as to
    obtain the 'context' value used to
    encrypt the entry, decrypt the encrypted
    value, create a new list with the
    updated values and send it to a pickle
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
    if pwd_lst != []:
        with open(f"{enc_key}", "rb") as g:
            sym_key = pickle.load(g)
            cell = SCellSeal(key=sym_key)

        with open("update_id_choice.txt", "r") as f:
            dirty_id = f.read()
            pwdid = dirty_id.strip()
        with open("update_col_choice.txt", "r") as f:
            dirty_col = f.read()
            col = dirty_col.strip()
        with open("update_updt_choice.txt", "r") as f:
            dirty_updt = f.read()
            updt = dirty_updt.strip()

        conn = sqlite3.connect("pwd.db")
        cur = conn.cursor()
        if col == "pwd":
            try:
                bval = int(pwdid).to_bytes(2, sys.byteorder)
                btri = bytes(updt, "latin-1")
                encrypted = cell.encrypt(btri, bval)
                query = f"UPDATE pwd SET {col} = '{encrypted}' WHERE pwdid = {pwdid}"
                cur.execute(
                    query,
                )
                conn.commit()
                conn.close()
            except sqlite3.Error as e:
                err_msg = "Error while connecting to db", e
                print("Error while connecting to db", e)
                if err_msg:
                    return query, err_msg
        else:
            try:
                query = f"UPDATE pwd SET {col} = '{updt}' WHERE pwdid = {pwdid}"
                cur.execute(
                    query,
                )
                conn.commit()
                conn.close()
            except sqlite3.Error as e:
                err_msg = "Error while connecting to db ", e
                print("Error while connecting to db ", e)
                if err_msg:
                    return query, err_msg

        return query


@db_information
@snoop
def update_answer():
    """
    Gets the newly created line from the database, builds a
    window wuth the updated values. We present them in a
    simple ascii table.
    """
    with open("update_id_choice.txt", "r") as u:
        dirty_id = u.read()
        pwdid = dirty_id.strip()

    conn = sqlite3.connect("pwd.db")
    cur = conn.cursor()
    query = (
        f"SELECT pwdid, site, username, comment, time FROM pwd WHERE pwdid = {pwdid}"
    )
    try:
        cur.execute(query)
        records = cur.fetchall()
        conn.close()
    except sqlite3.Error as e:
        err_msg = "Error while connecting to the db ", e
        print("Error while connecting to the db ", e)
        if err_msg:
            return query, err_msg

    # As at this moment we're not very concerned in showing the entirety of the
    # encrypted password, it's very long and doesn't bring any added information,
    # we'll replace by the '<ENCRYPTED>' string. The id value has to be converted
    # to string because, in the next step we'll look for the length of every 'test'
    # element, and int() has no len() property.
    test = [(str(a), b, c, "<ENCRYPTED>", d, e) for a, b, c, d, e in records]
    # The titles of the variables that will be in the table.
    names = ["id", "site", "user", "pwd", "comment", "time"]
    # List with the length of the name strings.
    lns_tst = [
        (len(a), len(b), len(c), len(d), len(e), len(f)) for a, b, c, d, e, f in test
    ]
    # Turns a list of tuples to a list. Most of the following code was written on the
    # basis that 'test' and 'names' were pure lists. To conform to that expectation, we
    # change it from a list of tuples to list.
    lens_tst = [item for t in lns_tst for item in t]
    # List with the length of the variables.
    lens_nms = [len(nm) for nm in names]
    # We do the same that we did to the list of tuples with length values, to 'tst',
    # that is, also, a list of tuples.
    teste = [item for t in test for item in t]
    # The next loop will ascertain from each of the last two lists, which element has the
    # bigger length. That way we know that the table cell of the respective line, will
    # have to have at, least, the width of its lengthier value. The loop compares each
    # result to a 'standard' one which, by convention, is the first one of each list.
    # The next two variables initiate those values.
    val_tst = lens_tst[0]
    val_nms = lens_nms[0]
    # Initiating lists needed for the loop. They'll collect the
    # the highest length value of each list.
    hi_ln_tst = []
    hi_ln_nms = []
    # This two are here because I was having an annoying 'unbound local error' error.
    # This was the simplest way of dealing with it.
    hi_len_tst = ""
    hi_len_nms = ""

    # The loop I talked about earlier. This one is specific to the collected variables lengths.
    for lt in lens_tst:
        if lt > val_tst:
            val_tst = lt
            hi_ln_tst.append(val_tst)
    # The loop should, but it doesn't, return just one value, it returns all values higher
    # than the first variable length. It returns str(), if it found just one value and return
    # list, if finds several values. If it's a list, we run the 'max' function.
    if len(hi_ln_tst) == 1:
        hi_len_tst = hi_ln_tst[0]
    if len(hi_ln_tst) > 1:
        hi_len_tst = max(hi_ln_tst)
    # This loop is the same as the last one, but now just for 'names'.
    for ln in lens_nms:
        if ln > val_nms:
            val_nms = ln
            hi_ln_nms.append(val_nms)
    if len(hi_ln_nms) == 1:
        hi_len_nms = hi_ln_nms[0]
    if len(hi_ln_nms) > 1:
        hi_len_nms = max(hi_ln_nms)

    # This variable measures the highest length of a line, by adding the highest leng() values
    # in both lists plus 3, to account for the spaces + separator between name and value.
    vh = int(hi_len_tst + hi_len_nms + 3)
    # Variable of the character that'll be used to build the top and bottom table separators.
    sep = "-"
    # Creates a string, made of consecutive number of '-' characters, calculated by multiplying
    # by the 'vh' value.
    traces = "".join(sep * vh)
    # The border in ascii squares have '+' signs on their vertices and starts two pixels before
    # the cell content, and ends two pixels after their end. This variable adds to the start
    # and end of the separators, these characters:
    ntraces = f"+-{traces}-+"
    # The len() of ntraces'. It'll be needed further along.
    ud_len = len(ntraces)

    # Calls the user-generated default values for 'Tput'. These variables are brought from
    # 'configs/config.py'
    cnf = tput_config()

    title_str = "UPDATE RESULTS"
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    with open("res_update.bash", "w") as f:
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
        # The top seprator line isn't part of the ('name', 'value') list that'll be used to fill
        # the table, so we print it before the start of the loop.
        f.write(f"tput cup {cnf['separator_height'] + 3} {table_width}\n")
        f.write(f"echo '{ntraces}'\n")
        # We're using a range() value that starts at 1, so the loop count starts at the same value as
        # the length of the list we'll create inside the loop. As the list will start at 1, we print
        # what would've been its index[0] element, before the loop.
        first_item_height = int(cnf["separator_height"] + 4)
        lst_zip = list(zip(names, teste))
        rng_lst_zip = range(1, len(lst_zip))
        # Creates a list where its elements are the integers inside the range of lst_zip. Necessary
        # for subsequent list iterations.
        rng_lst = [int(r) for r in rng_lst_zip]
        # These are, specifically, dimensions for index[0] line.
        # The other dimensions are defined inside the loop.
        n_len0 = int(hi_len_nms - len(lst_zip[0][0]))
        t_len0 = int(hi_len_tst - len(lst_zip[0][1]))
        space_n0 = "".join(" " * n_len0)
        space_t0 = "".join(" " * t_len0)
        # Printing index[0]
        f.write(f"tput cup {first_item_height} {table_width}\n")
        f.write(f"echo '| {lst_zip[0][0]}{space_n0} | {lst_zip[0][1]}{space_t0} |'\n")
        # The loop, counting from lst_zip[1], starts here.
        for v in rng_lst:
            n_len = int(hi_len_nms - len(lst_zip[v][0]))
            t_len = int(hi_len_tst - len(lst_zip[v][1]))
            space_n = "".join(" " * n_len)
            space_t = "".join(" " * t_len)
            # We add to the height of last printed element, 'first_item_height', the value of 'v'.
            # Since the range is starting at 1, it puts the string one line below the other.
            f.write(f"tput cup {cnf['separator_height'] + v + 4} {table_width}\n")
            f.write(f"echo '| {lst_zip[v][0]}{space_n} | {lst_zip[v][1]}{space_t} |'\n")
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
    subprocess.run("sudo chmod +x res_update.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./res_update.bash", cwd=os.getcwd(), shell=True)


@snoop
def call_update():
    """
    Calls the previous functions.
    It's called by 'main'.
    """
    update_question()
    db_call()
    update_answer()

    fs = Efs()
    fs.unmount()


if __name__ == "__main__":
    call_update()
