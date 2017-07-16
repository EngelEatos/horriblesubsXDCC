import sys
import socket
import string
import threading
import ipaddress

HOST = "irc.rizon.net"
PORT = 6667
NICK = "testtes6"
IDENT = "testes6"
REALNAME = "testtes6"
SERVER = "rizon"

s = socket.socket( )

def send(msg):
    s.send(msg.encode())

def login():
    send("NICK %s\r\n" % NICK)
    send("USER %s %s %s %s\r\n" % (IDENT, HOST, SERVER, REALNAME))
    #
    #
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def privmsg(target, msg):
    send("PRIVMSG " + target + " " + msg + "\r\n")
def join():
    print("Joining channel: #horriblesubs")
    send("JOIN #horriblesubs\r\n")

def stringbuild(line, start, end):
    result = ""
    for i in range(start, end):
        result += line[i] + " "
    return result[:len(result)-1]

def acceptTCP(ip, port, filename, size):
    f = open(filename, 'wb')
    tcp_socket = socket.socket()
    tcp_socket.connect( (ip, port) )
    print("SOCKET connected to %s:%s" % (ip, port) )
    current = 0
    while(current != size):
        l = tcp_socket.recv(1024)
        current += len(l)
        print("Receiving: " + sizeof_fmt(current) + "/" + sizeof_fmt(int(size)))
        f.write(l)
    f.close()
    print("DONE")
    tcp_socket.close()

def recv():
    ignore = ["JOIN", "QUIT", "MODE", "001", "002", "003", "005", "251", "252", "253", "254", "255", "265", "266", "333", "353", "366", "372", "375", "376"]
    readbuffer = ""
    while 1:
        readbuffer = readbuffer + s.recv(1024).decode("utf-8")
        temp = readbuffer.split("\n")
        readbuffer = temp.pop()
        for line in temp:
            line = line.rstrip()
            line = line.split()
            if(line[1] == "004"):
                print("logged in")
                join()
            elif(line[1] == "433"):
                print("nick already in use")
                sys.exit(1)
            #elif(line[1] in ignore):
                #user-list
                #print('', end='', flush=True)
            elif(line[0] == "PING"):
                send("PONG %s\r\n" % line[1])
            elif(line[1] == "332"):
                print("Join successfull - channel: " + line[3])

            elif(line[1] == "NOTICE"):
                if(len(line) >= 4 and "News" not in line[3]):
                    print('', end='', flush=True)
                else:
                    print(line[1] + " - " + line[0] + ": " + stringbuild(line, 4, len(line)) )
            elif(line[1] == "366"):
                print("sending PRIVMSG")
                send("PRIVMSG Ginpachi-Sensei :xdcc send #1123\r\n")
            elif(line[1] == "PRIVMSG" and "DCC" in line[3]):
                length = len(line)
                ip = str(ipaddress.ip_address(int(line[length-3])))
                port = int(line[length-2])
                size = int(line[length-1][:-1])
                filename = stringbuild(line, 5, length-3)
                print("%s %s %s %s" % (ip, port, size, filename))
                f = open(filename[1:-1], 'wb')
                t = threading.Thread(target=acceptTCP, args=[ip, port, filename[1:-1], size])
                t.start()
            else:
                try:
                    print(line)
                except UnicodeEncodeError as e:
                    [print(l) for l in line]

s.connect((HOST, PORT))
login()
t = threading.Thread(target=recv)
t.start()
