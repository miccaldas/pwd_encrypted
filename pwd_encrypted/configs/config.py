"""
We gather here all variables that we want to make available
to the rest of the project. To add a new set of configurations,
just create a new function to house them and call it from
whatever module needs it.
"""
import os

import snoop
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


@snoop
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
