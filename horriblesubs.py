"""Calculates diff of local and online Animes episodes & download these via XDCC"""
import os
import logging
import json
from random import randint
from termcolor import colored
import config
import irclient
import xdccparser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASEURL = config.BASEURL
ANIME_FOLDER = config.ANIME_FOLDER
DEFAULT_RES = config.DEFAULT_RES
DEFAULT_BOT = config.DEFAULT_BOT

def get_local_animes():
    """Return the folder/animes from ANIME_FOLDER."""
    animes = []
    for folder in os.listdir(ANIME_FOLDER):
        if os.path.isdir(os.path.join(ANIME_FOLDER, folder)):
            animes.append(folder)
    return animes

def get_local_episodes(name):
    """Return a list of files of a anime-folder inside ANIME_FOLDER"""
    episodes = []
    path = os.path.join(ANIME_FOLDER, name)
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            episodes.append(xdccParser.parse_name(file))
    return episodes

def get_diff_episodes(packages, local):
    """Return the difference between the folder of packages and local"""
    package_eps = set([p[3][2] for p in packages])
    local_eps = [l[2] for l in local]
    diff_eps = list(set(package_eps) - set(local_eps))
    logging.debug("package: " + str(package_eps))
    logging.debug("local: " + str(local_eps))
    return diff_eps

def get_episode_package(packages, episode):
    """get availible package of episode, first default then random"""
    selected = []
    for package in packages:
        if package[3][2] == episode:
            if package[0] == DEFAULT_BOT:
                return package
            else:
                selected.append(package)
    return selected[randint(0, len(selected)-1)]

def print_json(data):
    """pretty print of json_data"""
    parsed = json.loads(data)
    print(json.dumps(parsed, indent=4, sort_keys=True))

def main():
    """Main"""
    animes = get_local_animes()
    result = {}
    for show in animes:
        print(show)
        packages = xdccParser.search(show, DEFAULT_RES)
        local = get_local_episodes(show)
        diff = get_diff_episodes(packages, local)
        if diff:
            print(colored('missing: ' + str(diff), 'red'))
            for episode in diff:
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
    irc = irclient.IRCclient(json_data, ANIME_FOLDER)
    irc.connect()

if __name__ == '__main__':
    main()
