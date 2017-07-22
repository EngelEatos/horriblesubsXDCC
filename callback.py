"""all acllback functions for receive-function in one file"""
import sys
import config

def login_callback(line):
    """callback-function for login"""
    if line[1] == "004":
        print("logged in")
        return True
    elif line[1] == "433":
        print("nick already in use")
        sys.exit(1)

def join_callback(line):
    """callback-function for join"""
    if len(line) > 1:
        return line[1] == "332"

def botname_callback(line):
    """callback-function for getBotName"""
    if line[1] == "311" and line[2] == config.USER:
        return line[4] + "@" + line[5]

def process_callback(line):
    """callback-function for process"""
    if len(line) >= 4:
        if line[1] == "PRIVMSG" and "DCC" in line[3]:
            return line
