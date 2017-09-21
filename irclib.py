"""simple ircclient to download anime packages"""
import ipaddress
import json
import logging
import os
import re
import socket
import sys
import threading

from pyee import EventEmitter
from tqdm import tqdm

from tcpdownloader import TcpDownloader
from xdccparser import parse_name

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class IrcLib():
    """IrcLib"""
    ee = EventEmitter()

    def __init__(self, host, port, user, channel, download_dir, json_data):
        self.socket = socket.socket()
        self.host = host
        self.port = port
        self.user = user
        self.channel = channel
        self.download_dir = download_dir
        self.json_data = json_data
        self.downloader = TcpDownloader(4)
        self.downloader.start()
        self.offerer = []
        self.joined = False
        self.whois = dict()

    def send_raw(self, msg):
        """send raw message"""
        print("< %s\n" % msg)
        self.socket.sendall(bytes("%s\n" % msg, "UTF-8"))

    def privmsg(self, target, msg):
        """send private message"""
        self.send_raw("PRIVMSG %s :%s" % (target, msg))

    def request_xdcc(self, bot, package):
        """request xdcc package"""
        self.privmsg(bot, "xdcc send #" + package)

    def get_xdcc_info(self, bot, number):
        """get info of a xdcc package"""
        self.privmsg(bot, "xdcc info " + number)

    def get_bot_info(self, bot):
        """get bot whois"""
        if bot not in self.whois:
            self.send_raw("WHOIS " + bot)

    def connect(self):
        """"connect to host, port"""
        host = self.host
        user = self.user
        self.socket.connect((host, self.port))
        server = host[host.find('.') + 1:host.rfind('.')]
        self.send_raw("NICK %s" % user)
        self.send_raw("USER %s %s %s %s" % (user, host, server, user))
        #th = threading.Thread(target=self.receive)
        #th.daemon = True
        # th.start()
        self.receive()

    def quit(self):
        """send quit and exit"""
        self.send_raw("QUIT I'm outty")
        self.socket.close()
        sys.exit(0)

    @ee.on('irclib.ping.received')
    def pong(self, ping):
        """send pong"""
        self.send_raw("PONG %s" % ping)

    def join(self):
        """join channel"""
        logging.debug("send_join")
        self.send_raw("JOIN %s" % self.channel)

    @ee.on('irclib.ctcp')
    def on_ctcp(self, match):
        """on incoming ctcp request"""
        logging.debug("on_ctcp")
        #bot = msg_matches[1][msg_matches[1].find('!') + 1:]
        filename = match[1][1:-1] if '"' in match[1] else match[1]
        host = str(ipaddress.ip_address(int(match[2])))
        download_path = os.path.join(
            self.download_dir, parse_name(filename)[1], filename)
        print("%s %s %s %s" % (host, match[3], filename, match[4]))
        print(download_path)
        self.downloader.add_download(
            host, int(match[3]), int(match[4]), download_path)

    @ee.on('irclib.message.received')
    def on_message_received(self, msg, matches):
        """event on incoming private message"""
        dcc_pattern = r'^.+?DCC\sSEND\s(.*?)\s(\d+)\s(\d+)\s(\d+).+?$'
        match = re.match(dcc_pattern, matches[3])
        if match and len(match.groups()) >= 4:
            self.ee.emit('irclib.ctcp', self, match)
        else:
            print(msg)

    @ee.on('irclib.logged.in')
    def on_logged_in(self):
        """event on successfull login"""
        print("logged in as %s" % self.user)

    @ee.on('irclib.error')
    def on_error(self, msg):
        """event on error emit"""
        print("ERROR - %s" % msg)

    @ee.on('irclib.join.successfull')
    def on_successfull_join(self):
        """event on successfull join"""
        logging.debug("join sucessfull")
        self.start_requesting()

    @ee.on('irclib.motd.end')
    def on_motd_end(self):
        """event on incoming motd message"""
        logging.debug("on_motd_end")
        self.join()

    @ee.on('irclib.data')
    def on_data(self, line):
        """event on incoming unkown data"""
        logging.debug(line)

    @ee.on('irclib.bot.info')
    def on_bot_info(self, matches):
        """event on incoming bot info"""
        logging.debug(matches.groups())
        msg = matches[3]
        self.offerer.append(
            msg[msg.find('~'):msg.rfind(' ')].replace(' ', '@'))

    @ee.on('irclib.nick.error')
    def on_nick_already_in_use(self):
        """event on nick_error message"""
        self.ee.emit('irclib.error', "nick already in use")
        self.quit()

    @ee.on('irclib.reply')
    def on_reply(self, matches):
        """switch-case for incoming messages"""
        case = int(matches[2])
        if str(case) == "004":
            logging.debug("reply-logged")
            self.ee.emit('irclib.logged.in', self)
        elif case == 311:
            logging.debug("reply-bot-info-received")
            self.ee.emit('irclib.bot.info', self, matches)
        elif case == 332:
            logging.debug("reply-join")
            self.ee.emit('irclib.join.successfull', self)
        elif case == 376:
            logging.debug("reply-motd")
            self.ee.emit('irclib.motd.end', self)
        elif case == 443:
            logging.debug("reply-nick")
            self.ee.emit('irclib.nick.error', self)
        else:
            logging.debug(matches.groups())

    @ee.on('irclib.socket.data')
    def socket_on_data(self, data):
        """event on incoming data"""
        message_pattern = r':(.*)!.+PRIVMSG\s+(#*[^ ]+)\s+:(.*)'
        reply_pattern = r':(.*)\s+(\d{3})\s+(.*)\s+:(.*)'

        lines = data.split("\n")
        for line in lines:
            logging.debug(line)
            matches = re.match(reply_pattern, line)
            if matches and len(matches.groups()) >= 4:
                self.ee.emit('irclib.reply', self, matches)
            if line.startswith("PING"):
                pong = re.match(r'^PING\s+([^ ]+)$', line)
                if pong:
                    self.ee.emit('irclib.ping.received', self, pong[1])
            elif "PRIVMSG" in line:
                matches = re.match(message_pattern, line)
                if matches:
                    msg = str(matches.group(2) + ": " + matches.group(3))
                    self.ee.emit('irclib.message.received', self, msg, matches)
            else:
                self.ee.emit('irclib.data', self, line)

    def receive(self):
        """receive line from irc-server"""
        while True:
            data = self.socket.recv(2048).decode('utf-8')
            if not data:
                continue
            self.ee.emit('irclib.socket.data', self, data)

    def start_requesting(self):
        """download files by package number"""
        bots = json.loads(self.json_data)
        for bot in bots:
            for package in bots[bot]:
                self.request_xdcc(bot, package)


if __name__ == '__main__':
    irc = IrcLib("irc.rizon.net", 6667, "engeleatosbot2",
                 "#horriblesubs", "G:/summer", "")
    irc.connect()
