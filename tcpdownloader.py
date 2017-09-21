"""downloader for downloads over tcp"""
import socket
import threading
from queue import Queue

from tqdm import tqdm


class TcpDownloader():
    """TcpDownloader class"""

    def __init__(self, num_threads):
        self.queue = Queue()
        self.num_threads = num_threads
        self.threads = []
        self.current_pbar = 0

    def get_queue_size(self):
        """return queue size"""
        return self.queue.empty()

    def add_download(self, host, port, size, download_path):
        """add download-package to queue"""
        self.queue.put([host, port, size, download_path, self.current_pbar])
        self.current_pbar += 1

    def worker(self):
        """work next item in queue"""
        while True:
            item = self.queue.get()
            if item is None:
                break
            self.download(item)
            self.queue.task_done()

    def start(self):
        """setup threads and start"""
        for i in range(self.num_threads):
            print("Thread #%d start" % i)
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.threads.append(thread)

    def shutdown(self):
        """shutdown all threads"""
        for i in range(self.num_threads):
            print("Thread #%d stopped" % i)
            self.queue.put(None)
        for thread in self.threads:
            thread.join()

    def download(self, item):
        """core function - establish socket and download"""
        #item = [host, port, size, download_path]
        tcp_socket = socket.socket()
        tcp_socket.connect((item[0], item[1]))
        output_file = open(item[3], 'wb')
        size = item[2]
        print(item[3])
        filename = item[3][item[3].rfind('\\') + 1:]
        current = 0
        with tqdm(total=size, unit='B', unit_scale=True, desc=filename) as pbar:
            while current != size:
                received = tcp_socket.recv(2048)
                current += len(received)
                output_file.write(received)
                pbar.update(len(received))
        output_file.close()
        tcp_socket.close()
        #print("DONE - " + item[3])
