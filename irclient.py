import sys
import socket
import string
import threading
import ipaddress
import json
import os
import queue
from tqdm import tqdm

HOST = "irc.rizon.net"
PORT = 6667
NICK = "testtest6"
IDENT = "testest6"
REALNAME = "testtest6"
SERVER = "rizon"
DOWNLOAD_DIR = "/home/chaos/tmp"

class IRCclient():
    def __init__(self, host, port, user, channel, json):
        self.host = host
        self.port = port
        self.user = user
        self.channel = channel
        self.sock = socket.socket()
        self.json = json

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

    def progress(s, count, total, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
        sys.stdout.flush()

    def acceptTCP(s, ip, port, filename, size):
        f = open(os.path.join(DOWNLOAD_DIR, filename), 'wb')
        print(os.path.join(DOWNLOAD_DIR, filename))
        tcp_socket = socket.socket()
        tcp_socket.connect( (ip, port) )
        #tcp_socket = socket.create_connection( (ip, port))
        print("SOCKET connected to %s:%s" % (ip, port) )
        current = 0
        with tqdm(total=size, unit='B', unit_scale=True) as pbar:
            while(current != size):
                #s.progress(current, size, filename)
                l = tcp_socket.recv(1024)
                current += len(l)
                pbar.update(len(l))
                #print(Receiving: " + s.sizeof_fmt(current) + "/" + s.sizeof_fmt(int(size)))
                f.write(l)
        f.close()
        print("DONE: " + filename)
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
            print(temp)
            for line in temp:
                line = line.rstrip()
                line = line.split()
                if(len(line) < 1):
                    return
                res = callback(line)
                if(res):
                    return res
                elif(line[0] == "PING"):
                    s.send("PONG %s\r\n" % line[1])
    def process(s):
        #Ginpachi-Sensei xdcc send #1123
        json_data = '{"Ginpachi-Sensei" : [4300,4528,3051,4059]}'
        #json_data = s.json
        bots = json.loads(json_data)
        for bot in bots:
            for package in bots[bot]:
                s.privmsg(bot, "xdcc send #" + str(package))
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
                    t = threading.Thread(target=s.acceptTCP, args=[ip, port, filename[1:-1], size])
                    t.start()

    def processCallback(s, line):
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

def main():
    irc = IRCclient("irc.rizon.net", 6667, "testtest13", "#horriblesubs", "")
    irc.connect()

def test():
    irc = IRCclient("irc.rizon.net", 6667, "testtest13", "#horriblesubs")
    irc.process()

if __name__ == '__main__':
    main()
