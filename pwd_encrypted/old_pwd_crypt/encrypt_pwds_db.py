"""Module Docstring"""
import subprocess

import isort  # noqa: F401
import snoop
from cryptography.fernet import Fernet
from loguru import logger
from mysql.connector import Error, connect

fmt = "{time} - {name} - {level} - {message}"
logger.add("../logs/info.log", level="INFO", format=fmt, backtrace=True, diagnose=True)  # noqa: E501
logger.add("../logs/error.log", level="ERROR", format=fmt, backtrace=True, diagnose=True)  # noqa: E501

subprocess.run(["isort", __file__])


@logger.catch
@snoop
def encrypt_pwds():
    """Here we'll download the open passwords from the db,
    so we can encrypt them."""

    key = Fernet.generate_key()
    with open("password.key", "wb") as f:
        f.write(key)

    fernet = Fernet(key)
    encrypted_pwds = []

    try:
        conn = connect(host="localhost", user="mic", password="xxxx", database="pwd_encrypted")
        cur = conn.cursor()
        query = """ SELECT pwdid, passwd FROM pwd """
        cur.execute(query)
        records = cur.fetchall()
        for i in range(len(records)):
            token = fernet.encrypt(records[i][1].encode())
            encrypted_pwds.append((records[i][0], token))
    except Error as e:
        print("Error while connecting to db", e)
    finally:
        if conn:
            conn.close()

    print(encrypted_pwds)
    return encrypted_pwds


if __name__ == "__main__":
    encrypt_pwds()


@logger.catch
@snoop
def upload_encrypted_passwords():
    """Here we will replace the open passwords for the
    encrypted ones, in the database."""

    crypt_version = encrypt_pwds()

    try:
        conn = connect(host="localhost", user="mic", password="xxxx", database="pwd_encrypted")
        cur = conn.cursor()
        for crypt in crypt_version:
            args = (crypt[1], crypt[0])
            query = "UPDATE pwd SET crypto = %s WHERE pwdid = %s"
            cur.execute(query, args)
            conn.commit()
    except Error as e:
        print("Error while connecting to db", e)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    upload_encrypted_passwords()
