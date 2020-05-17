from lib.ircsettingsloader import IrcSettingsLoader
import multiprocessing as mp
from lib.irclib import IrcLib
import time
import socket

bots = ["Ginpachi-Sensei", "CR-RALEIGH|NEW", "CR-HOLLAND|NEW", "CR-BATCH|720p", "CR-ARCHIVE|720p", "ARUTHA-BATCH|720p"]
ISL = IrcSettingsLoader()


def measure(irc_queue_in, irc_queue_out, data):
    """tcpdownload one by one"""
    result = []
    for task in data:
        print(task["bot"])
        irc_queue_in.put("xdcc_request %s %s" % (task["bot"], task["package_nr"]))
        (server), size, _path = irc_queue_out.get()
        tcp_socket = socket.socket()
        tcp_socket.connect(server)
        current = 0
        start = time.perf_counter()
        while current != size:
            received = tcp_socket.recv(2048)
            current += len(received)
        r = time.perf_counter() - start
        tcp_socket.close()
        irc_queue_out.task_done()
        result.append( (size/r, size, r, task["bot"]) )
    return result

def check_irc(irc_queue_in, irc_queue_out):
    """check if irc thread is ready to retrieve commands"""
    status = ""
    while status != "letgo":
        irc_queue_in.put("ready")
        status = irc_queue_out.get()
    irc_queue_in.put("clear")

def setup_irc(k):
    """setup irc"""
    manager = mp.Manager()
    irc_queue_in = manager.Queue()
    irc_queue_out = manager.Queue()
    irc = IrcLib(k, irc_queue_in, irc_queue_out)
    irc.start()
    check_irc(irc_queue_in, irc_queue_out)
    return irc_queue_in, irc_queue_out

def save_result(r):
    ranking = [x[3] for x in sorted(r, reverse=True)]
    print("result: {}".format(ranking))
    ISL.set_bot_ranking(ranking)
    ISL.save()

if __name__ == '__main__':
    mp.freeze_support()
    irc_queue_in, irc_queue_out = setup_irc(ISL)
    data = [{"bot": bot, "package_nr" : 1, "name": "test"} for bot in bots]
    s = measure(irc_queue_in, irc_queue_out, data)
    irc_queue_in.put("exit")
    