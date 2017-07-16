"""Calculates diff of local and online Animes episodes & download these via XDCC"""
import os
import logging
import xdccParser
from subprocess import call
from random import randint
from termcolor import colored
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASEURL = "http://horriblesubs.info"
ANIME_FOLDER = "/run/media/chaos/Animes/summer"
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
    logging.debug("package: " + str(package_eps))
    logging.debug("local: " + str(local_eps))
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
        diff = get_diff_episodes(packages, local)
        if len(diff) > 0:
            print(colored('missing: ' + str(diff), 'red'))
            for ep in diff:
                package = get_episode_package(packages, ep)
                obj["botname"] = package[0]
                obj["package"] = package[1]
                obj["folder"] = os.path.join(ANIME_FOLDER, show)
                jList.append(obj)
        else:
            print(colored('up to date', 'green'))
        print()
    if len(jList) == 0:
        return
    json_data = json.dumps({ "todo":jList})
    call(["node", "irc-client.js", json_data])
    fix()

def fix():
    for root, dirs, files in os.walk(ANIME_FOLDER):
        for file in files:
            if file.endsWith(".mkv\"") and file.startsWith("\""):
                os.rename(file, file[1:-1])

if __name__ == '__main__':
    main()
