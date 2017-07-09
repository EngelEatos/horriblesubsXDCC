import os
import re
import xdccParser
import showParser

baseUrl = "http://horriblesubs.info"
animeFolder = "G:\\summer"
defaultRes = "720p"
defaultBot = "CR-RALEIGH|NEW"

def getLocalAnimes():
    animes = []
    for dir in os.listdir(animeFolder):
        if os.path.isdir(os.path.join(animeFolder, dir)):
            animes.append(dir)
    return animes

def getLocalEpisodes(name):
    episodes = []
    path = os.path.join(animeFolder, name)
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            episodes.append(xdccParser.parseName(file))
    return episodes

def getmissingEpisodes(packages, local):
    pEps = set([p[3][2] for p in packages])
    lEps = [l[2] for l in local]
    print("package: " + str(pEps))
    print("local: " + str(lEps))
    mEps = list(set(pEps) - set(lEps))
    return mEps

def main():
    animes = getLocalAnimes()
    for show in animes:
        print(show)
        packages = xdccParser.search(show, defaultRes)
        local = getLocalEpisodes(show)
        print(getmissingEpisodes(packages, local))

def test():
    print(parseName("[HorribleSubs] Knight's & Magic - 01 [720p].mkv"))


if __name__ == '__main__':
    main()
