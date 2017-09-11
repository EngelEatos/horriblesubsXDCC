"""calculates diff of local and online Animes episodes & download these via XDCC"""
import os
import logging
import json
from random import randint
from termcolor import colored
import config
import irclient
import xdccparser
import colorama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASEURL = config.BASEURL
ANIME_FOLDER = config.ANIME_FOLDER
DEFAULT_RES = config.DEFAULT_RES
DEFAULT_BOT = config.DEFAULT_BOT
CONFIG_FILE = config.CONFIG_FILE

def get_local_animes():
    """return the folder/animes from ANIME_FOLDER."""
    animes = []
    for folder in os.listdir(ANIME_FOLDER):
        if os.path.isdir(os.path.join(ANIME_FOLDER, folder)):
            animes.append(folder)
    return animes

def get_subscribed_animes():
    """return subscribed animes listed in CONFIG_FILE"""
    animes = []
    with open(CONFIG_FILE, 'r') as config:
        animes = json.load(config)
    return animes

def get_local_episodes(name):
    """return a list of files of a anime-folder inside ANIME_FOLDER"""
    episodes = []
    path = os.path.join(ANIME_FOLDER, name)
    if not os.path.isdir(path):
        os.makedirs(path)
    for ep in os.listdir(path):
        ep_path = os.path.join(path, ep)
        if os.path.isfile(ep_path):
            episodes.append([xdccparser.parse_name(ep), os.stat(ep_path).st_size])
    return episodes

def distinct_packages(packages):
    """return a distinct list of the packages"""
    result = []
    eps = []
    for p in packages:
        if p[3][2] not in eps:
            eps.append(p[3][2])
            result.append(p)
    return result

def get_size(local, ep):
    """return the size of ep in local episodes"""
    for l in local:
        if l[0][2] == ep:
            return l[1]
    return -1

def get_diff_episodes(packages, local):
    """return the difference between the folder of packages and local"""
    todo = []
    local_eps = [l[0][2] for l in local]
    packages = distinct_packages(packages)
    for p in packages:
        ep = p[3][2]
        size = int(p[2])
        if ep in local_eps:
            local_size = int(get_size(local, ep)/(1024*1024))
            #print(str(size) + " =?= " + str(local_size))
            if size-50 <= local_size <= size+50:
                continue
        todo.append(ep)
    return todo

def delete_local_episodes(anime, episode):
    """delete the local ep"""
    path = os.path.join(ANIME_FOLDER, anime, "[HorribleSubs] " + anime + " - " + episode + " [720p].mkv")
    if os.path.isfile(path):
        print("REMOVE: '%s'" % path)
        os.remove(path)

def get_packages_by_ep(packages, episode):
    result = []
    version_result = []
    for package in packages:
        if package[3][2] == episode:
            if package[3][3]:
                version_result.append(package)
            else:
                result.append(package)
    return (result, version_result)

def get_latest_packages(version_result):
    packs = []
    max = 0
    for result in version_result:
        version = int(result[3][3][1:])
        if version < max:
            continue
        if version > max:
            packs.clear()
            max = version
        packs.append(result)
    return packs

def get_packages(packages):
    selected = []
    for package in packages:
        if package[0] == DEFAULT_BOT:
            return package
        else:
            selected.append(package)
    return selected[randint(0, len(selected)-1)]

def get_episode_package(packages, episode):
    """get availible package of episode, first default then random"""
    (result, version_result) = get_packages_by_ep(packages, episode)
    packages = get_latest_packages(version_result) if version_result else result
    return get_packages(packages)

def print_json(data):
    """pretty print of json_data"""
    parsed = json.loads(data)
    print(json.dumps(parsed, indent=4, sort_keys=True))

def main():
    """main"""
    colorama.init()
    animes = get_subscribed_animes() if os.path.isfile(CONFIG_FILE) else get_local_animes()
    result = {}
    for show in animes:
        print(show)
        packages = xdccparser.search(show, DEFAULT_RES)
        local = get_local_episodes(show)
        diff = get_diff_episodes(packages, local)
        if diff:
            print(colored('missing: ' + str(diff), 'red'))
            for episode in diff:
                delete_local_episodes(show, episode)
                package = get_episode_package(packages, episode)
                if not package[0] in result:
                    result[package[0]] = [package[1]]
                else:
                    result[package[0]].append(package[1])
        else:
            print(colored('up to date', 'green'))
        print()
    if not result:
        return
    json_data = json.dumps(result)
    print_json(json_data)
    irc = irclient.irc_client(json_data, ANIME_FOLDER)
    irc.connect()

if __name__ == '__main__':
    main()
