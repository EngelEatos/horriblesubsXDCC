import sys
import socket
import string
import threading
import ipaddress
import json
import os

HOST = "irc.rizon.net"
PORT = 6667
NICK = "testtes6"
IDENT = "testes6"
REALNAME = "testtes6"
SERVER = "rizon"
DOWNLOAD_DIR = "/home/chaos/tmp"

class IRCclient():
    def __init__(self, host, port, user, channel):
        self.host = host
        self.port = port
        self.user = user
        self.channel = channel
        self.sock = socket.socket()

    def send(s, msg):
        print(msg+"\r\n")
        s.sock.send((msg+"\r\n").encode())

    def privmsg(s, target, msg):
        s.send("PRIVMSG " + target + " :" + msg)

    def connect(s):
        s.sock.connect( (s.host, s.port) )
        s.login()
        #t = threading.Thread(target=s.recv)
        #t.start()

    def login(s):
        s.send("NICK %s" % s.user)
        s.send("USER %s %s %s %s" % (s.user, s.host, s.host[s.host.find('.')+1:s.host.rfind('.')], s.user))
        if(s.recvCon(s.loginCallback)):
            s.join()

    def loginCallback(s, line):
        if(line[1] == "004"):
            print("logged in")
            return True
        elif(line[1] == "433"):
            print("nick already in use")
            sys.exit(1)

    def join(s):
        print("trying to join channel: " + s.channel)
        s.send("JOIN " + s.channel)
        if(s.recvCon(s.joinCallback)):
            print("Join successfull - channel: " + s.channel)
            s.process()
        else:
            print("Join failed")
            sys.exit(1)

    def joinCallback(s, line):
        if(len(line) > 1):
            return (line[1] == "332")

    def acceptTCP(s,id, ip, port, filename, size):
        f = open(os.path.join(DOWNLOAD_DIR, filename), 'wb')
        tcp_socket = socket.socket()
        tcp_socket.connect( (ip, port) )
        print("tid: " + str(id) + " - SOCKET connected to %s:%s" % (ip, port) )
        current = 0
        while(current != size):
            l = tcp_socket.recv(1024)
            current += len(l)
            print("tid: " + str(id) + " - Receiving: " + s.sizeof_fmt(current) + "/" + s.sizeof_fmt(int(size)))
            f.write(l)
        f.close()
        print("tid: " + str(id) + " - DONE")
        tcp_socket.close()

    def getBotname(s):
        s.send("WHOIS Ginpachi-Sensei")
        return s.recvCon(s.botNameResult)

    def botNameResult(s, line):
        if(line[1] == "311" and line[2] == s.user):
            return line[4] + "@" + line[5]

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
    def process(s):
        #Ginpachi-Sensei xdcc send #1123
        #request
        #json = '{"todo":[{"botname" : "CR-RALEIGH|NEW","package": 5,"folder": "/home/chaos/output/"},{"botname" : "CR-RALEIGH|NEW","package": 160,"folder": "/home/chaos/output/test/"}]}';
        json_data = '{"Ginpachi-Sensei" : [1123,80], "CR-RALEIGH|NEW" : [5]}'
        j = json.loads(json_data)
        for botname in j:
            packages = j[botname]
            for i in range(len(packages)):
                s.privmsg(botname, "xdcc send #" + str(packages[i]))
                line = s.recvCon(s.processCallback)
                print(line)
                offerer = line[0][line[0].find('!')+1:]
                botname = s.getBotname()
                if(offerer == botname):
                    length = len(line)
                    ip = str(ipaddress.ip_address(int(line[length-3])))
                    port = int(line[length-2])
                    size = int(line[length-1][:-1])
                    filename = s.stringbuild(line, 5, length-3)
                    print("%s %s %s %s" % (ip, port, size, filename))
                    f = open(filename[1:-1], 'wb')
                    t = threading.Thread(target=s.acceptTCP, args=[i, ip, port, filename[1:-1], size])
                    t.start()

    def processCallback(s, line):
        print(line)
        if(len(line) >= 4):
            if(line[1] == "PRIVMSG" and "DCC" in line[3]):
                return line


    def stringbuild(s, line, start, end):
        result = ""
        for i in range(start, end):
            result += line[i] + " "
        return result[:len(result)-1]

    def sizeof_fmt(s, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

irc = IRCclient("irc.rizon.net", 6667, "testbot13", "#horriblesubs")
irc.connect()
