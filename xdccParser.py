import re
import requests
from bs4 import BeautifulSoup as bs
from pyparsing import commaSeparatedList
from urllib.parse import quote
#result
#    0          1         2     3
# botname - packageNr - size - name
def search(anime, defaultRes):
    term = anime + " " + defaultRes
    url = "http://xdcc.horriblesubs.info/search.php?t=" + quote(term)
    content = requests.get(url).text
    matches = re.findall('\{(.*?)\}',content)
    result = []
    for match in matches:
        parsedlist = commaSeparatedList.parseString(match)
        itm = [getValue(s) for s in parsedlist]
        itm[3] = parseName(itm[3])
        if itm[3] is not None and itm[3][1] == anime:
            result.append(itm)
    return result

def parseName(name):
    matches = re.findall('^\[(.*?)\]\s(.*?)\s-\s(\d+(?:\.\d+|)).+?\[([0-9]{3,4})p\]\.mkv$', name)
    return [match for match in matches[0]] if len(matches) > 0 else None


def getValue(s):
    return s[s.find(":")+2:-1] if "\"" in s else s[s.find(":")+1:]

def main():
    result = search("Castlevania", "720p")
    for res in result:
        print(res)

if __name__ == '__main__':
    main()
