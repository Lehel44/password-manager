# Password manager in Python

from Crypto.Protocol.KDF import PBKDF2
import Crypto.Random
import hashlib

# Menu design
def print_menu():
    print(30 * "-", "MENU", 30 * "-")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    print(67 * "-")


def pbkdf_gen(password):
    random = Crypto.Random.new()
    salt = hashlib.sha256().digest()
    keysize = 256
    keys = PBKDF2(password, salt, count=20000, dkLen = keysize * 2)  # 2x256 bit keys

## Ezt kell elküldeni emailben -> SMTP library
#pbkdf_gen("LehelJelszoAsd")

loop = True

while loop:  # While loop which will keep going until loop = False
    print_menu()  # Displays menu
    choice = eval(input("Enter your choice [1-5]: "))

    if choice == 1:
        print("Login has been selected")
        ## You can add your code or functions here
    elif choice == 2:
        print("Register has been selected")
        ## You can add your code or functions here
    elif choice == 3:
        print("Exit has been selected")
        ## You can add your code or functions here
        loop = False  # This will make the while loop to end as not value of loop is set to False
    else:
        # Any integer inputs other than values 1-5 we print an error message
        input("Wrong option selection. Enter any key to try again..")