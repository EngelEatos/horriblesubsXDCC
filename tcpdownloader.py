"""downloader class"""
import json
import logging
import socket
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

logging.basicConfig(level=logging.INFO)


def download(item, irc_queue_in, irc_queue_out):
    """downlaod files"""
    irc_queue_in.put("xdcc_request %s %s" % (item[0], item[1]))
    (server), size, path = irc_queue_out.get()
    tcp_socket = socket.socket()
    tcp_socket.connect(server)
    output_file = open(path, 'wb')
    current = 0
    while current != size:
        received = tcp_socket.recv(2048)
        current += len(received)
        output_file.write(received)
    output_file.close()
    tcp_socket.close()
    irc_queue_out.task_done()
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
