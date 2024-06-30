from termcolor import colored
from colorama import just_fix_windows_console

# This fixes issues with colored text on windows consoles
just_fix_windows_console()


# Colored text lambda functions
def print_blue(x: str):
    print(colored(x, "cyan"))

def print_green(x: str):
    print(colored(x, "green"))

def print_red(x: str):
    print(colored(x, "red"))

def print_purple(x: str):
    print(colored(x, "magenta"))
