"""
Purges all transient files created.
"""
import os

import snoop
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


# @snoop
def clean():
    """
    We'll be deleting all text, bash and bin
    files in this folder. We'll use os for
    that.
    """

    cwd = os.getcwd()
    lst_files = os.listdir(cwd)

    del_lst = [".txt", ".bin", ".bash"]

    for file in lst_files:
        for d in del_lst:
            if file.endswith(d):
                os.remove(f"{cwd}/{file}")


if __name__ == "__main__":
    clean()

