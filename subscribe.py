""" generate config file for subscribing animes """
import os
import json
import showparser
import config

CONFIG = config.CONFIG

def subscribe(data):
    """writes shows to file"""
    with open(CONFIG, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)

def decide(i, show):
    """decide if subscribe to show - takes yes/no"""
    while True:
        answer = input("[%s]\tsubscribe to '%s'? [y/n]\t" % (i, show))
        if not answer:
            return True
            #continue
        answer = answer[0].lower()
        valid = ["y", "n"]
        if answer in valid:
            return answer == "y"

def main():
    """MAIN"""
    data = []
    if os.path.isfile(CONFIG):
        os.remove(CONFIG)
    shows = list(showParser.get_airing_shows().keys())
    for i in enumerate(shows):
        num = str(i+1).zfill(len(str(len(shows))))
        if decide(num, shows[i]) and shows[i] not in data:
            data.append(shows[i])
    subscribe(data)
    print("\nRESULT:\tsubscribed to " + str(len(data)) + " of total " + str(len(shows)) + " Animes")

if __name__ == '__main__':
    main()
