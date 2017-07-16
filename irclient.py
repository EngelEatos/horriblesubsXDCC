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

class IRCclient():
    def __init__(self, host, port, user, channel):
        self.host = host
        self.port = port
        self.user = user
        self.channel = channel
        self.sock = socket.socket()

    def send(s, msg):
        s.sock.send((msg+"\r\n").encode())

    def privmsg(s, target, msg):
        send("PRIVMSG " + target + " :" + msg)

    def connect(s):
        s.sock.connect( (s.host, s.port) )
        s.login()
        #t = threading.Thread(target=s.recv)
        #t.start()

    def login(s):
        s.send("NICK %s" % s.user)
        s.send("USER %s %s %s %s" % (s.user, s.host, s.host[s.host.find('.')+1:s.host.rfind('.')], s.user))
        while True:

            elif(line[0] == "PING"):
                s.send("PONG %s\r\n" % line[1])
    def loginCallback(s, line):
        if(line[1] == "004"):
            print("logged in")
            s.join()
        elif(line[1] == "433"):
            print("nick already in use")
            sys.exit(1)
    def join(s):
        print("Joining channel: " + s.channel)
        s.send("JOIN " + s.channel)
        while True:


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

    def getBotname(s):
        s.send("WHOIS Ginpachi-Sensei")
        recvCon(s.botNameResult)

    def botNameResult(s, line):
        if(line[1] == "311" and line[2] == s.user):
            return line[4] + line[5]

    def recvCon(s, callback):
        readbuffer = ""
        while True:
            readbuffer = readbuffer + s.sock.recv(1024).decode("utf-8")
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()
            for line in temp:
                line = line.rstrip()
                line = line.split()
                res = callback(line)
                if(res):
                    return res
                elif(line[0] == "PING"):
                    s.send("PONG %s\r\n" % line[1])
    def recv(s):
        readbuffer = ""
        bot = ""
        while 1:
            readbuffer = readbuffer + s.sock.recv(1024).decode("utf-8")
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()
            for line in temp:
                line = line.rstrip()
                line = line.split()
                if(line[1] == "004"):
                    print("logged in")
                    s.join()
                elif(line[1] == "433"):
                    print("nick already in use")
                    sys.exit(1)
                elif(line[0] == "PING"):
                    s.send("PONG %s\r\n" % line[1])
                elif(line[1] == "332"):
                    print("Join successfull - channel: " + line[3])
                    s.send("WHOIS Ginpachi-Sensei")
                elif(line[1] == "311" and line[2] == s.user):
                    bot = line[4] + line[5]
                elif(line[1] == "NOTICE" and "News" not in line):
                        print(line[1] + " - " + line[0] + ": " + s.stringbuild(line, 4, len(line)) )
                elif(line[1] == "366"):
                    #print("sending PRIVMSG")
                    #send("PRIVMSG Ginpachi-Sensei :xdcc send #1123\r\n")
                    print('', end='', flush=True)
                elif(line[1] == "PRIVMSG" and "DCC" in line[3]):
                    check = line[0][line[0].find('!')+1:]
                    if bot and bot == check:
                        length = len(line)
                        ip = str(ipaddress.ip_address(int(line[length-3])))
                        port = int(line[length-2])
                        size = int(line[length-1][:-1])
                        filename = s.stringbuild(line, 5, length-3)
                        print("%s %s %s %s" % (ip, port, size, filename))
                        f = open(filename[1:-1], 'wb')
                        t = threading.Thread(target=s.acceptTCP, args=[ip, port, filename[1:-1], size])
                        t.start()
                else:
                    try:
                        print(line)
                    except UnicodeEncodeError as e:
                        [print(l) for l in line]
    def stringbuild(line, start, end):
        result = ""
        for i in range(start, end):
            result += line[i] + " "
        return result[:len(result)-1]

    def sizeof_fmt(num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

irc = IRCclient("irc.rizon.net", 6667, "testbot12", "#horriblesubs")
irc.connect()
