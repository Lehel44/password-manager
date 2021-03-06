from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import random
import hashlib
import os
import re
import smtplib
import datetime
import getpass

symbols = set('''.,;:?!'"-_{}@&#<>[]ß×÷|\~^''')
enc = 'iso-8859-15'

def print_menu():
    print(31 * "-", "MENU", 30 * "-")
    print("1. Register")
    print("2. Login")
    print("3. Forgot your password?")
    print("4. Quit")
    print(67 * "-")


def print_manage_menu():
    print(22 * "-", "MANAGE YOUR PASSWORDS", 22 * "-")
    print("1. List passwords with description")
    print("2. Add new password with description")
    print("3. Modify password or description")
    print("4. Delete password")
    print("5. Change account password")
    print("6. Log out")
    print(67 * "-")


def print_add_password_menu():
    print(25 * "-", "ADD NEW PASSWORD", 24 * "-")
    print("1. Give own password")
    print("2. Generate strong random password")
    print("3. Back")
    print(67 * "-")


def print_password_table():
    rows, columns = os.popen('stty size', 'r').read().split()
    columns = int(columns)

    if not os.stat(path).st_size == 0:
        is_mac_valid, decrypted_data = decrypt_file(path)
        if is_mac_valid:
            lines = decrypted_data.split('\n')
            passwords = []
            descriptions = []

            now = datetime.datetime.now()
            today = date(now.year, now.month, now.day)

            for x in range(0, len(lines)):
                if (x % 3) == 0:
                    passwords.append(lines[x])
                if (x % 3) == 1:
                    date_list = [0, 0, 0]
                    for y in range(0,3):
                        pos = lines[x].find('.')
                        date_list[y] = int(lines[x][:pos])
                        lines[x] = lines[x][pos+1:]
                    creation_day = date(date_list[0], date_list[1], date_list[2])
                    delta = (today - creation_day).days
                    if delta >= 90:
                        lines[x] = "(EXPIRED) " + lines[x]
                    else:
                        lines[x] = "(" + str(90 - delta) + ") " + lines[x]
                    descriptions.append(lines[x])

            pass_cols = max(len(max(passwords, key=len)), 8)
            desc_cols = max(len(max(descriptions, key=len)), 11)
            desc_cols = min(desc_cols, columns - 13 - pass_cols)

            if columns < (pass_cols + 53):
                print("Please widen your console to list passwords.")
            else:
                print("╔═════╦═" + pass_cols * "═" + "═╦═" + desc_cols * "═" + "═╗")
                print("║ Id  ║ Password" + (pass_cols - 8) * " " + " ║ Description" +
                      (desc_cols - 11) * " " + " ║")

                for x in range(0, len(passwords)):
                    if len(descriptions[x]) > desc_cols:
                        description_part = descriptions[x]
                        concatenation = ""
                        while len(description_part) > desc_cols:
                            concatenation += description_part[:desc_cols] + " ║\n" + "║     ║ " + \
                                             pass_cols * " " + " ║ "
                            description_part = description_part[desc_cols:]

                        concatenation += description_part + \
                                         (desc_cols - len(description_part)) * " "
                        descriptions[x] = concatenation

                    print("╠═════╬═" + pass_cols * "═" + "═╬═" + desc_cols * "═" + "═╣")
                    print("║ " + (3 - len(str(x))) * " " + str(x + 1) + " ║ " +
                          (pass_cols - len(passwords[x])) * " " + passwords[x] + " ║ " +
                          descriptions[x] + (desc_cols - len(descriptions[x])) * " " + " ║")

                print("╚═════╩═" + pass_cols * "═" + "═╩═" + desc_cols * "═" + "═╝")
                return len(passwords)
    else:
        os.system('clear')
        print(26 * "-", "LIST PASSWORDS", 25 * "-")
        print("")
        if columns < 31:
            print("Please widen your console to list passwords.")
        else:
            print("╔════╦══════════╦═════════════╗")
            print("║ Id ║ Password ║ Description ║")
            print("╠════╬══════════╬═════════════╣")
            print("║    ║          ║             ║")
            print("╚════╩══════════╩═════════════╝")
        return 0


def long_enough(pw):
    if len(pw) > 7:
        print("✔ Password is long enough")
        return True
    else:
        print("✖ Password is less than 8 characters")
        return False


def contains_letter(pw):
    if any(char.isalpha() for char in pw):
        print("✔ Password contains letter")
        return True
    else:
        print("✖ Password does not contain letter")
        return False


def contains_number(pw):
    if any(char.isdigit() for char in pw):
        print("✔ Password contains number")
        return True
    else:
        print("✖ Password does not contain number")
        return False


def contains_symbol(pw):
    if any((c in symbols) for c in pw):
        print("✔ Password contains symbol")
        return True
    else:
        print("✖ Password does not contain symbol")
        return False


def pbkdf_gen(password):
    salt = hashlib.sha256().digest()
    key_size = 256
    keys = PBKDF2(password, salt, count=20000, dkLen = key_size * 2)
    return keys


def generate_random_strong_password():
    dic = '''abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.,;:?!'"-_{}@&#<>[]ß×÷|\~^'''
    length = 32

    strong = False
    while not strong:
        generated_pass = "".join(random.sample(dic, length))
        if any(char.isalpha() for char in generated_pass):
            if any(char.isdigit() for char in generated_pass):
                if any((c in symbols) for c in generated_pass):
                    strong = True

    return generated_pass


def decrypt_file(path):
    file_in = open(path, 'r')
    pw_file_text = file_in.readlines()
    file_in.close()
    aad, ciphertext, tag, nonce, kdf_salt = pw_file_text

    aad = aad[:-1]
    ciphertext = str.encode(ciphertext[2:-2])
    ciphertext = ciphertext.decode('unicode-escape').encode('ISO-8859-1')
    tag = str.encode(tag[2:-2])
    tag = tag.decode('unicode-escape').encode('ISO-8859-1')
    nonce = str.encode(nonce[2:-2])
    nonce = nonce.decode('unicode-escape').encode('ISO-8859-1')
    kdf_salt = str.encode(kdf_salt[2:-1])
    kdf_salt = kdf_salt.decode('unicode-escape').encode('ISO-8859-1')

    decryption_key = PBKDF2(login_pw, kdf_salt)
    cipher = AES.new(decryption_key, AES.MODE_GCM, nonce)
    cipher.update(str.encode(aad))
    try:
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        decrypted_data = decrypted_data.decode('utf-8')
    except ValueError as mac_mismatch:
        input("✖ MAC validation failed during decryption. No authentication guarantees on your password file.\n"
              "Press Enter to continue...")
        os.system('clear')
        return False, ''
    return True, decrypted_data


def encrypt_file(data, path, message, password):
    kdf_salt = get_random_bytes(32)
    key = PBKDF2(password, kdf_salt)
    aad = "Operation Overlord"
    cipher = AES.new(key, AES.MODE_GCM)
    cipher.update(str.encode(aad))
    ciphertext, tag = cipher.encrypt_and_digest(str.encode(data))
    nonce = cipher.nonce

    with open(path, 'w') as f:
        f.write(aad)
        f.write('\n')
        f.write(str(ciphertext))
        f.write('\n')
        f.write(str(tag))
        f.write('\n')
        f.write(str(nonce))
        f.write('\n')
        f.write(str(kdf_salt))
    f.close()
    input(message)


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


def modify_password_or_description(id, modify_password, password, modify_description, description, path):
    is_mac_valid, decrypted_data = decrypt_file(path)
    if is_mac_valid:
        lines = decrypted_data.split('\n')
        if modify_password == 'n' and modify_description == 'y':
            old_desc = lines[(id - 1) * 3 + 1]
            pos = find_nth(old_desc, '.', 3) + 1
            date = old_desc[:pos]
            description = date + description
            lines[(id - 1) * 3 + 1] = description

        if modify_password == 'y' and modify_description == 'n':
            now = datetime.datetime.now()
            date = str(now.year) + '.' + str(now.month) + '.' + str(now.day) + '.'
            old_desc = lines[(id - 1) * 3 + 1]
            pos = find_nth(old_desc, '.', 3) + 1
            description = date + old_desc[pos:]
            lines[(id - 1) * 3] = password
            lines[(id-1) * 3 + 1] = description

        if modify_password == 'y' and modify_description == 'y':
            now = datetime.datetime.now()
            date = str(now.year) + '.' + str(now.month) + '.' + str(now.day) + '.'
            description = date + description
            lines[(id - 1) * 3] = password
            lines[(id-1) * 3 + 1] = description

        data = "\n".join(lines)
        message = "✔ Modification is successfully saved.\nPress Enter to continue..."
        encrypt_file(data, path, message, login_pw)
    else:
        return


def delete_password(id, number_of_id, path):
    is_mac_valid, decrypted_data = decrypt_file(path)
    if is_mac_valid:
        lines = decrypted_data.split('\n')

        if number_of_id == 1:
            os.remove(path)
        elif id == number_of_id:
            for x in range(0, 3):
                del lines[(id - 1) * 3 - 1]
        else:
            for x in range(0, 3):
                del lines[(id - 1) * 3]

        message = "✔ Password is successfully deleted.\nPress Enter to continue..."
        if os.path.exists(path):
            data = "\n".join(lines)
            encrypt_file(data, path, message, login_pw)
        else:
            file = open(path, 'w+')
            file.close()
            input(message)
        os.system('clear')
    else:
        return


def save_password_with_description(password, path):
    description = input("Please enter a description for the given password: ")
    now = datetime.datetime.now()
    date = str(now.year) + '.' + str(now.month) + '.' + str(now.day) + '.'
    description = date + description

    if not os.stat(path).st_size == 0:
        is_mac_valid, decrypted_data = decrypt_file(path)
        if is_mac_valid:
            data = decrypted_data + "\n\n" + password + "\n" + description
        else:
            return
    else:
        data = password + "\n" + description

    message = "✔ Password with description is successfully saved.\nPress Enter to continue..."
    encrypt_file(data, path, message, login_pw)
    os.system('clear')


def send_out_generated_password(email):
    if not re.match(".+@.+\..+", email):
        input("✖ Please give a valid e-mail address!\nPress Enter to continue...")
        os.system('clear')
    else:
        generated_pass = generate_random_strong_password()

        pbkdf_pass = pbkdf_gen(generated_pass)
        if email in open('database/users.txt').read().splitlines():
            with open('database/' + email + '/' + email + '.bin', 'wb') as fgen:
                fgen.write(pbkdf_pass)
            fgen.close()

        to = email
        name = to.split('@')[0].capitalize()
        robot_user = 'pwmanager007@gmail.com'
        robot_pwd = 'Crysys007'

        smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(robot_user, robot_pwd)

        msg = MIMEMultipart('multipart')
        msg['Subject'] = 'Password Manager new password'
        msg['From'] = robot_user
        msg['To'] = to

        part1 = MIMEText('Hi ' + name + ',\n\n'
        'We recieved a request to reset your Password Manager password.\n\n'
        'Your new password:', 'plain')
        part2 = MIMEText('<b>{0}</b>'.format(generated_pass), 'html')
        part3 = MIMEText('\nYou can change it after logged in.', 'plain')
        part4 = MIMEText('''<b>Didn't request this change?</b>''', 'html')
        part5 = MIMEText('''If you didn't request a new password, let your Help Desk know your computer was compromised.\n\n'''
        'Kind regards,\n'
        '       Password Manager Team', 'plain')

        msg.attach(part1)
        msg.attach(part2)
        msg.attach(part3)
        msg.attach(part4)
        msg.attach(part5)
        smtpserver.sendmail(robot_user, to, msg.as_string())
        smtpserver.close()

        input("E-mail is sent with the new password. Check your mailbox, maybe your spams too.\n"
              "Press Enter to continue...")
        os.system('clear')


loop = True
register = True
login = True
manage = True

os.system('clear')

while loop:

    while True:
        try:
            print_menu()
            choice = int(input("Enter your choice [1-4]: "))
            break
        except:
            os.system('clear')
            print("Wrong option selection. Please try again..")

    if choice == 1:
        while register:
            if not os.path.exists('database'):
                os.mkdir('database')
            if not os.path.exists('database/users.txt'):
                file = open('database/users.txt', 'w+')
                file.close()

            os.system('clear')
            print(29 * "-", "REGISTER", 28 * "-")

            email = input("Please enter your e-mail address: ")
            if email in open('database/users.txt').read().splitlines():
                input("✖ That e-mail is taken! Please try another one. Or did you forget your password?\n"
                      "Press Enter to continue...")
                os.system('clear')
                break

            if not re.match(".+@.+\..+", email):
                input("✖ Please register with an e-mail address!\nPress Enter to continue...")
                os.system('clear')
                break

            print("WARNING: In case of forgetting account password leads to lose all the data stored by the account!")
            print("A strong password is at least 8 characters long and contains letters, numbers and symbols.")
            pw1 = getpass.getpass("Please enter a strong password: ")

            if pw1 in email:
                input("✖ E-mail and password are (partly) the same. Please choose another password.\n"
                      "Press Enter to continue...")
                os.system('clear')
                break
            elif pw1 in open('weakPasswordDictionary.txt', encoding=enc).read():
                input("✖ Your password has been found in the weak password dictionary. Please choose another password."
                      "\nPress Enter to continue...")
                os.system('clear')
                break
            else:
                pw2 = getpass.getpass("Please re-enter your chosen password: ")

                if pw1 == pw2:
                    print("✔ Passwords are the same")

                    long = long_enough(pw1)
                    letter = contains_letter(pw1)
                    number = contains_number(pw1)
                    symbol = contains_symbol(pw1)

                    if long and letter and number and symbol:
                        print("✔✔✔ Good password ✔✔✔")

                        with open('database/users.txt', 'a') as file:
                            file.write(email + "\n")
                        file.close

                        emailfile = email + ".bin"

                        os.mkdir('database/' + email)
                        with open('database/' + email + '/' + emailfile, 'wb') as f:
                            f.write(pbkdf_gen(pw1))
                        f.close()

                        prev_pw_file = email + ".prev.txt"
                        with open('database/' + email + '/' + prev_pw_file, 'w') as f:
                            f.write(str(pbkdf_gen(pw1)))
                        f.close()

                        input("Press Enter to continue...")
                        os.system('clear')
                        break
                    else:
                        input("✖ ✖ ✖ Weak password. Please try again.\nPress Enter to continue...")
                        os.system('clear')
                        break

                else:
                    input("✖ Passwords do not match. Please try again.\nPress Enter to continue...")
                    os.system('clear')
                    break

    elif choice == 2:
        login = True
        while login:
            os.system('clear')
            print(30 * "-", "LOGIN", 30 * "-")

            if not os.path.exists('database/users.txt'):
                input("✖ You need to register first!\nPress Enter to continue...")
                os.system('clear')
                break

            login_email = input("Please enter your e-mail address: ")
            login_file = login_email + ".bin"

            login_pw = getpass.getpass("Please enter your password: ")
            hashedkey = pbkdf_gen(login_pw)

            if login_email in open('database/users.txt').read().splitlines():
                with open('database/' + login_email + '/' + login_file, 'rb') as fin:
                    storedkey = fin.read()
                fin.close()

                if storedkey == hashedkey:
                    password_file = login_email + ".pw.txt"
                    path = 'database/' + login_email + '/' + password_file
                    if not os.path.exists(path):
                        file = open(path, 'w+')
                        file.close()

                    os.system('clear')
                    manage = True
                    while manage:
                        while True:
                            try:
                                print_manage_menu()
                                manage_choice = int(input("Enter your choice [1-6]: "))
                                break
                            except:
                                os.system('clear')
                                print("Wrong option selection. Please try again..")

                        if manage_choice == 1:
                            os.system('clear')
                            print(26 * "-", "LIST PASSWORDS", 25 * "-")
                            print("")
                            print_password_table()
                            input("Press Enter to continue...")
                            os.system('clear')
                        elif manage_choice == 2:
                            os.system('clear')
                            while True:
                                try:
                                    print_add_password_menu()
                                    add_pw_choice = int(input("Enter your choice [1-3]: "))
                                    if add_pw_choice < 1 or add_pw_choice > 3:
                                        raise new_exc from original_exc
                                    break
                                except:
                                    os.system('clear')
                                    print("Wrong option selection. Please try again..")

                            if add_pw_choice == 1:
                                print("A strong password is at least 8 characters long and contains letters, numbers "
                                      "and symbols.")
                                pw1 = getpass.getpass("Please enter a strong password: ")

                                if pw1 in open('weakPasswordDictionary.txt', encoding=enc).read():
                                    input("✖ Your password has been found in the weak password dictionary. Please "
                                          "choose another password.\nPress Enter to continue...")
                                    os.system('clear')
                                else:
                                    pw2 = getpass.getpass("Please re-enter your chosen password: ")
                                    if pw1 == pw2:
                                        print("✔ Passwords are the same")

                                        long = long_enough(pw1)
                                        letter = contains_letter(pw1)
                                        number = contains_number(pw1)
                                        symbol = contains_symbol(pw1)

                                        if long and letter and number and symbol:
                                            print("✔✔✔ Good password ✔✔✔\n")
                                            save_password_with_description(pw1, path)
                                        else:
                                            input("✖ ✖ ✖ Weak password. Please try again.\nPress Enter to continue...")
                                            os.system('clear')
                                    else:
                                        input("✖ Passwords do not match. Please try again.\nPress Enter to continue...")
                                        os.system('clear')
                            elif add_pw_choice == 2:
                                generated_pass = generate_random_strong_password()
                                print("✔ Random strong password is generated.")
                                save_password_with_description(generated_pass, path)
                            elif add_pw_choice == 3:
                                os.system('clear')
                        elif manage_choice == 3:
                            os.system('clear')
                            print(18 * "-", "MODIFY PASSWORD OR DESCRIPTION", 17 * "-")
                            print('')
                            number_of_id = print_password_table()
                            try:
                                print("Type anything but valid Id to back!")
                                chosen_id = int(input("The Id of the row you want to modify: "))
                                if chosen_id < 1 or chosen_id > number_of_id:
                                    raise new_exc from original_exc
                            except:
                                input("✖ Invalid Id chosen. Please try again.\nPress Enter to continue...")
                                os.system('clear')
                                chosen_id = 0

                            if chosen_id != 0:
                                interrupt = False
                                password = ''
                                modify_password = input("Do you want to modify password (y/n)? ")
                                modify_password = modify_password.lower()
                                if modify_password == 'y':
                                    print("1. Give own password")
                                    print("2. Generate strong random password")
                                    try:
                                        choice = int(input("Enter your choice [1-2]: "))
                                        if choice < 1 or choice > 2:
                                            raise new_exc from original_exc
                                    except:
                                        input("✖ Invalid Id chosen. Please try again.\nPress Enter to continue...")
                                        os.system('clear')
                                        interrupt = True

                                    if choice == 1:
                                        print("A strong password is at least 8 characters long and contains letters, "
                                              "numbers and symbols.")
                                        password = getpass.getpass("Please enter a strong password: ")

                                        if password in open('weakPasswordDictionary.txt', encoding=enc).read():
                                            input("✖ Your password has been found in the weak password dictionary. "
                                                  "Please choose another password.\nPress Enter to continue...")
                                            os.system('clear')
                                            interrupt = True
                                        else:
                                            pw2 = getpass.getpass("Please re-enter your chosen password: ")
                                            if password == pw2:
                                                print("✔ Passwords are the same")

                                                long = long_enough(password)
                                                letter = contains_letter(password)
                                                number = contains_number(password)
                                                symbol = contains_symbol(password)

                                                if long and letter and number and symbol:
                                                    print("✔✔✔ Good password ✔✔✔\n")
                                                else:
                                                    input("✖ ✖ ✖ Weak password. Please try again.\nPress Enter to "
                                                        "continue...")
                                                    os.system('clear')
                                                    interrupt = True
                                            else:
                                                input("✖ Passwords do not match. Please try again.\nPress Enter to "
                                                    "continue...")
                                                os.system('clear')
                                                interrupt = True
                                    elif choice == 2:
                                        password = generate_random_strong_password()
                                        print("✔ Random strong password is generated.")

                                if not interrupt:
                                    description = ''
                                    modify_description = input("Do you want to modify description (y/n)? ")
                                    modify_description = modify_description.lower()
                                    if modify_description == 'y':
                                        description = input("Please enter a description for the chosen password: ")

                                    if modify_password == 'y' or modify_description == 'y':
                                        modify_password_or_description(chosen_id, modify_password, password,
                                                                       modify_description, description, path)
                                    os.system('clear')
                        elif manage_choice == 4:
                            os.system('clear')
                            print(25 * "-", "DELETE PASSWORD", 25 * "-")
                            print('')
                            number_of_id = print_password_table()
                            try:
                                print("Type anything but valid Id to back!")
                                chosen_id = int(input("The Id of the row you want to modify: "))
                                if chosen_id < 1 or chosen_id > number_of_id:
                                    raise new_exc from original_exc
                            except:
                                input("Invalid Id chosen. Please try again.\nPress Enter to continue...")
                                os.system('clear')
                            delete_password(chosen_id, number_of_id, path)
                        elif manage_choice == 5:
                            os.system('clear')
                            print(21 * "-", "CHANGE ACCOUNT PASSWORD", 21 * "-")
                            print('')
                            current_password = getpass.getpass("Please enter your current password: ")
                            hashedkey = pbkdf_gen(current_password)

                            with open('database/' + login_email + '/' + login_file, 'rb') as fin:
                                storedkey = fin.read()
                            fin.close()

                            if storedkey == hashedkey:
                                print("A strong password is at least 8 characters long and contains letters, numbers "
                                       "and symbols.")
                                pw1 = getpass.getpass("Please enter a strong password: ")

                                if pw1 in login_email:
                                    input("✖ E-mail and password are (partly) the same. Please choose another password."
                                          "\nPress Enter to continue...")
                                    os.system('clear')
                                elif pw1 in open('weakPasswordDictionary.txt', encoding=enc).read():
                                    input("✖ Your password has been found in the weak password dictionary. Please "
                                          "choose another password.\nPress Enter to continue...")
                                    os.system('clear')
                                else:
                                    pw2 = getpass.getpass("Please re-enter your chosen password: ")

                                    if pw1 == pw2:
                                        print("✔ Passwords are the same")

                                        long = long_enough(pw1)
                                        letter = contains_letter(pw1)
                                        number = contains_number(pw1)
                                        symbol = contains_symbol(pw1)

                                        if long and letter and number and symbol:
                                            print("✔✔✔ Good password ✔✔✔")

                                            file_in = open("database/" + login_email + "/" + login_email + ".prev.txt",
                                                           'r')
                                            pw_file_text = file_in.readlines()
                                            file_in.close()

                                            pbkdf_pw = pbkdf_gen(pw1)
                                            for x in range(0, len(pw_file_text)):
                                                pw_file_text[x] = pw_file_text[x].rstrip()
                                            if str(pbkdf_pw) not in pw_file_text:
                                                if len(pw_file_text) == 6:
                                                    pw_file_text.pop(0)

                                                pw_file_text.append(str(pbkdf_pw))
                                                pw_file_text = "\n".join(pw_file_text)

                                                prev_pw_file = login_email + ".prev.txt"
                                                with open('database/' + login_email + '/' + prev_pw_file, 'w') as f:
                                                    f.write(pw_file_text)
                                                f.close()

                                                if not os.stat(path).st_size == 0:
                                                    is_mac_valid, decrypted_data = decrypt_file(path)
                                                    if is_mac_valid:
                                                        message = "✔ Password file with new password is successfully " \
                                                                  "reencrypted.\nPress Enter to continue..."
                                                        encrypt_file(decrypted_data, path, message, pw1)
                                                else:
                                                    input("✔ Password is successfully changed.\n"
                                                          "Press Enter to continue...")

                                                login_pw = pw1

                                                with open('database/' + login_email + '/' + login_file, 'wb') as f:
                                                    f.write(pbkdf_pw)
                                                f.close()
                                                os.system('clear')
                                            else:
                                                input("✖ Recently used password. Please choose another one.\n"
                                                      "Press Enter to continue...")
                                                os.system('clear')
                                        else:
                                            input("✖ ✖ ✖ Weak password. Please try again.\nPress Enter to continue...")
                                            os.system('clear')
                                    else:
                                        input("✖ Passwords do not match. Please try again.\nPress Enter to continue...")
                                        os.system('clear')
                            else:
                                input("✖ Incorrect password. Please try again.\nPress Enter to continue...")
                                os.system('clear')
                        elif manage_choice == 6:
                            manage = False
                            login = False
                            os.system('clear')
                        else:
                            os.system('clear')
                            print("Wrong option selection. Please try again..")
                else:
                    input("✖ Incorrect e-mail or password. Please try again.\nPress Enter to continue...")
                    os.system('clear')
                    break
            else:
                input("✖ Incorrect e-mail or password. Please try again.\nPress Enter to continue...")
                os.system('clear')
                break

    elif choice == 3:
        os.system('clear')
        print(22 * "-", "FORGOT YOUR PASSWORD?", 22 * "-")

        if not os.path.exists('database/users.txt'):
            input("✖ You need to register first.\nPress Enter to continue...")
            os.system('clear')
        else:
            input("WARNING: Claiming for a new password leads to erase all the data stored by the account!\n"
                  "OK, I got it! Do it! Press Enter to continue...")
            forgot_email = input("Enter your e-mail address: ")
            send_out_generated_password(forgot_email)

    elif choice == 4:
        print("Quit has been selected")
        loop = False
    else:
        os.system('clear')
        print("Wrong option selection. Please try again..")