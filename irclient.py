import sys
import socket
import string

HOST = "irc.rizon.net"
PORT = 6667
NICK = "testtest2"
IDENT = "testest2"
REALNAME = "testtest2"
SERVER = "rizon"
readbuffer = ""
s = socket.socket( )

def send(s, msg):
    s.send(msg.encode())

s.connect((HOST, PORT))
send(s, "NICK %s\r\n" % NICK)
send(s, "USER %s %s %s %s\r\n" % (IDENT, HOST, SERVER, REALNAME))
send(s, "JOIN #horriblesubs\r\n")
send(s, "/msg CR-RALEIGH|NEW xdcc send #5\r\n")
while 1:
    readbuffer = readbuffer + s.recv(1024).decode("utf-8")
    temp = readbuffer.split("\n")
    readbuffer = temp.pop( )

    for line in temp:
        line = line.rstrip()
        line = line.split()
        print(line)
        if(line[0] == "PING"):
            send(s, "PONG %s\r\n" % line[1])
