"""generate config file for subscribing animes """
import os

from beautifultable import BeautifulTable

from animesettingsloader import AnimeSettingsLoader
from showparser import get_airing_shows

ASL = AnimeSettingsLoader()


def subscribe(data):
    """writes shows to file"""
    ASL.set_watching(data)
    ASL.save()


def decide(i, show):
    """decide if subscribe to show - takes yes/no"""
    while True:
        answer = input("[%s]\tsubscribe to '%s'? [y/n]\t" % (i, show))
        if not answer:
            continue
        answer = answer[0].lower()
        if answer in ["y", "n"]:
            return answer == "y"


def digits(value):
    """return count of digits of number"""
    return len(str(value))


def main():
    """main"""
    table = BeautifulTable()
    table.column_headers = ["idx", "anime", "subscribed"]
    data = []

    shows = list(get_airing_shows().keys())
    for idx, show in enumerate(shows):
        num = str(idx + 1).zfill(digits(len(shows)))
        if decide(num, show):
            table.append_row([idx + 1, show, "x"])
            data.append(show)
        else:
            table.append_row([idx + 1, show, "-"])
    os.system('cls' if os.name == 'nt' else 'clear')

    print(table)
    subscribe(data)
    print("\nRESULT:\tsubscribed to " + str(len(data)) +
          " of total " + str(len(shows)) + " Animes")


if __name__ == '__main__':
    main()
