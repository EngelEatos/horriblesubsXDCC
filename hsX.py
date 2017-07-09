"""Calculates diff of local and online Animes episodes & download these via XDCC"""
import os
import logging
import xdccParser
from subprocess import call


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

BASEURL = "http://horriblesubs.info"
ANIME_FOLDER = "G:\\summer"
DEFAULT_RES = "720p"
#DEFAULT_BOT = "CR-RALEIGH|NEW"

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
    logging.info("diff: " +  str(diff_eps))
    return diff_eps

def download():
    json = '{"todo":[{"botname" : "CR-RALEIGH|NEW","package": 5,"folder": "/home/chaos/output/"},{"botname" : "CR-RALEIGH|NEW","package": 160,"folder": "/home/chaos/output/test/"}]}';
    call(["node", "irc-client2.js", json])

def main():
    """Main"""
    animes = get_local_animes()
    for show in animes:
        print(show)
        packages = xdccParser.search(show, DEFAULT_RES)
        local = get_local_episodes(show)
        diff = get_diff_episodes(packages, local)
        print(diff)
        break

if __name__ == '__main__':
    main()
