"""simple ircclient to download anime packages"""
import ipaddress
import logging
import os
import re
import socket
import sys
from threading import Thread

from pyee import EventEmitter

from xdccparser import parse_name


class IrcLib(Thread):
    """IrcLib"""
    ee = EventEmitter()

    def __init__(self, isl, queue_in, queue_out, logger):
        Thread.__init__(self)
        self.logger = logger or logging.getLogger(__name__)
        self.socket = socket.socket()
        self.serverinfo = isl.get_serverinfo()
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.active = False
        self.whois = dict()
        self.joined = False

    def send_raw(self, msg):
        """send raw message"""
        self.logger.debug("< %s\n", msg)
        self.socket.sendall(bytes("%s\n" % msg, "UTF-8"))

    def privmsg(self, target, msg):
        """send private message"""
        self.send_raw("PRIVMSG %s :%s" % (target, msg))

    def request_xdcc(self, bot, package):
        """request xdcc package"""
        self.privmsg(bot, "xdcc send #" + package)

    def run(self):
        self.connect()

    def connect(self):
        """"connect to host, port"""
        host = self.serverinfo['host']
        user = self.serverinfo['user']
        self.socket.connect((host, self.serverinfo['port']))
        server = host[host.find('.') + 1:host.rfind('.')]
        self.send_raw("NICK %s" % user)
        self.send_raw("USER %s %s %s %s" % (user, host, server, user))
        self.active = True
        self.receive()

    def join_channel(self):
        """join channel"""
        self.logger.debug("send_join")
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
        self.logger.debug("on_ctcp")
        match_list = [match.group(i)
                      for i in range(len(match.groups()) + 1)][1:]
        filename, host, port, size = match_list
        # msg_matches[1][msg_matches[1].find('!') + 1:]
        filename = filename[1:-1] if '"' in filename else filename
        host = str(ipaddress.ip_address(int(host)))
        download_path = os.path.join(
            self.serverinfo['anime_folder'], parse_name(filename)[1], filename)
        #print("%s %s %s %s" % (host, port, filename, size))
        self.queue_out.put([(host, int(port)), int(size), download_path])

    @ee.on('irclib.message.received')
    def on_message_received(self, msg, matches):
        """event on incoming private message"""
        dcc_pattern = r'^.+?DCC\sSEND\s(.*?)\s(\d+)\s(\d+)\s(\d+).+?$'
        match = re.match(dcc_pattern, matches[3])
        if match and len(match.groups()) >= 4:
            self.ee.emit('irclib.ctcp', self, match)
        else:
            self.logger.debug(msg)

    @ee.on('irclib.logged.in')
    def on_logged_in(self):
        """event on successfull login"""
        print("logged in as %s" % self.serverinfo('user'))

    @ee.on('irclib.join.successfull')
    def on_successfull_join(self):
        """event on successfull join"""
        self.logger.debug("join sucessfull")
        self.joined = True

    @ee.on('irclib.motd.end')
    def on_motd_end(self):
        """event on incoming motd message"""
        self.logger.debug("on_motd_end")
        self.join_channel()

    @ee.on('irclib.data')
    def on_data(self, line):
        """event on incoming unkown data"""
        self.logger.debug(line)

    @ee.on('irclib.bot.info')
    def on_bot_info(self, matches):
        """event on incoming bot info"""
        self.logger.debug(matches.groups())
        self.logger.debug(self.active)
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
            self.logger.debug("reply-logged")
            self.ee.emit('irclib.logged.in', self)
        elif case == 311:
            self.logger.debug("reply-bot-info-received")
            self.ee.emit('irclib.bot.info', self, matches)
        elif case == 332:
            self.logger.debug("reply-join")
            self.ee.emit('irclib.join.successfull', self)
        elif case == 376:
            self.logger.debug("reply-motd")
            self.ee.emit('irclib.motd.end', self)
        elif case == 443:
            self.logger.debug("reply-nick")
            self.ee.emit('irclib.nick.error', self)
        else:
            self.logger.debug(matches.groups())

    @ee.on('irclib.socket.data')
    def socket_on_data(self, data):
        """event on incoming data"""
        message_pattern = r':(.*)!.+PRIVMSG\s+(#*[^ ]+)\s+:(.*)'
        reply_pattern = r':(.*)\s+(\d{3})\s+(.*)\s+:(.*)'

        lines = data.split("\n")
        for line in lines:
            self.logger.debug(line)
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
            if self.queue_in.empty():
                continue
            cmd = self.queue_in.get().split(" ")
            if cmd[0] == "ready":
                self.queue_out.put("letgo" if self.joined else "no")
            elif cmd[0] == "xdcc_request":
                self.request_xdcc(cmd[1], cmd[2])
            elif cmd[0] == "exit":
                break
            elif cmd[0] == "clear":
                while not self.queue_out.empty():
                    self.queue_out.get()
        self.ee.emit('irclbi.receive.exit', self)
