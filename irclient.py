"""simple ircclient to download anime packages"""
import sys
import socket
import os
import json
import ipaddress
from tqdm import tqdm
import xdccparser
import config
import callback

HOST = config.HOST
PORT = config.PORT
USER = config.USER
CHANNEL = config.CHANNEL

class irc_client():
    """irc-client"""
    def __init__(self, json_data, download_dir):
        """initalize ircclient"""
        self.json_data = json_data
        self.download_dir = download_dir
        self.sock = socket.socket()
        self.whois = dict()

    def send(self, msg):
        """send message"""
        print(msg+"\r\n")
        self.sock.send((msg+"\r\n").encode())

    def privmsg(self, target, msg):
        """send private message"""
        self.send("PRIVMSG " + target + " :" + msg)

    def connect(self):
        """connect to HOST, PORT"""
        self.sock.connect((HOST, PORT))
        #login
        server = HOST[HOST.find('.')+1:HOST.rfind('.')]
        self.send("NICK %s" % USER)
        self.send("USER %s %s %s %s" % (USER, HOST, server, USER))
        if self.receive(callback.login_callback):
            self.join()

    def join(self):
        """join channel on server"""
        print("trying to join channel: " + CHANNEL)
        self.send("JOIN " + CHANNEL)
        if self.receive(callback.join_callback):
            print("Join successfull - channel: " + CHANNEL)
            self.process()
        else:
            print("Join failed")
            sys.exit(1)

    def accept_tcp(self, host, port, filename, size):
        """accept incoming tcp offer"""
        anime = xdccparser.parse_name(filename)[1]
        episode_file = open(os.path.join(self.download_dir, anime, filename), 'wb')
        print(os.path.join(self.download_dir, anime, filename))
        tcp_socket = socket.socket()
        tcp_socket.connect((host, port))
        print("SOCKET connected to %s:%s" % (host, port))
        current = 0
        with tqdm(total=size, unit='B', unit_scale=True) as pbar:
            while current != size:
                received = tcp_socket.recv(1024)
                current += len(received)
                pbar.update(len(received))
                #print(Receiving: " + self.sizeof_fmt(current) + "/" + self.sizeof_fmt(int(size)))
                episode_file.write(received)
        episode_file.close()
        print("DONE: " + filename)
        tcp_socket.close()

    def get_botname(self, bot):
        """get botname"""
        if bot not in self.whois:
            self.send("WHOIS " + bot)
            self.whois[bot] = self.receive(callback.botname_callback)
        return self.whois[bot]

    def receive(self, callback_function):
        """receive line from irc-server"""
        readbuffer = ""
        while True:
            readbuffer = readbuffer + self.sock.recv(1024).decode("utf-8")
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()
            for line in temp:
                line = line.rstrip()
                line = line.split()
                if len(line) < 1:
                    return
                res = callback_function(line)
                if res:
                    return res
                elif line[0] == "PING":
                    self.send("PONG %s\r\n" % line[1])

    def process(self):
        """proccess json and start download sequential"""
        bots = json.loads(self.json_data)
        for bot in bots:
            for package in bots[bot]:
                self.download_files([bot, str(package)])

    def download_files(self, task):
        """download files by package number"""
        bot = task[0]
        package = task[1]
        self.privmsg(bot, "xdcc send #" + package)
        line = self.receive(callback.process_callback)
        print(line)
        offerer = line[0][line[0].find('!')+1:]
        botname = self.get_botname(bot)
        if offerer == botname:
            length = len(line)
            host = str(ipaddress.ip_address(int(line[length-3])))
            port = int(line[length-2])
            size = int(line[length-1][:-1])
            filename = self.stringbuild(line, 5, length-3)
            print("%s %s %s %s" % (host, port, size, filename))
            self.accept_tcp(host, port, filename[1:-1], size)

    def stringbuild(self, line, start, end):
        """build string from list from start to end"""
        result = ""
        for i in range(start, end):
            result += line[i] + " "
        return result[:len(result)-1]

    def sizeof_fmt(self, num, suffix='B'):
        """convert byte size to humanreadable size"""
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
