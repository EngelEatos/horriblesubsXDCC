import irc.client
import sys
import shlex
import os
import struct

class IRCCat(irc.client.SimpleIRCClient):
    def __init__(self, target):
        irc.client.SimpleIRCClient.__init__(self)
        self.target = target
        self.received_bytes = 0

    def on_welcome(self, connection, event):
        print("welcome")
        if irc.client.is_channel(self.target):
            connection.join(self.target)
        else:
            self.send_it()

    def on_join(self, connection, event):
        print("join")
        self.send_it()

    def on_disconnect(self, connection, event):
        sys.exit(0)

    def send_it(self):
        self.connection.privmsg(self.target, "xdcc send #1123")
        self.connection.privmsg("CR-RALEIGH|NEW", "xdcc send #5")
        #while 1:
        #    line = sys.stdin.readline().strip()
        #    if not line:
        #        break
        #    self.connection.privmsg(self.target, line)
        #self.connection.quit("")

    def on_ctcp(self, connection, event):
        if(len(event.arguments) <= 1):
            return
        payload = event.arguments[1]
        parts = shlex.split(payload)
        print(parts)
        command, filename, peer_address, peer_port, size = parts
        if command != "SEND":
            return
        self.filename = os.path.basename(filename)
        if os.path.exists(self.filename):
            print("A file named", self.filename,
                "already exists. Refusing to save it.")
            self.connection.quit()
            return
        self.file = open(self.filename, "wb")
        peer_address = irc.client.ip_numstr_to_quad(peer_address)
        peer_port = int(peer_port)
        self.dcc = self.dcc_connect(peer_address, peer_port, "raw")

    def on_dccmsg(self, connection, event):
        data = event.arguments[0]
        self.file.write(data)
        self.received_bytes = self.received_bytes + len(data)
        self.dcc.send_bytes(struct.pack("!I", self.received_bytes))

    def on_dcc_disconnect(self, connection, event):
        self.file.close()
        print("Received file %s (%d bytes)." % (self.filename,
                                                self.received_bytes))
        #self.connection.quit()

def main():
    server = "irc.rizon.net"
    port = 6667
    nickname = "testest231"
    target = "Ginpachi-Sensei"
    c = IRCCat(target)
    try:
        c.connect(server, port, nickname)
    except irc.client.ServerConnectionError as x:
        print(x)
        sys.exit(1)
    c.start()

if __name__ == "__main__":
    main()
