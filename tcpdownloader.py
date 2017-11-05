"""downloader class"""
import json
import logging
import multiprocessing as mp
import os
import socket
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

from xdccparser import parse_name

logging.basicConfig(level=logging.DEBUG)


def download(item, irc_queue_in, irc_queue_out):
    """downlaod files"""
    logger = logging.getLogger("tcpdownloader")
    logger.debug("start download")
    irc_queue_in.put("xdcc_request %s %s" % (item[0], item[1]))
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


def create_queue(data):
    """create all commands"""
    tasks = []
    for bot in data:
        for package in data[bot]:
            tasks.append([bot, package])
    return tasks


def tcpdownload(irc_queue_in, irc_queue_out, json_data):
    """run"""
    tasks = create_queue(json.loads(json_data))
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        futures = [executor.submit(
            download, item, irc_queue_in, irc_queue_out) for item in tasks]
        kwargs = {
            'total': len(futures),
            'unit': 'animes',
            'unit_scale': True,
            'leave': True
        }

        for future in tqdm(as_completed(futures), **kwargs):
            pass


def tcpdownload_one(irc_queue_in, irc_queue_out, json_data):
    """tcpdownload one by one"""
    tasks = create_queue(json.loads(json_data))
    for task in tqdm(tasks, desc="Processing animes"):
        irc_queue_in.put("xdcc_request %s %s" % (task[0], task[1]))
        (server), size, path = irc_queue_out.get()
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        tcp_socket = socket.socket()
        tcp_socket.connect(server)
        parsed = parse_name(os.path.basename(path))
        filename = "{0} - {1}".format(parsed[1], parsed[2])
        current = 0
        with open(path, 'wb') as output_file:
            with tqdm(total=size, desc=filename, unit='B', unit_scale=True) as pbar:
                while current != size:
                    received = tcp_socket.recv(2048)
                    current += len(received)
                    output_file.write(received)
                    pbar.update(len(received))
        tcp_socket.close()
        irc_queue_out.task_done()
