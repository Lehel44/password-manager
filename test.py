# Password manager in Python

from Crypto.Protocol.KDF import PBKDF2
import Crypto.Random
import hashlib
import os
import getpass

# Menu design
def print_menu():
    print(30 * "-", "MENU", 30 * "-")
    print("1. Register")
    print("2. Login")
    print("3. Forgot your password?")
    print("4. Quit")
    print(67 * "-")


def pbkdf_gen(password):
    random = Crypto.Random.new()
    salt = hashlib.sha256().digest()
    keysize = 256
    keys = PBKDF2(password, salt, count=20000, dkLen = keysize * 2)  # 2x256 bit keys
    return keys

# Ezt kell elküldeni emailben -> SMTP library
# pbkdf_gen("LehelJelszoAsd")

loop = True
register = True
login = True

while loop:  # While loop which will keep going until loop = False
    print_menu()  # Displays menu
    choice = eval(input("Enter your choice [1-4]: "))

    if choice == 1:
        while register:
            print(29 * "-", "REGISTER", 28 * "-")
            email = input("Please enter your e-mail address: ")

            if not os.path.exists('users.txt'):
                file = open('users.txt', 'w+')
                file.close()
            if email in open('users.txt').read():
                print("Email already exist! Please select another one. Or did you forget your password?")
                break

            # print("The chosen e-mail is: ", email)
            print("A strong password is at least 8 characters long and contains letters, numbers and symbols")
            pw1 = input("Please enter a strong password: ")

            # Same as email?
            if pw1 in email:
                print("E-mail and password are (party) the same. Please chose another password")
            elif pw1 in open('weakPasswordDictionary.txt').read():
                print("Your password has been found in the weak password dictionary. Please chose another password")
            else:
                pw2 = input("Please re-enter your chosen password: ")
                # pw1 = getpass.getpass('Please enter a strong password: ')
                # pw2 = getpass.getpass('Please re-enter your chosen password: ')

                if pw1 == pw2:
                    print("Passwords are the same")

                    # Long enough?
                    if len(pw1) > 7:
                        print("Password is long enough")
                        long = True
                    else:
                        print("Password is not long enough")
                        long = False

                    # Are there letters in the password?
                    if any(char.isalpha() for char in pw1):
                        print("Password contains letter")
                        letter = True
                    else:
                        print("Password does not contain letter")
                        letter = False

                    # Are there numbers in the password?
                    if any(char.isdigit() for char in pw1):
                        print("Password contains number")
                        number = True
                    else:
                        print("Password does not contain number")
                        number = False

                    # Are there symbols in the password?
                    symbols = set('.,;:?!-_{}@&#<>[]$ß×÷€|\~^đĐŁł')
                    if any((c in symbols) for c in pw1):
                        print('Password contains symbol')
                        symbol = True
                    else:
                        print('Password does not contain symbol')
                        symbol = True
                else:
                    print("Passwords are different, please try again")

                if long and letter and number and symbol:
                    print("Good password")
                    register = False

                    # Add new e-mail to users.txt
                    with open('users.txt', 'a') as file:
                        file.write(email+"\n")
                    file.close

                    # Create new file with PBKDF2 key for user
                    emailfile = email + ".bin"

                    with open(emailfile, 'wb') as f:
                        f.write(pbkdf_gen(pw1))
                    f.close()
                else:
                    print("Bad password. Please try again.")

    elif choice == 2:
        while login:
            print(30 * "-", "LOGIN", 30 * "-")

            if not os.path.exists('users.txt'):
                print("You need to register first!")
                break

            login_email = input("Please enter your e-mail address: ")
            if login_email in open('users.txt').read():
                print("E-mail found in users")
                login_file = login_email + ".bin"

            login_pw = input("Please enter your password: ")
            hashedkey = pbkdf_gen(login_pw)
            # print(hashedkey)

            with open(login_file, 'rb') as fin:
                storedkey = fin.read()
            # print(storedkey)

            if storedkey == hashedkey:
                print("Logged in successfully!")
                print("TODO: MANAGER FUNCTIONS")
                break  # just temporarily
            else:
                print("Incorrect e-mail or password. Please try again.")

    elif choice == 3:
        print("Forgot your password? has been selected")
        # You can add your code or functions here
    elif choice == 4:
        print("Quit has been selected")
        # You can add your code or functions here
        loop = False  # This will make the while loop to end as not value of loop is set to False
    else:
        # Any integer inputs other than values 1-5 we print an error message
        input("Wrong option selection. Enter any key to try again..")