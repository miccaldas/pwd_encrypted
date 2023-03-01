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
import subprocess

import snoop
from db_decorator.db_information import db_information
from snoop import pp

from configs.config import tput_config


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


# @db_information
@snoop
def srch_question():
    """
    Generates a Tput window with a question.
    """

    cnf = tput_config()

    title_width = int(
        cnf["init_width"]
        + (len(cnf["separator"]) / 2)
        - (len("WHAT ARE YOU LOOKING FOR") / 2)
    )

    title_str = "[»»] - What are you looking for? "

    with open("srch_q.bash", "w") as f:
        f.write("#!/usr/bin/env bash\n\n")
        f.write("tput clear\n\n")
        f.write(f"tput cup {cnf['init_height']} ")
        f.write(f"{title_width}\n")
        f.write(f"tput setaf {cnf['title_color']}\n")
        f.write("tput bold\n")
        f.write('echo "WHAT ARE YOU LOOKING FOR?"\n')
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


if __name__ == "__main__":
    srch_question()
