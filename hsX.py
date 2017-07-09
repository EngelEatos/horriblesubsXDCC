"""Calculates diff of local and online Animes episodes & download these via XDCC"""
import os
import logging
import xdccParser
from subprocess import call
from random import randint
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASEURL = "http://horriblesubs.info"
ANIME_FOLDER = "G:\\summer"
DEFAULT_RES = "720p"
DEFAULT_BOT = "CR-RALEIGH|NEW"

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
            episodes.append(xdccParser.parseName(file))
    return episodes

def get_diff_episodes(packages, local):
    """Return the difference between the folder of packages and local"""
    package_eps = set([p[3][2] for p in packages])
    local_eps = [l[2] for l in local]
    diff_eps = list(set(package_eps) - set(local_eps))
    logging.info("package: " + str(package_eps))
    logging.info("local: " + str(local_eps))
    logging.info("diff: " +  str(diff_eps))
    return diff_eps

def get_episode_package(packages, episode):
    selected = []
    for p in packages:
        if p[3][2] == episode:
            if p[0] == DEFAULT_BOT:
                return p
            else:
                selected.append(p)
    return selected[randint(0, len(selected)-1)]

def printJson(data):
    parsed = json.loads(data)
    print(json.dumps(parsed, indent=4, sort_keys=True))

def main():
    """Main"""
    animes = get_local_animes()
    jList = []
    for show in animes:
        obj = {}
        print(show)
        packages = xdccParser.search(show, DEFAULT_RES)
        local = get_local_episodes(show)
        for ep in get_diff_episodes(packages, local):
            package = get_episode_package(packages, ep)
            obj["botname"] = package[0]
            obj["package"] = package[1]
            obj["folder"] = os.path.join(ANIME_FOLDER, show)
            jList.append(obj)
    json_data = json.dumps({ "todo":jList})
    call(["node", "irc-client.js", json_data])


if __name__ == '__main__':
    main()
