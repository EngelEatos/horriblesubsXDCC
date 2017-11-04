"""downloader class"""
import json
import logging
import os
import socket
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tcpdownloader")


def download(item, irc_queue_in, irc_queue_out):
    """downlaod files"""
    logger.debug("start download")
    irc_queue_in.put("xdcc_request %s %s" % (item[0], item[1]))
    (server), size, path = irc_queue_out.get()
    path = path.replace("Knight_s & Magic", "Knight's & Magic")
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    logger.debug(str(server), size, path)
    tcp_socket = socket.socket()
    tcp_socket.connect(server)
    output_file = open(path, 'wb')
    current = 0
    while current != size:
        logger.debug(str(current) + "/" + str(size))
        received = tcp_socket.recv(2048)
        current += len(received)
        output_file.write(received)
    output_file.close()
    tcp_socket.close()
    irc_queue_out.task_done()
    logger.debug("download return")
    return True


def create_queue(data):
    """create all commands"""
    logger.debug("create queue")
    tasks = []
    for bot in data:
        for package in data[bot]:
            tasks.append([bot, package])
    return tasks


def tcpdownload(irc_queue_in, irc_queue_out, json_data):
    """run"""
    logger.debug("start tcpdownlod")
    logger.debug(json_data)
    tasks = create_queue(json.loads(json_data))
    with ProcessPoolExecutor(max_workers=5) as executor:
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
