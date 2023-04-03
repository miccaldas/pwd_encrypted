"""
This module inserts a new password in the database.
It collects user input through a cli, checks if the
site to upload is already in the database, creates
and/or encrypts a password. Uploads it to the db.
"""
import os
import pickle
import random
import sqlite3
from string import punctuation

import click
import snoop
from Cryptodome.Random.random import randrange
from dotenv import load_dotenv
from english_words import get_english_words_set
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from snoop import pp

from pwd_encrypted.configs.config import Efs


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()
pwdfldr = os.getenv("PWD_LOC")


# @snoop
def check_repeats(site):
    """
    We check with the database to see if there's already an entry with
    the same site's name. If there are, we present the information to
    the user and ask him if he wants to continue inputing the entry or
    if he wants to abort. In the first case we do nothing and the
    program continues, in the other, we exit the program.
    """
    query = f"SELECT * FROM pwd_fts WHERE pwd_fts MATCH '{site}'"

    sqlite3.enable_callback_tracebacks(True)
    conn = sqlite3.connect("pwd.db")
    cur = conn.cursor()
    cur.execute(query)
    records = cur.fetchall()
    if records:
        vals = [(str(a), b, c, e, f) for a, b, c, d, e, f, g in records]
        columns = ["ID", "SITE", "USERNAME", "COMMENT", "TIME"]
        table = Table(highlight=True, border_style="#898121")
        rows = []
        for v in vals:
            rows.append([v[0], v[1], v[2], v[3], v[4]])
        for column in columns:
            table.add_column(column, justify="center")
        for row in rows:
            table.add_row(*row)
        console = Console()
        console.print("\n")
        console.print(
            f"[bold]The site '{site}' that you requested is similar to this entry:\n",
            justify="center",
        )
        console.print(table, justify="center")
        gonogo = Confirm.ask("                                                      [bold]Do you want to upload it anyway?")
        if gonogo:
            pass
        else:
            raise SystemExit


@snoop
def create_encrypt_pwd(pwdinput):
    """
    Collects all information from 'answr.bin'.
    Generates password and context value.
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

    # 'passwd' is the variable name that later on will be used to encrypt a new password.
    # So as to use the same password generating code, regardless if I chose my own pwd or
    # not, we'll arbitrarily decide that 'pwdinput' is a password, and the code we'll run
    # based on this assumption. This never becomes a problem because we immediately check
    # if 'pwdinput' is indeed a password or not, by checking if it is an integer. If false,
    # nothing changes and we go to the encryption portion of code. If true, we'll create it
    # now. This default choice saves us from two if statements almost alike.
    passwd = pwdinput
    if type(passwd) == int:
        length = passwd
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
        words = random.choices(wordlst, k=length)
        punct = random.choices(pun, k=int(length - 1))
        sam = words + punct
        # In 'sam' the words and punctuation are in order.
        # We want it mixed together.
        samp = random.sample(sam, int(length + (length - 1)))
        # Turns it from a list to a string.
        samp_str = " ".join(samp)
        # We get rid of the spaces, because a lot of sites
        # don't accept passwords with spaces.
        passwd = samp_str.replace(" ", "")

    with open(f"{enc_key}", "rb") as b:
        sym_key = pickle.load(b)
    cell = SCellSeal(key=sym_key)
    # Turns string to bytes()
    bpasswd = passwd.encode("latin-1")
    # 'randrange' chooses a number between 100 and 1000.
    cont = randrange(100, 1000)
    # Convert resulting integer of last operation, to a bytes type object.
    con = cont.to_bytes(2, "little")
    # We encrypt it with Themis.
    encrypted = cell.encrypt(bpasswd, con)
    pwcon = [encrypted, con]

    with open(f"{pwdfldr}/pwd_con.bin", "wb") as f:
        pickle.dump(pwcon, f)


@snoop
def db_call(answers):
    """
    inserts the new entry in the database.
    """

    try:
        query = "INSERT INTO pwd (site, username, pwd, comment, context) VALUES (?1, ?2, ?3, ?4, ?5)"
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


@click.command()
@click.option("-s", "--site")
@click.option("-u", "--user")
@click.option("-p", "--password")
@click.option("-l", "--length", type=int)
@click.option("-c", "--commentary", prompt=True)
# @snoop
def call_add(site, user, password, length, commentary):
    """
    Gathers all information through command line.
    Calls all other functions.
    Cli functionality can be accessed by calling **pwdadd**.\n
    Options:\n
    -s   Site name.\n
    -u   Username.\n
    -p   Password, if you don't want it to create one fror you.\n
    -l   Length, number of words used to create your password. Keep it low or the encrypted values will be ridiculously long.\n
    -c   Commentary. What is the site about, and shit like that.
    """
    check_repeats(site)
    if password:
        create_encrypt_pwd(password)
    else:
        create_encrypt_pwd(length)

    with open(f"{pwdfldr}/pwd_con.bin", "rb") as f:
        enc_values = pickle.load(f)

    answers = [site, user, commentary]
    answers.insert(2, enc_values[0])
    answers.insert(-1, enc_values[1])
    db_call(answers)

    fs = Efs()
    fs.unmount()

    os.remove(f"{pwdfldr}/pwd_con.bin")
    os.remove(f"{pwdfldr}/answr.bin")


if __name__ == "__main__":
    call_add()
