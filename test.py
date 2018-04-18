# Password manager in Python

from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
import smtplib
import random
import hashlib
import os
import getpass

# Menu design
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
    print("3. Modify passwords")
    print("4. Delete password")
    print("5. Change account password")
    print("6. Log out")
    print("TODO: MANAGER FUNCTIONS")
    print(67 * "-")


def pbkdf_gen(password):
    random = Random.new()
    salt = hashlib.sha256().digest()
    keysize = 256
    keys = PBKDF2(password, salt, count=20000, dkLen = keysize * 2)  # 2x256 bit keys
    return keys


def sendOutGeneratedPassword(email):
    # Generate random strong password
    dic = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ.,;:?!-_{}@&#<>[]ß×÷|\~^"
    length = 32
    generatedPass = "".join(random.sample(dic, length))
    print(generatedPass)

    # Register new password to the correct file
    with open(email+".bin", 'wb') as fgen:
        fgen.write(pbkdf_gen(generatedPass))
    fgen.close()

    # Send out mail
    print("TODO: Your generated password has been sent out")


# Ezt kell elküldeni emailben -> SMTP library
# pbkdf_gen("LehelJelszoAsd")

loop = True
register = True
login = True
manage = True

os.system('clear')

while loop:  # While loop which will keep going until loop = False

    while True:
        try:
            print_menu()  # Displays menu
            choice = int(input("Enter your choice [1-4]: "))
            break
        except:
            os.system('clear')
            print("Wrong option selection. Please try again..")

    if choice == 1:
        while register:
            print(29 * "-", "REGISTER", 28 * "-")
            email = input("Please enter your e-mail address: ")

            if not os.path.exists('database'):
                os.mkdir('database')
            if not os.path.exists('database/users.txt'):
                file = open('database/users.txt', 'w+')
                file.close()

            if email in open('database/users.txt').read().splitlines():
                input("✖ Email already exists! Please select another one. Or did you forget your password?\n"
                      "Press Enter to continue...")
                os.system('clear')
                break

            # print("The chosen e-mail is: ", email)
            print("A strong password is at least 8 characters long and contains letters, numbers and symbols.")
            pw1 = input("Please enter a strong password: ")  # TODO: getpass.getpass()

            enc = 'iso-8859-15'
            # Same as email?
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
                pw2 = input("Please re-enter your chosen password: ")  # TODO: getpass.getpass()
                # pw1 = getpass.getpass('Please enter a strong password: ')
                # pw2 = getpass.getpass('Please re-enter your chosen password: ')

                if pw1 == pw2:
                    print("✔ Passwords are the same")

                    # Long enough?
                    if len(pw1) > 7:
                        print("✔ Password is long enough")
                        long = True
                    else:
                        print("✖ Password is less than 8 characters")
                        long = False

                    # Are there letters in the password?
                    if any(char.isalpha() for char in pw1):
                        print("✔ Password contains letter")
                        letter = True
                    else:
                        print("✖ Password does not contain letter")
                        letter = False

                    # Are there numbers in the password?
                    if any(char.isdigit() for char in pw1):
                        print("✔ Password contains number")
                        number = True
                    else:
                        print("✖ Password does not contain number")
                        number = False

                    # Are there symbols in the password?
                    symbols = set('.,;:?!-_{}@&#<>[]ß×÷|\~^')
                    if any((c in symbols) for c in pw1):
                        print("✔ Password contains symbol")
                        symbol = True
                    else:
                        print("✖ Password does not contain symbol")
                        symbol = False

                    if long and letter and number and symbol:
                        print("✔✔✔ Good password ✔✔✔")

                        # Add new e-mail to users.txt
                        with open('database/users.txt', 'a') as file:
                            file.write(email + "\n")
                        file.close

                        # Create new file with PBKDF2 key for user
                        emailfile = email + ".bin"

                        os.mkdir('database/' + email)
                        with open('database/' + email + '/' + emailfile, 'wb') as f:
                            f.write(pbkdf_gen(pw1))
                        f.close()

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
        while login:
            print(30 * "-", "LOGIN", 30 * "-")

            if not os.path.exists('database/users.txt'):
                input("✖ You need to register first!\nPress Enter to continue...")
                os.system('clear')
                break

            login_email = input("Please enter your e-mail address: ")
            login_file = login_email + ".bin"

            login_pw = input("Please enter your password: ")  # TODO: getpass.getpass()
            hashedkey = pbkdf_gen(login_pw)
            # print(hashedkey)

            if login_email in open('database/users.txt').read().splitlines():
                with open('database/' + login_email + '/' + login_file, 'rb') as fin:
                    storedkey = fin.read()
                # print(storedkey)

                if storedkey == hashedkey:
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
                            print("LIST PASSWORDS")
                            # TODO
                        elif manage_choice == 2:
                            print("ADD NEW PASSWORD")
                            # TODO
                        elif manage_choice == 3:
                            print("MODIFY PASSWORDS")
                            # TODO
                        elif manage_choice == 4:
                            print("DELETE PASSWORDS")
                            # TODO
                        elif manage_choice == 5:
                            print("CHANGE ACCOUNT PASSWORD")
                            # TODO
                        elif manage_choice == 6:
                            manage = False
                            # TODO
                        else:
                            os.system('clear')
                            print("Wrong option selection. Please try again..")

                    # break  # just temporarily
                else:
                    input("✖ Incorrect e-mail or password. Please try again.\nPress Enter to continue...")
                    os.system('clear')
                    break
            else:
                input("✖ Incorrect e-mail or password. Please try again.\nPress Enter to continue...")
                os.system('clear')
                break

    elif choice == 3:
        print(22 * "-", "FORGOT YOUR PASSWORD?", 22 * "-")

        if not os.path.exists('database/users.txt'):
            input("✖ You need to register first.\nPress Enter to continue...")
            os.system('clear')
        else:
            forgot_email = input("Enter your e-mail address: ")
            if forgot_email in open('database/users.txt').read().splitlines():
                print("✔ E-mail found in users")
                sendOutGeneratedPassword(forgot_email)
                os.system('clear')
            else:
                input("✖ E-mail is invalid. Please try again.\nPress Enter to continue...")
                os.system('clear')

    elif choice == 4:
        print("Quit has been selected")
        # You can add your code or functions here
        loop = False  # This will make the while loop to end as not value of loop is set to False
    else:
        # Any integer inputs other than values 1-5 we print an error message
        os.system('clear')
        print("Wrong option selection. Please try again..")