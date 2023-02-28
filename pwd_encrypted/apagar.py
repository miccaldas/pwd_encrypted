"""Module Docstring"""
import snoop
from db_decorator.db_information import db_information
from reusable_files import tput_page_config
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


@db_information
@snoop
def apagar():
    """"""
    sepr = tput_page_config.separator
    print(sepr)


if __name__ == "__main__":
    apagar()
