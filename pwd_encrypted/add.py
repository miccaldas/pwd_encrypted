"""
This module inserts a new password in the database.
To do that, asks if user wants to author its password
or if he preffers us to do it for him, creates
passwords of length based on the user input, checks if
the site the user inputed is already on the database,
warns if it is and asks him if he wants to continue
adding it to the db, and encrypts the password before
uploading it to the database.
"""
import os
import pickle
import random
import sqlite3
import subprocess
import sys
from string import punctuation

import snoop
from Cryptodome.Random.random import randrange
from db_decorator.db_information import db_information
from dotenv import load_dotenv
from english_words import get_english_words_set
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from snoop import pp

from configs.config import Efs, tput_config


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()


# @snoop
def first_input_window():
    """
    Agreggates the site, username and password authorship
    questions. We break the questions loop, so we can run
    the function that checks for repeats and asks the user
    if he wants to author the password or let us do it.
    """

    cnf = tput_config()

    title_str = "FIRST, SOME QUESTIONS..."
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    sitio_str = "[»»] What is the name of the site? "
    username_str = "[»»] What is the username? "
    author_str = "[»»] Do you want to name the password yourself? [y/n] "

    with open("add.bash", "w") as f:
        f.write("#!/usr/bin/env bash\n\n")
        f.write("tput clear\n\n")
        f.write(f"tput cup {cnf['init_height']} {title_width}\n")
        f.write(f"tput setaf {cnf['title_color']}\n")
        f.write("tput bold\n")
        f.write(f'echo "{title_str}"\n')
        f.write("tput sgr0\n\n")
        f.write("")

        f.write(f"tput cup {cnf['separator_height']} {cnf['init_width']}\n")
        f.write(f"echo '{cnf['separator']}'\n")

        f.write(f"tput cup {cnf['separator_height'] + 4} {cnf['init_width']}\n")
        f.write(f"read -p '{sitio_str}: ' choice\n")
        f.write('echo "${choice}" > sitio_choice.txt\n')

        f.write(f"tput cup {cnf['separator_height'] + 6} {cnf['init_width']}\n")
        f.write(f'read -p "{username_str}: " choice\n')
        f.write('echo "${choice}" > username_choice.txt\n')

        f.write(f"tput cup {cnf['separator_height'] + 8} {cnf['init_width']}\n")
        f.write(f'read -p "{author_str}: " choice\n')
        f.write('echo "${choice}" > author_choice.txt\n')

        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x add.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./add.bash", cwd=os.getcwd(), shell=True)


@db_information
# @snoop
def check_repeats():
    """
    We check with the database to see if there's already an entry with
    the same site's name. If there are, we present the information to
    the user and ask him if he wants to continue inputing the entry or
    if he wants to abort. In the first case we do nothing and the
    program continues, in the other, we exit the program.
    """

    cnf = tput_config()

    warning_str = "For the site name that you gave us, we already have this record:"
    warning_question_str = "Do you still want to add the record?[y/n] "

    query = "SELECT * FROM pwd WHERE site LIKE ?"

    lst_files = os.listdir(os.getcwd())

    title_str = "YOU MAY BE REPEATING YOURSELF..."
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    if "sitio_choice.txt" in lst_files:
        with open("sitio_choice.txt", "r") as f:
            dirty_site = f.read()
            sitio = dirty_site.strip()

            sqlite3.enable_callback_tracebacks(True)
            conn = sqlite3.connect("pwd.db")
            cur = conn.cursor()
            cur.execute(query, (sitio,))
            records = cur.fetchone()
            if records:
                with open("site_repeat.bash", "w") as f:
                    f.write("#!/usr/bin/env bash\n\n")
                    f.write("tput clear\n\n")
                    f.write(f"tput cup {cnf['init_height']} {title_width}\n")
                    f.write(f"tput setaf {cnf['title_color']}\n")
                    f.write("tput bold\n")
                    f.write(f'echo "{title_str}"\n')
                    f.write("tput sgr0\n\n")
                    f.write("")

                    f.write(f"tput cup {cnf['separator_height']} {cnf['init_width']}\n")
                    f.write(f"echo '{cnf['separator']}'\n")

                    f.write(
                        f"tput cup {cnf['separator_height'] + 2} {cnf['init_width']}\n"
                    )
                    f.write(f'echo "{warning_str}"\n')

                    f.write(
                        f"tput cup {cnf['separator_height'] + 4 + 1} {cnf['init_width']}\n"
                    )
                    f.write(f"tput setaf {cnf['title_color']}\n")
                    f.write("tput bold\n")
                    f.write(f'echo ID. "{records[0]}"\n')
                    f.write("tput sgr0\n\n")

                    f.write(
                        f"tput cup {cnf['separator_height'] + 4 + 2} {cnf['init_width']}\n"
                    )
                    f.write(f'echo Site. "{records[1]}"\n')

                    f.write(
                        f"tput cup {cnf['separator_height'] + 4 + 3} {cnf['init_width']}\n"
                    )
                    f.write(f'echo Username. "{records[2]}"\n')

                    f.write(
                        f"tput cup {cnf['separator_height'] + 4 + 4} {cnf['init_width']}\n"
                    )
                    f.write(f'echo Password. "{records[4]}"\n')

                    f.write(
                        f"tput cup {cnf['separator_height'] + 4 + 5} {cnf['init_width']}\n"
                    )
                    f.write(f'echo Comment. "{records[5]}"\n')

                    f.write(
                        f"tput cup {cnf['separator_height'] + 4 + 6} {cnf['init_width']}\n"
                    )
                    f.write(f'echo Time. "{records[6]}"\n')

                    f.write(
                        f"tput cup {cnf['separator_height'] + 4 + 8} {cnf['init_width']}\n"
                    )
                    f.write(f'read -p "{warning_question_str} " choice\n')
                    f.write('echo "${choice}" > warning_choice.txt\n')

                    f.write("tput clear\n")
                    f.write("tput sgr0\n")
                    f.write("tput rc")

                    subprocess.run(
                        "sudo chmod +x site_repeat.bash",
                        cwd=os.getcwd(),
                        shell=True,
                    )
                    subprocess.run("./site_repeat.bash", cwd=os.getcwd(), shell=True)
    else:
        print("Couldn't find 'sitio_choice.txt' file")


# @snoop
def pwd_authorship():
    """
    Checks if the user wants to author the password or not,
    if yes, collects his choice in a file, if no, exits the app.
    """
    cnf = tput_config()

    author_y_str = "Add your password: "

    lst_files = os.listdir(os.getcwd())

    title_str = "BUT, WHO WRITES THE PASSWORD?"
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    if "author_choice.txt" in lst_files:
        with open("author_choice.txt", "r") as f:
            dirty_author = f.read()
            author = dirty_author.strip()

        if author == "y":
            with open("author_y.bash", "w") as f:
                f.write("#!/usr/bin/env bash\n\n")
                f.write("tput clear\n\n")
                f.write(f"tput cup {cnf['init_height']} {title_width}\n")
                f.write(f"tput setaf {cnf['title_color']}\n")
                f.write("tput bold\n")
                f.write(f'echo "{title_str}"\n')
                f.write("tput sgr0\n\n")
                f.write("")

                f.write(f"tput cup {cnf['separator_height']} {cnf['init_width']}\n")
                f.write(f"echo '{cnf['separator']}'\n")

                f.write(f"tput cup {cnf['separator_height'] + 2} {cnf['init_width']}\n")
                f.write(f'read -p "{author_y_str} " choice\n')
                f.write('echo "${choice}" > author_y.txt\n')

                f.write("tput clear\n")
                f.write("tput sgr0\n")
                f.write("tput rc")
                f.close()

                subprocess.run(
                    "sudo chmod +x author_y.bash", cwd=os.getcwd(), shell=True
                )
                subprocess.run("./author_y.bash", cwd=os.getcwd(), shell=True)
    else:
        print("Couldn't find 'author_choice.txt'.")


# @snoop
def second_input_window():
    """
    This method ends the questionnary. We'll create
    two different pipelines, one for those who made
    their own password, and for those who didn't.
    We'll create a window with the questions still
    not made: length of password and comment.
    """
    cnf = tput_config()

    lgth_str = "How long do you want your password to be? "
    comment_str = "Any comments that you would like to add? "
    title_str = "MORE QUESTIONS..."
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    lst_files = os.listdir(os.getcwd())

    if "author_choice.txt" in lst_files:
        with open("author_choice.txt", "r") as f:
            dirty_author = f.read()
            author = dirty_author.strip()

        with open("second_input.bash", "w") as f:
            f.write("#!/usr/bin/env bash\n\n")
            f.write("tput clear\n\n")
            f.write(f"tput cup {cnf['init_height']} {title_width}\n")
            f.write(f"tput setaf {cnf['title_color']}\n")
            f.write("tput bold\n")
            f.write(f'echo "{title_str}"\n')
            f.write("tput sgr0\n\n")
            f.write("")

            f.write(f"tput cup {cnf['separator_height']} {cnf['init_width']}\n")
            f.write(f"echo '{cnf['separator']}'\n")

            if author == "n":
                f.write(f"tput cup {cnf['separator_height'] + 2} {cnf['init_width']}\n")
                f.write(f'read -p "{lgth_str} " choice\n')
                f.write('echo "${choice}" > lgth_choice.txt\n')
                f.write(f"tput cup {cnf['separator_height'] + 4} {cnf['init_width']}\n")
                f.write(f'read -p "{comment_str} " choice\n')
                f.write('echo "${choice}" > comment_choice.txt\n')

            if author == "y":
                f.write(f"tput cup {cnf['separator_height'] + 4} {cnf['init_width']}\n")
                f.write(f'read -p "{comment_str} " choice\n')
                f.write('echo "${choice}" > comment_choice.txt\n')

            f.write("tput clear\n")
            f.write("tput sgr0\n")
            f.write("tput rc")
            f.close()

            subprocess.run(
                "sudo chmod +x second_input.bash", cwd=os.getcwd(), shell=True
            )
            subprocess.run("./second_input.bash", cwd=os.getcwd(), shell=True)


@db_information
# @snoop
def add_upld_db_call():
    """
    Collects all information gathered by the questions of
    the previous functions. Generates passwords andd sends
    the treated information into the database.
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

    lst_files = os.listdir(os.getcwd())

    with open("sitio_choice.txt", "r") as d:
        dirty_site = d.read()
        sitio = dirty_site.strip()
    with open("username_choice.txt", "r") as g:
        use_dirty = g.read()
        username = use_dirty.strip()
    with open("comment_choice.txt", "r") as e:
        com_dirty = e.read()
        comment = com_dirty.strip()

    if "author_y.txt" in lst_files:
        with open("author_y.txt", "r") as p:
            pwd_dirty = p.read()
            passwd = pwd_dirty.strip()

    if "author_choice.txt" in lst_files:
        with open("author_choice.txt", "r") as h:
            autopwd_dirty = h.read()
            pwd_request = autopwd_dirty.strip()
        if pwd_request == "n":
            if "lgth_choice.txt" in lst_files:
                with open("lgth_choice.txt", "r") as r:
                    lgth_dirty = r.read()
                    lgt = lgth_dirty.strip()
                    lgth = int(lgt)
                    # This moment starts the building of the password.
                    # Gets the word list.
                    word_lst = get_english_words_set(["gcide"])
                    wordlst = list(word_lst)
                    # Gets the punctuation list.
                    punt = punctuation
                    # Bash has a really bad time with quotation marks. Python don't
                    # love them neither. To make our life easier, we just exclude
                    # them from the passwords.
                    pun = [i for i in punt if i != "'" and i != '"']
                    # 'k' is the password length chosen by the user.
                    words = random.choices(wordlst, k=lgth)
                    punct = random.choices(pun, k=int(lgth - 1))
                    sam = words + punct
                    # In 'sam' the words and punctuation are in order.
                    # We want it mixed together.
                    samp = random.sample(sam, int(lgth + (lgth - 1)))
                    # Turns it from a list to a string.
                    samp_str = " ".join(samp)
                    # We get rid of the spaces, because a lot of sites
                    # don't accept passwords with spaces.
                    passwd = samp_str.replace(" ", "")
        if pwd_request == "y":
            pass
        # In principle we already opened the filesystem in the
        # beginning of the module, but you never know.
        if pwd_lst != []:
            with open(f"{enc_key}", "rb") as b:
                sym_key = pickle.load(b)
            cell = SCellSeal(key=sym_key)
            # Turns string to bytes()
            bpasswd = passwd.encode("latin-1")
            # 'randrange' chooses a number between 100 and 1000.
            cont = randrange(100, 1000)
            # Convert resulting integer of last operation, to a bytes type object.
            con = cont.to_bytes(2, sys.byteorder)
            # We encrypt it with Themis.
            encrypted = cell.encrypt(bpasswd, con)

            try:
                # Here we begin the info insertion to the db. We added a column, 'context', that'll be filled
                # with the value of 'con'. In other modules we were always encrypting values that were already
                # in the db; so we used the id number of the lines as the context value. But now we're creating
                # a new line, there's no id value to guide us. Adding 1 to the highest current id value, doesn't
                # work, because if a line was erased and it was above the current max() result, that number won't
                # be used again. It'll skip it and start counting from then on. This makes trying to predict the
                # next id value a dangerous proposition. Instead we'll use Cryptodome's 'Random' module to choose
                # a number, trn it to bytes() and shove it to its own column in the db.
                query = "INSERT INTO pwd (site, username, pwd, comment, context) VALUES (?1, ?2, ?3, ?4, ?5)"
                answers = [sitio, username, encrypted, comment, con]
                sqlite3.enable_callback_tracebacks(True)
                conn = sqlite3.connect("pwd.db")
                cur = conn.cursor()
                cur.execute(query, answers)
                conn.commit()
            except sqlite3.Error as e:
                err_msg = "Error connecting to db", e
                print("Error connecting to db", e)
                if err_msg:
                    return query, err_msg
            finally:
                if conn:
                    conn.close()

            truncated = [sitio, username, "<ENCRYPTED>", comment]
            with open("answers.bin", "wb") as y:
                pickle.dump(truncated, y)

                return query


# @snoop
def add_feedback_window():
    """
    Builds a window wuth the values supplied by the user. So he
    can verify if everything is correct. Presented as a ascii table.
    """
    with open("answers.bin", "rb") as u:
        values = pickle.load(u)

    # The names of the variables that'll go in the table.
    names = ["site", "user", "pwd", "comment"]
    # Lists with the length of the variables and values strings.
    lens_val = [len(ts) for ts in values]
    lens_nms = [len(nm) for nm in names]
    # The next loop will ascertain from each of the last two
    # lists, which element has the bigger length. That way we
    # know that the table cell of the respective line, will have
    # to have at least this width. The loop compares each result
    # to a 'standard' one which, by convention, is the first one
    # of each list. The next two variables initiate those values.
    val_val = lens_val[0]
    val_nms = lens_nms[0]
    # Initiating lists needed for the loop. They'll collect the
    # the highest length value of each list.
    hi_ln_val = []
    hi_ln_nms = []
    # These two are here because I was gettinf an annoying
    # 'unbound local error' error, and this was a simple
    # way of dealing with it.
    hi_len_val = ""
    hi_len_nms = ""

    # The loop I talked about earlier. This one is specific
    # to the collected values lengths.
    for lt in lens_val:
        if lt > val_val:
            val_val = lt
            hi_ln_val.append(val_val)
    # The loop should, but doesn't, return just one value, it returns
    # all values higher than the first variable length. Because of
    # this, we have to expect that the result might be a string or a
    # list. If it's a list, we run the 'max' function.
    if len(hi_ln_val) == 1:
        hi_len_val = hi_ln_val[0]
    if len(hi_ln_val) > 1:
        hi_len_val = max(hi_ln_val)

    # Same loop as the last one, but now for the 'names' list.
    for ln in lens_nms:
        if ln > val_nms:
            val_nms = ln
            hi_ln_nms.append(val_nms)
    if len(hi_ln_nms) == 1:
        hi_len_nms = hi_ln_nms[0]
    if len(hi_ln_nms) > 1:
        hi_len_nms = max(hi_ln_nms)

    # This variable measures the highest possible width of a line,
    # in the presentation table, by adding the highest lengths in
    # both lists, plus 3, to account for the spaces and seprator
    # between the strings.
    vh = int(hi_len_val + hi_len_nms + 3)
    # Variable of the character that'll be used to build the upper and
    # lower separators on each line.
    sep = "-"
    # Creates a string, made of '-' characters, with a length calculated
    # by multiplying 'sep' by 'vh'. This assures that the table won't be
    # smaller than the sum of its longest merbers.
    traces = "".join(sep * vh)
    # The borders in ascii boxes have '+' signs on their vertices, start two
    # pixels before the cell content, and end two pixels after their end.
    # This variable adds to the start and finish of the 'traces' string these
    # characters.
    ntraces = f"+-{traces}-+"
    # The length value of the ascii table.
    ud_len = len(ntraces)

    # Calls the user-generated default values for 'Tput'. These variables are brought from
    # 'configs/config.py'
    cnf = tput_config()

    title_str = "GAZE IN AWE AT YOUR ACOMPLISHMENTS!"
    title_width = int(
        cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2)
    )

    with open("res_add.bash", "w") as f:
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
        # We're using a range() value that starts at 1, so the loop count starts on the same value as
        # the len() of the list we'll create to count loop rounds. Because it starts at 1, we print
        # what would've been its index[0], before the loop.
        first_item_height = int(cnf["separator_height"] + 4)
        lst_zip = list(zip(names, values))
        rng_lst_zip = range(1, len(lst_zip))
        # Creates a list where its elements are the integers inside the range of lst_zip. Necessary
        # for subsequent list iterations.
        rng_lst = [int(r) for r in rng_lst_zip]
        # These are, specifically, dimensions for index[0] line.
        # The other dimensions are defined inside the loop.
        n_len0 = int(hi_len_nms - len(lst_zip[0][0]))
        t_len0 = int(hi_len_val - len(lst_zip[0][1]))
        space_n0 = "".join(" " * n_len0)
        space_t0 = "".join(" " * t_len0)
        # Printing index[0]
        f.write(f"tput cup {first_item_height} {table_width}\n")
        f.write(f"echo '| {lst_zip[0][0]}{space_n0} | {lst_zip[0][1]}{space_t0} |'\n")
        # The loop, counting from lst_zip[1], starts here.
        for v in rng_lst:
            n_len = int(hi_len_nms - len(lst_zip[v][0]))
            t_len = int(hi_len_val - len(lst_zip[v][1]))
            space_n = "".join(" " * n_len)
            space_t = "".join(" " * t_len)
            # We add to the height of last printed element, 'first_item_height', the value of 'v'.
            # Since the range is starting at 1, it puts the string one line below the other.
            f.write(f"tput cup {cnf['separator_height'] + v + 4} {table_width}\n")
            f.write(f"echo '| {lst_zip[v][0]}{space_n} | {lst_zip[v][1]}{space_t} |'\n")
        # As we want this element to be under the iterated list, we add 1 to its length, because len()
        # starts at 0, to that we add 1 again so it's one line under the end of loop lines. To this we
        # add another 2 lines, one for each element that is part of the table but outside the loop.
        # That is, the top separator, and index[0].
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
    subprocess.run("sudo chmod +x res_add.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./res_add.bash", cwd=os.getcwd(), shell=True)


# @snoop
def call_add():
    """
    Calls the functions in the module
    and closes pwd's mount point.
    """
    first_input_window()
    check_repeats()
    pwd_authorship()
    second_input_window()
    add_upld_db_call()
    add_feedback_window()

    fs = Efs()
    fs.unmount()
