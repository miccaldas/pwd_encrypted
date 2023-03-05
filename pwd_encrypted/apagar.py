"""Module Docstring"""
# from db_decorator.db_information import db_information
# from configs.config import tput_config
import os
import subprocess

import snoop
from dotenv import load_dotenv
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()


# @db_information
@snoop
def apagar():
    """"""

    enc = "/home/mic/python/pwd_encrypted/pwd_encrypted/enc"
    dec = "/home/mic/python/pwd_encrypted/pwd_encrypted/dec"

    # cmd = f"echo 'Ih|%çe\\`Vknu;)0AO_lLUT5iH-Gx^qo9j<3fm$>8d.7SY2' | encfs --standard --stdinpass {enc} {dec}"
    cmd = f"echo 'Ih|%çe\\`Vknu;)0AO_lLUT5iH-Gx^qo9j<3fm$>8d.7SY2' | encfs --stdinpass {enc} {dec}"
    subprocess.run(cmd, cwd=os.getcwd(), shell=True)


if __name__ == "__main__":
    apagar()
