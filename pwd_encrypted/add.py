"""
This module deals with all operations about
inserting a new password in the database.
"""
import os
import random
import string

import snoop
from colr import color
from db_decorator.db_information import db_information
from english_words import get_english_words_set
from mysql.connector import Error, connect
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


@db_information
@snoop
def add():
    """
    We ask the user:
    1. Site name. Name of the site he wants a password for.
    2. Create his own password. By omission the module will
       create a password for the user, based on random
       selections from words from the english language and
       punctuation marks. But if the user wants to create it
       himself, we have this option.
    3. Password length. If the user chose the automatic
       creation of password, we ask how long does he want it.
       This will influence the number of words used.
    4. Comments. Any other information he would like to add.
    We upload the answers to the database, encrypt the
    password and print an ascii table with the choices made.
    """

    try:
        print("\n")
        sitio = input(color("  [*] What is the name of the site? ", fore="#fe7243"))
        username = input(color("  [*] What is the username? ", fore="#fe7243"))
        lgth = int(
            input(
                color(
                    "  [*] How long do you want your password to be? ", fore="#fe7243"
                )
            )
        )
        author = input(
            color(
                "  [*] Do you want to name the password yourself? [y/n] ",
                fore="#fe7243",
            )
        )
        comment = input(
            color("  [*] Any comments you would like to add? ", fore="#fe7243")
        )
        if author == "y":
            passwd = input(color("  [*] Input your password. ", fore="#fe7243"))
        else:
            pass

        # Gets the word list.
        word_lst = get_english_words_set(["gcide"])
        wordlst = list(word_lst)
        # Gets the punctuation list.
        punctuation = string.punctuation
        # 'k' is the password length chosen by the user.
        words = random.choices(wordlst, k=lgth)
        punct = random.choices(punctuation, k=int(lgth - 1))
        sam = words + punct
        # In 'sam' the words and punctuation are in order.
        # We want it mixed together.
        samp = random.sample(sam, int(lgth + (lgth - 1)))
        # Turns it from a list to a string.
        samp_str = " ".join(samp)
        # We get rid of the spaces, because a lot of sites
        # don't accept passwords with spaces.
        passwd = samp_str.replace(" ", "")

        answers = [sitio, username, passwd, comment]

        conn = connect(host="localhost", user="mic", password="xxxx", database="pwd")
        cur = conn.cursor()
        # With query1 we are checking if there is another site by the inputed.
        query1 = "SELECT * FROM pwd WHERE site LIKE %s"
        cur.execute(query1, (sitio,))
        records = cur.fetchall()
        # We transform records in a list, because we want to use a 'if ... in ...' expression, which is used in iterables only.
        records = list(records)
        for row in records:
            # Here is what we were talking about in the last comment
            if sitio in row:
                print(
                    color("  WARNING - ", fore="#fe7243"),
                    color(
                        "  For the site name that you gave us, we have the following records:",
                        fore="#fe7243",
                    ),
                )
                print("\n")
                print(
                    color("    Site - ", fore="#fe7243"), color(row[1], fore="#efb666")
                )
                print(
                    color("    Username - ", fore="#fe7243"),
                    color(row[2], fore="#efb666"),
                )
                print(
                    color("    Password - ", fore="#fe7243"),
                    color(row[3], fore="#efb666"),
                )
                print(
                    color("    Comment - ", fore="#fe7243"),
                    color(row[4], fore="#efb666"),
                )
                print("\n")
                dec = input(
                    color(
                        "  Do you want to continue inserting this record? [y/n] ",
                        fore="#fe7243",
                    )
                )
                print("\n")
                if dec == "n":
                    break
                if dec == "y":
                    pass
                else:
                    break

        # Here we begin the info insertion to the db. 'query2' is just the data we
        # collected from the questions before.
        query2 = (
            "INSERT INTO pwd (site, username, passwd, comment) VALUES (%s, %s, %s, %s)"
        )
        # On 'query4' we're going to encrypt the 'pwd' column entry. As the encryption
        # command doesn't work when you specify a line id, we have to use the 'update'
        # command. That means we have to know what is the last id to be inserted. For
        # this we use the command "MAX", that searches in a given column for the max
        # value in it.But the answer it's not the id line created by 'query2', it's
        # the id before that. Because of this we add 1 to the result, to have the
        # right column id.

        query3 = "SELECT MAX(pwdid) FROM pwd"
        cur.execute(query3)
        maxvtup = cur.fetchone()
        maxv = int(maxvtup[0] + 1)

        # The initial string used to create the key is kept in 'zshenv' as environment 
        # variable. We get it with 'os.environ()', and set 'key_str' active. 'key_str'
        # is a user variable, which means that it lasts the time of a session. To be
        # sure that is active, we set it before doing any encryption, or decryption work.
        aeskey = os.environ["AES_MYSQL_KEY"]
        answers4 = [aeskey]
        query4 = "SET @key_str = SHA2(%s, 512)"

        # This is the actual encryption command itself.
        answers5 = [passwd, maxv]
        query5 = "UPDATE pwd SET pwd = AES_ENCRYPT(%s, @key_str) WHERE pwdid = %s"

        for qry, ans in [(query2, answers), (query4, answers4), (query5, answers5)]:
            cur.execute(qry, ans)
            print(qry)
            conn.commit()
        conn.close()
    except Error as e:
        print("Error while connecting to db", e)

    # # And finally we print the inputed data, so the user can verify the information
    # added to the db. We'll be using a simple ascii table that'll insert by lines.
    # This might favour us when using it with tput. Most of the next chunk of code is
    # devoted to trying to get the correct width of the words and spaces, so as to make
    # the table lines align.

    # List with the collected variable results.
    teste = [sitio, username, passwd, comment]
    # The titles of the variables that will use in the table.
    names = ["site", "user", "pwd", "comment"]
    # Lists with the length of the variables and names strings.
    lens_tst = [len(ts) for ts in teste]
    lens_nms = [len(nm) for nm in names]
    # The next loop will ascertain from each of the last two
    # lists, which element has the bigger length. That way we
    # know that the table cell of the respective line, will have
    # to have at least the width. The loop compares each result
    # to a 'standard' one which, by convention, is the first one
    # of each list. The next two variables initiate those values.
    val_tst = lens_tst[0]
    val_nms = lens_nms[0]
    # Initiating lists needed for the loop. They'll collect the
    # the highest length value of each list.
    hi_ln_tst = []
    hi_ln_nms = []
    # These two are here because I was having the annoying
    # 'unbound local error' error, and this was the simple
    # way of dealing with it.
    hi_len_tst = ""
    hi_len_nms = ""

    # This is the loop I talked about earlier. This one is specific
    # to the collected variables lengths.
    for lt in lens_tst:
        if lt > val_tst:
            val_tst = lt
            hi_ln_tst.append(val_tst)
    # The loop should, but it doesn't, return just one value, but
    # it's returning all values higher than the first variable
    # length. Because of this, we have to deal when the result is
    # a string or a list. If it's a list, we run the 'max' function.
    if len(hi_ln_tst) == 1:
        hi_len_tst = hi_ln_tst[0]
    if len(hi_ln_tst) > 1:
        hi_len_tst = max(hi_ln_tst)

    # This loop is the same as the last one, but now just for the
    # answers list.
    for ln in lens_nms:
        if ln > val_nms:
            val_nms = ln
            hi_ln_nms.append(val_nms)
    if len(hi_ln_nms) == 1:
        hi_len_nms = hi_ln_nms[0]
    if len(hi_ln_nms) > 1:
        hi_len_nms = max(hi_ln_nms)

    # This variable measures the highest width of a line, by adding
    # the highest lengths in both lists and plus 3, to account for
    # the spaces between the strings. Case in point: ' | '.
    vh = int(hi_len_tst + hi_len_nms + 3)
    # Variable of the character that'll be used to build the upper and
    # lower separators on each line.
    sep = "-"
    # This creates a string, made of consecutive '-' characters,
    # multiplied by the width of the longest strings in both lists.
    # This is a way to print repeating characters on a string.
    traces = "".join(sep * vh)
    # The border in ascii squares have '+' signs on their vertices and
    # start two pixels before the cell content, and end two pixels afer
    # their end. This variable adds to the start and end of the separators
    # these characters.
    ntraces = f"  +-{traces}-+"
    # The final width of the ascii box, if the cells of each list are at its
    # highest length.
    ud_len = len(ntraces)

    # Finally we print the results. The space is to separate the table from the
    # terminal prompt.
    print("\n")
    # Printing the upper separator.
    print(ntraces)
    # Loop that'll print the contents of the lists in the same line; first the
    # title of the line, then its value. We zip the lists, so we can pair the
    # title with its corresponding value.
    for n, t in zip(names, teste):
        # Defines the length of the cell of title or name/value that is not
        # ocuppied by string itself. This empty space will be added to the
        # string when printing; so as to have always cells that are at least
        # as wide as the widest element on their respective columns.
        n_len = int(hi_len_nms - len(n))
        t_len = int(hi_len_tst - len(t))
        # These are printable representations of the length of spaces defined
        # on the last two variables.
        space_n = "".join(" " * n_len)
        space_t = "".join(" " * t_len)
        # Prints each line two pixels apart from the left border of the terminal,
        # adds a vertical separator and one space, the title string and the spaces
        # defined before. Adds ' | ' as line separator, and does the same for the
        # names/values strings.
        print(f"  | {n}{space_n} | {t}{space_t} |")
        # Prints the closing seprator.
        print(ntraces)
    print("\n")


if __name__ == "__main__":
    add()
