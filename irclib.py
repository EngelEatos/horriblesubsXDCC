import logging
import socket
from pyee import EventEmitter
import re
import queue

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IrcLib():
    CONNECTED = False
    JOINED = False
    ee = EventEmitter()

    def __init__(self, host, port, user, channel):
        self.socket = socket.socket()
        self.host = host
        self.port = port
        self.user = user
        self.channel = channel
        self.queue = queue.Queue()
    
    def send_raw(self, msg):
        """send raw message"""
        logging.debug("%s\n" % msg)
        length = self.socket.sendall(bytes("%s\n" % msg, "UTF-8"))
    
    def privmsg(self, target, msg):
        """send private message"""
        self.send_raw("PRIVMSG " + target + " :" + msg)
    
    def connect(self):
        """"connect to host, port"""
        host = self.host
        user = self.user
        self.socket.connect( (host, self.port) )
        server = host[host.find('.')+1:host.rfind('.')]
        self.send_raw("NICK %s" % user)
        self.send_raw("USER %s %s %s %s" % (user, host, server, user))
        self.receive()
    
    def quit(self):
        self.send_raw("QUIT I'm outty")
        self.socket.close()
        sys.exit(0)

    def is_connected(self):
        return self.CONNECTED
    
    def is_joined(self):
        return self.JOINED

    def pong(self, ping):
        self.send_raw("PONG %s" % ping)
    
    def join(self):
        self.send_raw("JOIN %s" % self.channel)

    @ee.on('irclib.message_received')
    def on_message_received(self, msg):
        print(msg)

    @ee.on('irclib.error')
    def on_error(self, msg):
        print("ERROR - %s" % msg)
    
    @ee.on('irclib.join_successfull')
    def on_successfull_join(self):
        self.JOINED = true

    @ee.on('irclib.motd.end')
    def on_motd_end(self):
         self.join()
    
    @ee.on('irclib.data')
    def on_data(self, line):
        print(line)
    
    @ee.on('irclib.nick_already_in_use')
    def on_nick_already_in_use(self):
        print("nick already in use")
        self.quit()
        
    @ee.on('irclib.socket_onData')
    def socket_onData(self, data):
        message_pattern = r':(.*)!.+PRIVMSG\s+(#*[^ ]+)\s+:(.*)'
        reply_pattern = r':(.*)\s+(\d{3})\s+([^ ]+)\s+:(.*)'

        lines = data.split("\n")
        for line in lines:
            print(line)
            matches = re.match(reply_pattern, line)
            if matches and len(matches.groups()) >= 4:
                if int(matches[2]) == 376:
                    self.ee.emit('irclib.motd.end', self)
                elif int(matches[2]) == 332:
                    self.ee.emit('irclib.join_successfull', self)
                elif int(matches[2]) == 443:
                    self.ee.emit('irclib.nick_already_in_use', self)
            if line.startswith("PING"):
                pong = re.match(r'^PING\s+([^ ]+)$', line)
                if pong:
                    self.pong(pong[1])
                    self.ee.emit('irclib.ping.received', self, pong[1])
            elif "PRIVMSG" in line:
                matches = re.match(message_pattern, line)
                if(matches):
                    msg = str(matches.group(2) + ": " + matches.group(3))
                    self.ee.emit('irclib.message_received', self, msg)
            else:
                self.ee.emit('irclib.data', self, line)

    def receive(self):  
        while True:
            data = self.socket.recv(2048).decode('utf-8')
            if not data:
                continue
            self.ee.emit('irclib.socket_onData', self, data)
            if self.JOINED:
                command = self.queue.get()
                if item is None:
                    continue
                if item[0] == 'DCC':
                    self.privmsg(item[1], 'xdcc send #' + item[2])
                    logging.debug('dcc request sent')
                elif item[0] == 'CMD':
                    self.send_raw(item[1])
                    logging.debug('cmd sent')
                else:
                    self.ee.emit('irclib.error', self, 'command-type wrong')
    
    def add_command(self, command):
        self.queue.put(['CMD', command])
    
    def add_dcc(self, bot, number):
        self.queue.put(['DCC', bot, number])

if __name__ == '__main__':
    irc = IrcLib("irc.rizon.net", 6667, "engeleatosbot2", "#horriblesubs")
    irc.connect()