"""
Main module of the app. Where all options are available.
"""
import os
import subprocess
import sys

import snoop
from snoop import pp

from add import call_add
from clean import clean
from configs.config import tput_config
from delete import call_del
from search import srch_question
from see import call_see
from update import call_update


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


# @snoop
def main_choice():
    """
    Creates a Tupt window with the available options,
    sets the choice to a file.
    """
    cnf = tput_config()

    title_str = "WHAT TO DO; WHAT TO DO..."
    title_width = int(cnf["init_width"] + (len(cnf["separator"]) / 2) - (len(f"{title_str}") / 2))
    add_str = "[1] Add an entry."
    srch_str = "[2] Search for an entry."
    updt_str = "[3] Update an entry."
    del_str = "[4] Delete entries."
    see_str = "[5] See the db."
    cln_str = "[6] Clean transient files."
    exit_str = "[7] Exit."

    with open("main.bash", "w") as f:
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
        f.write("tput bold\n")
        f.write(f'echo "{add_str}"\n')
        f.write(f"tput cup {cnf['separator_height'] + 6} {cnf['init_width']}\n")
        f.write(f'echo "{srch_str}"\n')
        f.write(f"tput cup {cnf['separator_height'] + 8} {cnf['init_width']}\n")
        f.write(f'echo "{updt_str}"\n')
        f.write(f"tput cup {cnf['separator_height'] + 10} {cnf['init_width']}\n")
        f.write(f'echo "{del_str}"\n')
        f.write(f"tput cup {cnf['separator_height'] + 12} {cnf['init_width']}\n")
        f.write(f'echo "{see_str}"\n')
        f.write(f"tput cup {cnf['separator_height'] + 14} {cnf['init_width']}\n")
        f.write(f'echo "{cln_str}"\n')
        f.write(f"tput cup {cnf['separator_height'] + 16} {cnf['init_width']}\n")
        f.write(f'echo "{exit_str}"\n')
        f.write(f"tput cup {cnf['separator_height'] + 18} {cnf['init_width']}\n")
        f.write("read -p 'Enter your choice: ' choice\n")
        f.write('echo "${choice}" > ')
        f.write("main_choice.txt\n\n")
        f.write("tput clear\n")
        f.write("tput sgr0\n")
        f.write("tput rc")

    subprocess.run("sudo chmod +x main.bash", cwd=os.getcwd(), shell=True)
    subprocess.run("./main.bash", cwd=os.getcwd(), shell=True)


if __name__ == "__main__":
    main_choice()


def main():
    """
    Reads user's choice, runs appropriate module.
    """
    with open("main_choice.txt", "r") as f:
        dirty_main = f.read()
        main = dirty_main.strip()

    if main == "1":
        call_add()
        clean()
    if main == "2":
        srch_question()
        clean()
    if main == "3":
        call_update()
        clean()
    if main == "4":
        call_del()
        clean()
    if main == "5":
        call_see()
        clean()
    if main == "6":
        clean()
    if main == "7":
        sys.exit()


if __name__ == "__main__":
    main()
