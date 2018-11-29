#!/usr/bin/python
"""calculates diff of local and online Animes episodes & download these via XDCC"""
import json
import logging
import multiprocessing as mp
import os
import sys

import colorama
from tabulate import tabulate
from termcolor import colored


from configloader.animesettingsloader import AnimeSettingsLoader
from lib.irclib import IrcLib
from configloader.ircsettingsloader import IrcSettingsLoader
from lib.packagehelper import get_diff_episodes, get_episode_package
from lib.tcpdownloader import tcpdownload, tcpdownload_one
from lib.xdccparser import parse_name, search

logging.basicConfig(level=logging.INFO)


BASEURL = "http://horriblesubs.info"
ISL = IrcSettingsLoader()
ASL = AnimeSettingsLoader()


def get_local_episodes(name):
    """return a list of files of a anime-folder inside ANIME_FOLDER"""
    episodes = []
    path = os.path.join(ISL.get_anime_folder(), name)
    if not os.path.isdir(path):
        os.makedirs(path)
        return episodes
    for episode in os.listdir(path):
        ep_path = os.path.join(path, episode)
        if os.path.isfile(ep_path):
            anime = parse_name(episode)
            file_size = os.stat(ep_path).st_size
            episodes.append([anime, file_size])
    return episodes


def delete_local_episodes(anime, episode):
    """delete the local ep"""
    filename = "[HorribleSubs] " + anime + " - " + episode + " [720p].mkv"
    path = os.path.join(ISL.get_anime_folder(), anime, filename)
    if os.path.isfile(path):
        print("REMOVE: '%s'" % path)
        os.remove(path)


def print_json(data):
    """pretty print of json_data"""
    parsed = json.loads(data)
    print(json.dumps(parsed, indent=4, sort_keys=True))


def check_animes(animes):
    """compare with caching"""
    result = []
    table_data = []
    for idx, show in enumerate(animes):
        packages = search(show, ISL.get_default_res())
        local = get_local_episodes(show)
        diff = get_diff_episodes(packages, local)
        if diff:
            table_data.append([idx + 1, show, colored(str(diff), 'red')])
            for episode in diff:
                delete_local_episodes(show, episode)
                package = get_episode_package(
                    packages, episode, ISL.get_default_bot())
                result.append(package)
        else:
            table_data.append(
                [idx + 1, show, colored("ok" if os.name == 'nt' else "\u2714", 'green')])
    print(tabulate(table_data, headers=[
        'idx', 'anime', 'status'], tablefmt='orgtbl') + "\n")
    return result


def cls():
    """clear terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def check_irc(irc_queue_in, irc_queue_out):
    """check if irc thread is ready to retrieve commands"""
    status = ""
    while status != "letgo":
        irc_queue_in.put("ready")
        status = irc_queue_out.get()
    irc_queue_in.put("clear")


def boot_up():
    """boot up. ASL ISL anime folder"""
    cls()
    if ASL.is_loaded() and ISL.is_loaded():
        print(
            colored("<] configs successfull loaded [>\n", "green").center(80))
    else:
        print(
            colored(">[ configs failed to load. Exit ]<\n", "red").center(80))
        sys.exit(1)
    if not os.path.isdir(ISL.get_anime_folder()):
        print(colored("anime folder not found: {}".format(ISL.get_anime_folder()), "red"))
        sys.exit(1)


def setup_irc():
    """setup irc"""
    manager = mp.Manager()
    irc_queue_in = manager.Queue()
    irc_queue_out = manager.Queue()
    irc = IrcLib(ISL, irc_queue_in, irc_queue_out)
    irc.start()
    check_irc(irc_queue_in, irc_queue_out)
    return irc_queue_in, irc_queue_out


def main():
    """main"""
    colorama.init()
    boot_up()
    animes = ASL.get_watching()
    if len(animes) <= 0:
        print("no subscribed animes. 'python sub_gui.py' for gui or animes.json")
    data = check_animes(animes)
    if not data:
        print(colored("<] nothing to do. [>\n", "green").center(80))
    else:
        irc_queue_in, irc_queue_out = setup_irc()
        if input("press enter to start downloading...") == "":
            if ISL.get_multiprocessing() == 0:
                tcpdownload_one(irc_queue_in, irc_queue_out, data)
            else:
                tcpdownload(irc_queue_in, irc_queue_out, data)
        irc_queue_in.put("exit")


if __name__ == '__main__':
    main()
