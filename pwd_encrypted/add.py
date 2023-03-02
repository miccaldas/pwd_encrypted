"""
This module deals with all operations about
inserting a new password in the database.
"""
import os
import pickle
import random
import string
import subprocess

import snoop
from colr import color
from db_decorator.db_information import db_information
from english_words import get_english_words_set
from mysql.connector import Error, connect
from snoop import pp


def type_watch(source, value):
    return "type({})".format(source), type(value)


snoop.install(watch_extras=[type_watch])


class Add:
    """
    Due to the fact that I still haven't figured out a faster
    way to take information from a bash script to Python,
    that isn't a file of some sort, I have to separate the
    rendering of the bash scripts from the python analysis of
    their data. If I render and try to open it too son, I'll
    just have a ton 'file not found errors'. So the way to go
    is to separate this moments on their own functions. But,
    since this means a lot of new pages that share the same
    template, and the information flows from one to the next,
    it seems natural that a class is the solution.
    """

    terminal_size = os.get_terminal_size()
    height = terminal_size.lines
    width = terminal_size.columns
    sitio_str = "[»»] What is the name of the site? "
    username_str = "[»»] What is the username? "
    lgth_str = "[»»] How long do you want your password to be? "
    author_str = "[»»] Do you want to name the password yourself? [y/n] "
    author_y_str = "[»»] Input your password. "
    comment_str = "[»»] Do you want to add a comment? "
    warning_str = "For the site name that you gave us, we have the following records:"
    warning_question_str = "Do you want to continue inserting this record? [y/n] "
    init_height = int(height / 4)
    init_width = int(width / 4)
    init_pos = f"{init_height} {init_width}"
    separator_height = int(init_height + 3)
    separator = "------------------------------ [X] ------------------------------"
    separator_width = init_width
    sitio_width = init_width
    username_width = init_width
    lgth_width = init_width
    author_width = init_width
    author_y_width = init_width
    comment_width = init_width
    warning_width = init_width
    warning_question_width = init_width
    space_under_separator = separator_height + 12
    title_color = 1

    def __init__(self):
        pass

    # @snoop
    def first_input_window(self):
        """
        Agreggates the site, username and password authorship
        questions. We break the questions loop, so we can run
        the function that checks for repeats and asks the user
        input on how to proceed and the function dedicated to
        password authorship.
        """

        with open("add.bash", "w") as f:
            f.write("#!/usr/bin/env bash\n\n")
            f.write("tput clear\n\n")
            f.write(f"tput cup {Add.init_pos}\n")
            f.write(f"tput setaf {Add.title_color}\n")
            f.write("tput bold\n")
            f.write('echo "ADD PASSWORD"\n')
            f.write("tput sgr0\n\n")
            f.write("")

            f.write(f"tput cup {Add.separator_height} {Add.separator_width}\n")
            f.write(f"echo '{Add.separator}'\n")

            f.write(f"tput cup {Add.separator_height + 4} {Add.sitio_width}\n")
            f.write(f"read -p '{Add.sitio_str}: ' choice\n")
            f.write('echo "${choice}" > sitio_choice.txt\n')

            f.write(f"tput cup {Add.separator_height + 6} {Add.username_width}\n")
            f.write(f'read -p "{Add.username_str}: " choice\n')
            f.write('echo "${choice}" > username_choice.txt\n')

            f.write(f"tput cup {Add.separator_height + 8} {Add.author_width}\n")
            f.write(f'read -p "{Add.author_str}: " choice\n')
            f.write('echo "${choice}" > author_choice.txt\n')

            f.write("tput clear\n")
            f.write("tput sgr0\n")
            f.write("tput rc")

        subprocess.run("sudo chmod +x add.bash", cwd=os.getcwd(), shell=True)
        subprocess.run("./add.bash", cwd=os.getcwd(), shell=True)

    @db_information
    # @snoop
    def check_repeats(self):
        """
        We check with the database to see if there's already an entry with
        the same site's name. If there are, we present the information to
        the user and ask him if he wants to continue inputing the entry or
        if he wants to abort. In the first case we do nothing and the
        program continues, in the other, we exit the program.
        """
        query1 = "SELECT * FROM pwd WHERE site LIKE %s"

        lst_files = os.listdir(os.getcwd())

        if "sitio_choice.txt" in lst_files:
            with open("sitio_choice.txt", "r") as f:
                dirty_site = f.read()
                sitio = dirty_site.strip()
                conn = connect(
                    host="localhost", user="mic", password="xxxx", database="pwd"
                )
                cur = conn.cursor()
                cur.execute(query1, (sitio,))
                records = cur.fetchone()
                if records:
                    with open("site_repeat.bash", "w") as f:
                        f.write("#!/usr/bin/env bash\n\n")
                        f.write("tput clear\n\n")
                        f.write(f"tput cup {Add.init_height} {Add.warning_width}\n")
                        f.write(f"tput setaf {Add.title_color}\n")
                        f.write("tput bold\n")
                        f.write('echo "WARNING!"\n')
                        f.write("tput sgr0\n\n")
                        f.write("")

                        f.write(
                            f"tput cup {Add.separator_height} {Add.warning_width}\n"
                        )
                        f.write(f"echo '{Add.separator}'\n")

                        f.write(
                            f"tput cup {Add.separator_height + 2} {Add.warning_width}\n"
                        )
                        f.write(f'echo "{Add.warning_str}"\n')

                        f.write(
                            f"tput cup {Add.separator_height + 4 + 1} {Add.warning_width}\n"
                        )
                        f.write(f"tput setaf {Add.title_color}\n")
                        f.write("tput bold\n")
                        f.write(f'echo ID. "{records[0]}"\n')
                        f.write("tput sgr0\n\n")

                        f.write(
                            f"tput cup {Add.separator_height + 4 + 2} {Add.warning_width}\n"
                        )
                        f.write(f'echo Site. "{records[1]}"\n')

                        f.write(
                            f"tput cup {Add.separator_height + 4 + 3} {Add.warning_width}\n"
                        )
                        f.write(f'echo Username. "{records[2]}"\n')

                        f.write(
                            f"tput cup {Add.separator_height + 4 + 4} {Add.warning_width}\n"
                        )
                        f.write(f'echo Password. "{records[4]}"\n')

                        f.write(
                            f"tput cup {Add.separator_height + 4 + 5} {Add.warning_width}\n"
                        )
                        f.write(f'echo Comment. "{records[5]}"\n')

                        f.write(
                            f"tput cup {Add.separator_height + 4 + 6} {Add.warning_width}\n"
                        )
                        f.write(f'echo Time. "{records[6]}"\n')

                        f.write(
                            f"tput cup {Add.separator_height + 4 + 8} {Add.warning_width}\n"
                        )
                        f.write(f'read -p "{Add.warning_question_str} " choice\n')
                        f.write('echo "${choice}" > warning_choice.txt\n')

                        f.write("tput clear\n")
                        f.write("tput sgr0\n")
                        f.write("tput rc")

                        subprocess.run(
                            "sudo chmod +x site_repeat.bash",
                            cwd=os.getcwd(),
                            shell=True,
                        )
                        subprocess.run(
                            "./site_repeat.bash", cwd=os.getcwd(), shell=True
                        )
        else:
            print("Couldn't find 'sitio_choice.txt' file")

    # @snoop
    def pwd_authorship(self):
        """
        Checks the results of the 'author' question, done by
        'add_input_window', in the 'author_choice.txt' file,
        if yes, collects their choice in a file, if no, it
        exits the app.
        """
        lst_files = os.listdir(os.getcwd())

        if "author_choice.txt" in lst_files:
            with open("author_choice.txt", "r") as f:
                dirty_author = f.read()
                author = dirty_author.strip()

            if author == "y":
                with open("author_y.bash", "w") as f:
                    f.write("#!/usr/bin/env bash\n\n")
                    f.write("tput clear\n\n")
                    f.write(f"tput cup {Add.init_height} {Add.warning_width}\n")
                    f.write(f"tput setaf {Add.title_color}\n")
                    f.write("tput bold\n")
                    f.write('echo "PASSWORD"\n')
                    f.write("tput sgr0\n\n")
                    f.write("")

                    f.write(f"tput cup {Add.separator_height} {Add.warning_width}\n")
                    f.write(f"echo '{Add.separator}'\n")

                    f.write(
                        f"tput cup {Add.separator_height + 2} {Add.warning_width}\n"
                    )
                    f.write(f'read -p "{Add.author_y_str} " choice\n')
                    f.write('echo "${choice}" > author_y.txt\n')

                    f.write("tput clear\n")
                    f.write("tput sgr0\n")
                    f.write("tput rc")
                    f.close()

                    subprocess.run(
                        "sudo chmod +x author_y.bash", cwd=os.getcwd(), shell=True
                    )
                    subprocess.run("./author_y.bash", cwd=os.getcwd(), shell=True)
        else:
            print("Couldn't find 'author_choice.txt'.")

    # @snoop
    def second_input_window(self):
        """
        This method ends the questionnary. We'll create
        two different pipelines, one for those who made
        their own password, and for those who didn't.
        We'll create a window with the questions still
        not made, length of password and comment.
        """
        lst_files = os.listdir(os.getcwd())

        if "author_choice.txt" in lst_files:
            with open("author_choice.txt", "r") as f:
                dirty_author = f.read()
                author = dirty_author.strip()

            with open("second_input.bash", "w") as f:
                f.write("#!/usr/bin/env bash\n\n")
                f.write("tput clear\n\n")
                f.write(f"tput cup {Add.init_height} {Add.warning_width}\n")
                f.write(f"tput setaf {Add.title_color}\n")
                f.write("tput bold\n")
                f.write('echo "PASSWORD"\n')
                f.write("tput sgr0\n\n")
                f.write("")

                f.write(f"tput cup {Add.separator_height} {Add.warning_width}\n")
                f.write(f"echo '{Add.separator}'\n")

                if author == "n":
                    f.write(
                        f"tput cup {Add.separator_height + 2} {Add.warning_width}\n"
                    )
                    f.write(f'read -p "{Add.lgth_str} " choice\n')
                    f.write('echo "${choice}" > lgth_choice.txt\n')
                    f.write(
                        f"tput cup {Add.separator_height + 4} {Add.warning_width}\n"
                    )
                    f.write(f'read -p "{Add.comment_str} " choice\n')
                    f.write('echo "${choice}" > comment_choice.txt\n')

                if author == "y":
                    f.write(
                        f"tput cup {Add.separator_height + 4} {Add.warning_width}\n"
                    )
                    f.write(f'read -p "{Add.comment_str} " choice\n')
                    f.write('echo "${choice}" > comment_choice.txt\n')

                f.write("tput clear\n")
                f.write("tput sgr0\n")
                f.write("tput rc")
                f.close()

                subprocess.run(
                    "sudo chmod +x second_input.bash", cwd=os.getcwd(), shell=True
                )
                subprocess.run("./second_input.bash", cwd=os.getcwd(), shell=True)

    @db_information
    # @snoop
    def add(self):
        """
        First we collect all the information gathered on the
        questions of the methods before. Then we create the
        mechanism to generate passwords and pass them through
        it. After we send the treated information into the
        database.
        """

        lst_files = os.listdir(os.getcwd())

        with open("sitio_choice.txt", "r") as d:
            dirty_site = d.read()
            sitio = dirty_site.strip()
        with open("username_choice.txt", "r") as g:
            use_dirty = g.read()
            username = use_dirty.strip()
        with open("comment_choice.txt", "r") as e:
            com_dirty = e.read()
            comment = com_dirty.strip()

        if "author_y.txt" in lst_files:
            with open("author_y.txt", "r") as p:
                pwd_dirty = p.read()
                passwd = pwd_dirty.strip()

        if "author_choice.txt" in lst_files:
            with open("author_choice.txt", "r") as h:
                autopwd_dirty = h.read()
                pwd_request = autopwd_dirty.strip()
            if pwd_request == "n":
                if "lgth_choice.txt" in lst_files:
                    with open("lgth_choice.txt", "r") as r:
                        lgth_dirty = r.read()
                        lgt = lgth_dirty.strip()
                        lgth = int(lgt)
                        # This moment starts the building of the password.
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

                        try:
                            # Here we begin the info insertion to the db. 'query2' is just the data we
                            # collected from the questions before.
                            query2 = "INSERT INTO pwd (site, username, passwd, comment) VALUES (%s, %s, %s, %s)"
                            # On 'query4' we're going to encrypt the 'pwd' column entry. As the encryption
                            # command doesn't work when you specify a line id, we have to use the 'update'
                            # command. That means we have to know what is the last id to be inserted. For
                            # this we use the command "MAX", that searches in a given column for the max
                            # value in it.But the answer it's not the id line created by 'query2', it's
                            # the id before that. Because of this we add 1 to the result, to have the
                            # right column id.
                            conn = connect(
                                host="localhost",
                                user="mic",
                                password="xxxx",
                                database="pwd",
                            )
                            cur = conn.cursor()
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

                            for qry, ans in [
                                (query2, answers),
                                (query4, answers4),
                                (query5, answers5),
                            ]:
                                cur.execute(qry, ans)
                                print(qry)
                                conn.commit()
                            conn.close()
                        except Error as e:
                            print("Error while connecting to db", e)

                        answers = [sitio, username, passwd, comment]

                        with open("answers.bin", "wb") as y:
                            pickle.dump(answers, y)

    # @snoop
    def add_insertion_window(self):
        """
        We build a window wuth the values supplied by the user, so he
        can verify if everything is correct. We presented them in a
        simple ascii table.
        """
        with open("answers.bin", "rb") as u:
            teste = pickle.load(u)

        # # And finally we print the inputed data, so the user can verify the information
        # added to the db. We'll be using a simple ascii table that'll insert by lines.
        # This might favour us when using it with tput. Most of the next chunk of code is
        # devoted to trying to get the correct width of the words and spaces, so as to make
        # the table lines align.

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


add = Add()
add.first_input_window()
add.check_repeats()
add.pwd_authorship()
add.second_input_window()
add.add()
add.add_insertion_window()
