"""downloader class"""
import logging
import multiprocessing as mp
import os
import socket
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm


logging.basicConfig(level=logging.INFO)


def download(item, irc_queue_in, irc_queue_out):
    """downlaod files"""
    logger = logging.getLogger("tcpdownloader")
    logger.debug("start download")
    irc_queue_in.put("xdcc_request %s %s" % (item["bot"], item["package_nr"]))
    (server), size, path = irc_queue_out.get()
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    logger.debug(str(server), size, path)
    tcp_socket = socket.socket()
    tcp_socket.connect(server)
    current = 0
    with open(path, 'wb') as output_file:
        while current != size:
            received = tcp_socket.recv(2048)
            current += len(received)
            output_file.write(received)
    tcp_socket.close()
    irc_queue_out.task_done()
    logger.debug("download return")
    return True

def tcpdownload(irc_queue_in, irc_queue_out, data):
    """run"""
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        futures = [executor.submit(
            download, item, irc_queue_in, irc_queue_out) for item in data]
        kwargs = {
            'total': len(futures),
            'unit': 'animes',
            'unit_scale': True,
            'leave': True
        }
        for _future in tqdm(as_completed(futures), **kwargs):
            pass


def tcpdownload_one(irc_queue_in, irc_queue_out, data):
    """tcpdownload one by one"""
    for task in tqdm(data, desc="Processing animes"):
        irc_queue_in.put("xdcc_request %s %s" % (task["bot"], task["package_nr"]))
        (server), size, path = irc_queue_out.get()
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        tcp_socket = socket.socket()
        tcp_socket.connect(server)
        current = 0
        with open(path, 'wb') as output_file:
            with tqdm(total=size, desc=task["name"], unit='B', unit_scale=True) as pbar:
                while current != size:
                    received = tcp_socket.recv(2048)
                    current += len(received)
                    output_file.write(received)
                    pbar.update(len(received))
        tcp_socket.close()
        irc_queue_out.task_done()
