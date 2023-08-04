"""
Module Docstring
"""
import os
import pickle
import sqlite3

# import snoop
from dotenv import load_dotenv
from pyfzf.pyfzf import FzfPrompt
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal, SecureCellError
from rich import print

# from snoop import pp

from pwd_encrypted.configs.config import Efs, tput_config
from pwd_encrypted.db import dbdata


# def type_watch(source, value):
#     return f"type({source})", type(value)


# snoop.install(watch_extras=[type_watch])

load_dotenv()

fzf = FzfPrompt()


# @snoop
def dbnames():
    """
    Downloads all site names. Will be used to
    create a fzf powered search..
    """
    query = "SELECT site FROM pwd"
    site_lst = dbdata(query, "fetch")
    sitelist = [i[0] for i in site_lst]

    with open("sitelist.bin", "wb") as f:
        pickle.dump(sitelist, f)


# @snoop
def site_srch():
    """
    Searches for correct site in the site list.
    """
    with open("sitelist.bin", "rb") as f:
        sitelist = pickle.load(f)

    chosensite = fzf.prompt(
        sitelist,
        '--border bold --border-label="╢Choose a Site╟" --border-label-pos bottom',
    )

    with open("chosensite.bin", "wb") as f:
        pickle.dump(chosensite, f)


# @snoop
def dbpwd():
    """
    Where we'll find the password for the site
    and show it to the user.
    """
    with open("chosensite.bin", "rb") as f:
        search = pickle.load(f)

    answrs = [f"{search[0]}"]
    query = "SELECT site, username, pwd, comment, time, context FROM pwd_fts WHERE pwd_fts MATCH ?"
    print(query)
    records = dbdata(query, "fetch", answers=answrs)

    with open("records.bin", "wb") as f:
        pickle.dump(records[0], f)


# @snoop
def decrypt():
    """
    Decrypts the password.
    """
    with open("records.bin", "rb") as f:
        records = pickle.load(f)

    with open("chosensite.bin", "rb") as f:
        srch = pickle.load(f)
    search = srch[0]

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

    if records == []:
        print("There's no entry in the database with that name.")
        raise SystemExit

    pwd_bytes = []
    try:
        dec = cell.decrypt(records[2], records[5])
        # As it's not needed anymore, we don't collect the 'context' item from the list.
        pwd_bytes.append((records[0], records[1], dec, records[3], records[4]))
    except ThemisError as e:
        print(e)
    # We convert the password value from bytes to strings.
    pwd_strs = [(a, b, c.decode("latin-1"), d, e) for a, b, c, d, e in pwd_bytes]
    print(f"[bold #c2d1ad]  [+] - Your information for the site [bold #EAC696]{search}[/bold #EAC696] is:[/bold #c2d1ad]\n")
    print(f"[bold #c2d1ad]  Site: [bold #c99c28]{pwd_strs[0][0]}")
    print(f"[bold #c2d1ad]  Username: [bold #c99c28]{pwd_strs[0][1]}")
    print(f"[bold #c2d1ad]  Password: [bold #c99c28]{pwd_strs[0][2]}")
    print(f"[bold #c2d1ad]  Created On: [bold #c99c28]{pwd_strs[0][4]}")
    print(f"[bold #c2d1ad]  Comment: [bold #c99c28]{pwd_strs[0][3]}")
    # print(f"\n[bold #c2d1ad]    Username/Password for the site {search}: [/][bold #c99c28]\[ {pwd_strs[0][1]} // {pwd_strs[0][2]} ][/]\n")


# @snoop
def srchfzf():
    """
    Main function of the module.
    It calls all others.
    """
    dbnames()
    site_srch()
    dbpwd()
    decrypt()

    # cwd = "/home/mic/python/pwd_encrypted/pwd_encrypted"
    # for i in ["chosensite.bin", "records.bin", "sitelist.bin"]:
    #     os.remove(f"{cwd}/{i}")


if __name__ == "__main__":
    srchfzf()
