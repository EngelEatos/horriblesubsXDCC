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

class IrcClient():
    """irc-client"""
    def __init__(self, json_data, download_dir):
        """initalize ircclient"""
        self.json_data = json_data
        self.download_dir = download_dir
        self.sock = socket.socket()
        self.whois = dict()

    def send(self, msg):
        """send message"""
        print("%s\r\n" % msg)
        self.sock.send(bytes("%s\n" % msg, "UTF-8"))

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
        if anime == "Knight_s & Magic":
            anime = "Knight's & Magic"
            filename = filename.replace("Knight_s & Magic", anime)
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
        while True:
            data = self.sock.recv(2048).decode('utf-8')
            if not data:
                continue
            lines = data.split("\n")
            for line in lines:
                data_array = line.split(' ')
                print(data_array)
                #self.uprint(data_array)
                #print()
                if len(data_array) <= 1:
                    continue
                if data_array[0] == 'PING':
                    self.send("PONG %s\r\n" % data_array[1])
                elif data_array[1] == 'JOIN':
                    print("JOIN - %s" % get_user_name(data_array[0]))
                elif data_array[1] == 'QUIT':
                    print("QUIT - %s" % get_user_name(data_array[0]))
                callback_result = callback_function(data_array)
                if callback_result:
                    return callback_result

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
            size = int(line[length-1][:-2])
            filename = stringbuild(line, 5, length-3)
            print("%s %s %s %s" % (host, port, size, filename))
            self.accept_tcp(host, port, filename[1:-1], size)

def get_user_name(irc_line):
    """return username from irc-line"""
    return irc_line[1:irc_line.find('!')]

def stringbuild(line, start, end):
    """build string from list from start to end"""
    result = ""
    for i in range(start, end):
        result += line[i] + " "
    return result[:len(result)-1]

def sizeof_fmt(num, suffix='B'):
    """convert byte size to humanreadable size"""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

if __name__ == '__main__':
    _IRC_ = IrcClient("[]", "G:/summer")
    _IRC_.connect()
