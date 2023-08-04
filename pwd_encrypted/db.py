"""
MySQL module, to be shared by all modules.
"""
import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()


def dbdata(query, data, answers=None, location="."):
    """
    Collects list of posts on the db.
    We'll use this function as a template,
    letting the functions that call on it
    to define its structure. That being
    the query and if using .fetchall()
    or .commit()
    This permits writing just one db function
    per module.
    """
    db = os.getenv("DB_LOC")

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        if answers:
            cur.execute(query, answers)
        else:
            cur.execute(query)
        if data == "fetch":
            data = cur.fetchall()
        if data == "commit":
            data = conn.commit()
    except sqlite3.Error as e:
        print("Error while connecting to db", e)
    finally:
        if conn:
            conn.close()

    return data
