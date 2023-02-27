"""Module Docstring"""
import codecs
import pickle
import random
import string
from base64 import b64decode, b64encode

import snoop
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# from cryptography.fernet import Fernet
from db_decorator.db_information import db_information
from english_words import get_english_words_set
from mysql.connector import Error, connect
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


@db_information
@snoop
def teste():
    """"""
    word_lst = get_english_words_set(["gcide"])
    wordlst = list(word_lst)
    print(len(word_lst))
    print(type(word_lst))
    punctuation = string.punctuation
    print(len(punctuation))
    print(type(punctuation))

    wds = random.choices(wordlst, k=4)
    print(wds)
    pct = random.choices(punctuation, k=3)
    print(pct)
    sam = wds + pct
    print(sam)
    samp = random.sample(sam, 6)
    sampe = " ".join(samp)
    sample = sampe.replace(" ", "")
    print(sample)


# if __name__ == "__main__":
#  teste()


# @db_information
# @snoop
# def crypto():
#     # master_key = Fernet.generate_key()
#     # with open("mk.bin", "wb") as f:
#     #   pickle.dump(master_key, f)

#     with open("mk.bin", "rb") as f:
#         mk = pickle.load(f)

#     # print(dec_text)

#     #    try:
#     #       answers = [d64, 656]
#     #       conn = connect(host="localhost", user="mic", password="xxxx", database="pwd")
#     #      cur = conn.cursor()
#     #      query = "UPDATE pwd SET test = %s WHERE pwdid = %s"
#     #     cur.execute(query, answers)
#     #    conn.commit()
#     #  except Error as e:
#     #     err_msg = "Error while connecting to db", e
#     #    print("Error while connecting to db", e)
#     #   if err_msg:
#     #      return query, err_msg
#     #  finally:
#     #     if conn:
#     #        conn.close()

#     with open("id_pwd.bin", "rb") as f:
#         records = pickle.load(f)
# #    cipher_suite = Fernet(mk)
# #    cipher_text = cipher_suite.encrypt('3PU5wne!gIGYAF"=dcqMLa~'.encode())
#     # d64 = b64encode(cipher_text)

#     # print(f"d64 is: {d64}")
# #    print(cipher_text)

#     try:
#         conn = connect(host="localhost", user="mic", password="xxxx", database="pwd")
#         cur = conn.cursor()
#  #       answers = [f"{cipher_text}", "657"]
#         query = "UPDATE pwd SET pwd = %s WHERE pwdid = %s"
#         cur.execute(query, answers)
#         conn.commit()
#     except Error as e:
#         err_msg = "Error while connecting to db", e
#         print("Error while connecting to db", e)
#         if err_msg:
#             return query, err_msg
#     finally:
#         if conn:
#             conn.close()

#     try:
#         answers = [657]
#         conn = connect(host="localhost", user="mic", password="xxxx", database="pwd")
#         cur = conn.cursor()
#         query = "SELECT pwd FROM pwd WHERE pwdid = %s"
#         cur.execute(query, answers)
#         record = cur.fetchone()
#     except Error as e:
#         err_msg = "Error while connecting to db", e
#         print("Error while connecting to db", e)
#         if err_msg:
#             return query, err_msg
#     finally:
#         if conn:
#             conn.close()

#     print(record)
#     # decs = b64decode(record[0])
#     print(record[0])
# #    uncipher = cipher_suite.decrypt(record[0])
# #    pwd_str = bytes(uncipher).decode("utf-8")
# #    print(pwd_str)
#  #   print(type(pwd_str))


@snoop
def crypto_dome():
    data = b"|NjRJl[3%_)kZV=!<}hHzQw"
    #key = get_random_bytes(16)
    #with open("aes_key.bin", "wb") as f:
   #     pickle.dump(key, f)

    with open("aes_key.bin", "rb") as f:
        aes_key = pickle.load(f)
    print(aes_key)

    cipher = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    nonce = cipher.nonce

    try:
        conn = connect(host="localhost", user="mic", password="xxxx", database="pwd")
        cur = conn.cursor()
        answers = [f"{ciphertext}", f"{tag}", "657"]
        query = "UPDATE pwd SET pwd = %s,  tag = %s WHERE pwdid = %s"
        cur.execute(query, answers)
        conn.commit()
    except Error as e:
        err_msg = "Error while connecting to db", e
        print("Error while connecting to db", e)
        if err_msg:
            return query, err_msg
    finally:
        if conn:
            conn.close()

    try:
        answers = [657]
        conn = connect(host="localhost", user="mic", password="xxxx", database="pwd")
        cur = conn.cursor()
        query = "SELECT tag, pwd FROM pwd WHERE pwdid = %s"
        cur.execute(query, answers)
        records = cur.fetchall()
    except Error as e:
        err_msg = "Error while connecting to db", e
        print("Error while connecting to db", e)
        if err_msg:
            return query, err_msg
    finally:
        if conn:
            conn.close()

    # file_out = open("encrypted.bin", "wb")
    # [file_out.write(x) for x in (ciphertext)]
    # file_out.close()

    # with open("encrypted.bin", "rb") as f:
    #     ciphertext = [f.read(x) for x in (16, 16, -1)]

    print(records)
    print(type(records[0][0]))
    print(type(records[0][1]))
    ciphertext = records[0][1]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    datastr = data.decode()
    print(datastr)


if __name__ == "__main__":
    crypto_dome()
