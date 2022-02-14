"""Module that searches and decodes password values."""
import subprocess

import isort  # noqa: F401
from colr import color
from cryptography.fernet import Fernet
from loguru import logger
from mysql.connector import Error, connect
from rich.console import Console
from rich.text import Text

fmt = "{time} - {name} - {level} - {message}"
logger.add("../logs/info.log", level="INFO", format=fmt, backtrace=True, diagnose=True)  # noqa: E501
logger.add("../logs/error.log", level="ERROR", format=fmt, backtrace=True, diagnose=True)  # noqa: E501

subprocess.run(["isort", __file__])


@logger.catch
def search():
    """"""

    with open("password.key", "rb") as f:
        key = f.read()

    fernet = Fernet(key)
    console = Console()

    try:
        busca = input(color(" [X] - What are you searching for? ", fore="#FF6701"))
        conn = connect(host="localhost", user="mic", password="xxxx", database="pwd")
        cur = conn.cursor()
        query = " SELECT pwdid, site, username, passwd, comment, time FROM pwd WHERE MATCH(site, username, comment) AGAINST ('" + busca + "')"
        cur.execute(query)
        records = cur.fetchall()
        for row in records:
            text0 = Text(f"++ ID ++ {row[0]}", justify="center")
            text0.stylize("bold #F6D7A7")
            console.print(text0)
            text1 = Text(f"++ SITE ++ {row[1]}", justify="center")
            text1.stylize("bold #87AAAA")
            console.print(text1)
            text2 = Text(f"++ USER ++ {row[2]}", justify="center")
            text2.stylize("bold #C8E3D4")
            console.print(text2)
            text3 = Text(f"++ PASSWORD ++ {row[3]}", justify="center")
            text3.stylize("bold F4D9C6")
            console.print(text3)
            text4 = Text(f"++ COMMENT ++ {row[4]}", justify="center")
            text4.stylize("bold #99A799")
            console.print(text4)
            text5 = Text(f"++ TIME ++ {row[5]}", justify="center")
            text5.stylize("bold #ADC2A9")
            console.print(text5)
            print("\n")

    except Error as e:
        print("Error while connecting to db", e)
        conn.close()

    print(fernet)


if __name__ == "__main__":
    search()
