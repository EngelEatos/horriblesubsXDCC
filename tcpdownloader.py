"""downloader class"""
import json
import logging
import socket
import threading
from queue import Queue

from tqdm import tqdm

from irclib import IrcLib
from ircsettingsloader import IrcSettingsLoader
from xdccparser import parse_name

logging.basicConfig(format="%(asctime)-15s %(levelname)s %(message)s",
                    datefmt="%F %T", level=logging.INFO)


class TcpDownloader():
    """downloader"""

    def __init__(self, num_threads, json_data):
        isl = IrcSettingsLoader()
        self.irc = IrcLib(isl)
        self.irc.connect()
        self.num_threads = num_threads
        self.threads = []
        self.queue = Queue()
        self.setup(json_data)

    def create_queue(self, data):
        """create all commands"""
        for bot in data:
            for package in data[bot]:
                self.queue.put([bot, package])
        self.shutdown()

    def setup(self, json_data):
        """run"""
        logging.debug(json_data)
        for i in range(self.num_threads):
            logging.debug("Thread #%d start", i)
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.threads.append(thread)
        self.create_queue(json.loads(json_data))

    def worker(self):
        """work next item in queue"""
        while True:
            item = self.queue.get()
            if item is None:
                break
            self.download(item)
            self.queue.task_done()

    def shutdown(self):
        """shutdown all threads"""
        for i in range(self.num_threads):
            logging.debug("Thread #%d stopped", i)
            self.queue.put(None)
        for thread in self.threads:
            thread.join()
        self.irc.quit()

    def download(self, item):
        """downlaod files"""
        logging.debug("active: " + str(self.irc.joined))
        while not self.irc.joined:
            pass

        self.irc.request_xdcc(item[0], item[1])
        (server), size, path = self.irc.queue.get()
        logging.debug(str(server), size, path)
        tcp_socket = socket.socket()
        tcp_socket.connect(server)
        output_file = open(path, 'wb')
        anime = parse_name(path[path.rfind('\\') + 1:])
        desc = anime[1] + " - " + anime[2]
        current = 0
        with tqdm(total=size, unit='B', unit_scale=True, desc=desc) as pbar:
            while current != size:
                received = tcp_socket.recv(2048)
                current += len(received)
                output_file.write(received)
                pbar.update(len(received))
        output_file.close()
        tcp_socket.close()
        self.irc.queue.task_done()
