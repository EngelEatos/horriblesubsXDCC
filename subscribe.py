"""generate config file for subscribing animes """
import os
import json
import showparser
import config
from beautifultable import BeautifulTable

CONFIG_FILE = config.CONFIG_FILE

def subscribe(data):
    """writes shows to file"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)

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
    if os.path.isfile(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    shows = list(showparser.get_airing_shows().keys())
    for idx, show in enumerate(shows):
        num = str(idx+1).zfill(digits(len(shows)))
        if decide(num, show):
            table.append_row([idx+1, show, "x"])
            data.append(show)
        else:
            table.append_row([idx+1, show, "-"])
    os.system('cls' if os.name == 'nt' else 'clear')

    print(table)
    subscribe(data)
    print("\nRESULT:\tsubscribed to " + str(len(data)) + " of total " + str(len(shows)) + " Animes")

if __name__ == '__main__':
    main()
