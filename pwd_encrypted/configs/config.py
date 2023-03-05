"""
We gather here all variables that we want to make available
to the rest of the project. To add a new set of configurations,
just create a new function to house them and call it from
whatever module needs it.
"""
import os
import subprocess
import snoop
from snoop import pp
from dotenv import load_dotenv


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()


# @snoop
def tput_config():
    """
    Configuration variables for Tput windows.
    """

    # Variable declaration. The variables that are here are the result, in form
    # or another, of python code. It just seems cleaner to present them this way.
    tputs = dict()
    termsize = os.get_terminal_size()
    width = termsize.columns
    height = termsize.lines
    init_height = int(height / 4)
    init_width = int(width / 4)
    lines = termsize.lines
    init_pos = f"{init_height} {init_width}"
    separator_height = int(init_height + 3)
    space_under_separator = int(height - 1)

    # Builds a dictionary that other modules can use.
    tputs["width"] = width
    tputs["height"] = height
    tputs["init_height"] = init_height
    tputs["init_width"] = init_width
    tputs["init_pos"] = init_pos
    tputs["separator_height"] = separator_height
    tputs["space_under_separator"] = space_under_separator
    tputs[
        "separator"
    ] = "------------------------------ [X] ------------------------------"
    tputs["title_color"] = 1

    return tputs


if __name__ == "__main__":
    tput_config()


class Efs:
    """
    Houses three methods,
    1. create,
    2, mount.
    3, unmount.
    'create' has already ran
    and, probably, we won't
    be needing it again. The
    other two start and stop
    the encryption in PWD_SEC_LOC
    """
    dec = os.getenv("PWD_SEC_LOC")
    enc = os.getenv("PWD_ENC_LOC")
    encfs_pwd = os.getenv("PWD_FLD_KEY")

    def __init__(self):
        pass

    #@snoop
    def create(self):
        """
        Creates a new fylesystem.
        This was already run and
        doesn't need to be ran
        again, except in case of
        catastrophic failure.
        It's here for documentaion
        purposes.
        """

        cmd = f"echo '{Efs.encfs_pwd}' | encfs --standard --stdinpass {Efs.enc} {Efs.dec}"
        # cmd = f'echo "Ih|%çe\`Vknu;)0AO_lLUT5iH-Gx^qo9j<3fm$>8d.7SY2" | encfs --stdinpass {enc} {dec}'
        subprocess.run(cmd, shell=True)

    #@snoop
    def mount(self):
        """ 
        Mounts the encrypted folder back up.
        You'll see now files inside the folder.
        """

        cmd = f"echo '{Efs.encfs_pwd}' | encfs --stdinpass {Efs.enc} {Efs.dec}"
        subprocess.run(cmd, shell=True)

    #@snoop
    def unmount(self):
        """
        When unmounting, the 'pwd' folder will
        appear empty and 'pwd_enc' encrypted
        versions will still be visible
        """

        cmd = f"encfs -u {Efs.dec}"
        subprocess.run(cmd, shell=True)
