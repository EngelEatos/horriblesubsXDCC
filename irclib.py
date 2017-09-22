"""simple ircclient to download anime packages"""
import ipaddress
import logging
import os
import re
import socket
import sys
import threading
from queue import Queue

from pyee import EventEmitter

from xdccparser import parse_name

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class IrcLib():
    """IrcLib"""
    ee = EventEmitter()

    def __init__(self, isl):
        self.socket = socket.socket()
        self.serverinfo = isl.get_serverinfo()
        self.queue = Queue()
        self.active = False
        self.whois = dict()
        self.joined = False
        self.receive_thread = threading.Thread(target=self.receive)

    def send_raw(self, msg):
        """send raw message"""
        logging.debug("< %s\n", msg)
        self.socket.sendall(bytes("%s\n" % msg, "UTF-8"))

    def privmsg(self, target, msg):
        """send private message"""
        self.send_raw("PRIVMSG %s :%s" % (target, msg))

    def request_xdcc(self, bot, package):
        """request xdcc package"""
        self.privmsg(bot, "xdcc send #" + package)

    def connect(self):
        """"connect to host, port"""
        host = self.serverinfo['host']
        user = self.serverinfo['user']
        self.socket.connect((host, self.serverinfo['port']))
        server = host[host.find('.') + 1:host.rfind('.')]
        self.send_raw("NICK %s" % user)
        self.send_raw("USER %s %s %s %s" % (user, host, server, user))
        self.active = True
        self.receive_thread.start()

    def join(self):
        """join channel"""
        logging.debug("send_join")
        self.send_raw("JOIN %s" % self.serverinfo['channel'])

    def quit(self):
        """send quit and exit"""
        self.send_raw("QUIT I'm outty")
        self.joined = False
        self.active = False

    @ee.on('irclib.receive.exit')
    def on_receive_exit(self):
        """event on receive thread exit"""
        self.socket.close()
        sys.exit(0)

    @ee.on('irclib.ping.received')
    def pong(self, ping):
        """event on incoming ping -> pong"""
        self.send_raw("PONG %s" % ping)

    @ee.on('irclib.ctcp')
    def on_ctcp(self, match):
        """on incoming ctcp request"""
        logging.debug("on_ctcp")
        match_list = [match.group(i)
                      for i in range(len(match.groups()) + 1)][1:]
        filename, host, port, size = match_list
        # msg_matches[1][msg_matches[1].find('!') + 1:]
        filename = filename[1:-1] if '"' in filename else filename
        host = str(ipaddress.ip_address(int(host)))
        download_path = os.path.join(
            self.serverinfo['anime_folder'], parse_name(filename)[1], filename)
        print("%s %s %s %s" % (host, port, filename, size))
        self.queue.put([(host, int(port)), int(size), download_path])

    @ee.on('irclib.message.received')
    def on_message_received(self, msg, matches):
        """event on incoming private message"""
        dcc_pattern = r'^.+?DCC\sSEND\s(.*?)\s(\d+)\s(\d+)\s(\d+).+?$'
        match = re.match(dcc_pattern, matches[3])
        if match and len(match.groups()) >= 4:
            self.ee.emit('irclib.ctcp', self, match)
        else:
            logging.debug(msg)

    @ee.on('irclib.logged.in')
    def on_logged_in(self):
        """event on successfull login"""
        print("logged in as %s" % self.serverinfo('user'))

    @ee.on('irclib.join.successfull')
    def on_successfull_join(self):
        """event on successfull join"""
        logging.debug("join sucessfull")
        self.joined = True

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
        logging.debug(self.active)
        # msg[msg.find('~'):msg.rfind(' ')].replace(' ', '@'))

    @ee.on('irclib.nick.error')
    def on_nick_already_in_use(self):
        """event on nick_error message"""
        print("nick already in use")
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
            if not self.active:
                break
            data = self.socket.recv(2048).decode('utf-8')
            if not data:
                continue
            self.ee.emit('irclib.socket.data', self, data)
        self.ee.emit('irclbi.receive.exit', self)
