"""This module will create the encryption key that will
    be used in the new password database."""
import subprocess

import cryptography  # noqa: F401
import isort  # noqa: F401
import snoop
from cryptography.fernet import Fernet
from loguru import logger

fmt = "{time} - {name} - {level} - {message}"
logger.add("../logs/info.log", level="INFO", format=fmt, backtrace=True, diagnose=True)  # noqa: E501
logger.add("../logs/error.log", level="ERROR", format=fmt, backtrace=True, diagnose=True)  # noqa: E501

subprocess.run(["isort", __file__])


@logger.catch
@snoop
def create_encryption_key():
    """We create a symmetric encryption key with the
    algorithm Fernet and then pass it to a file."""

    key = Fernet.generate_key()
    print(key)

    with open("pwd.key", "wb") as f:
        f.write(key)


if __name__ == "__main__":
    create_encryption_key()
