"""parse xdcc index site"""
import re
from urllib.parse import quote
import requests
from pyparsing import commaSeparatedList
#result
#    0          1         2     3
# botname - packageNr - size - name
def search(anime, default_res):
    """search xdcc site and parse result"""
    term = anime + " " + default_res
    content = requests.get("http://xdcc.horriblesubs.info/search.php?t=" + quote(term)).text
    matches = re.findall(r'\{(.*?)\}', content)
    result = []
    for match in matches:
        parsedlist = commaSeparatedList.parseString(match)
        itm = [get_value(s) for s in parsedlist]
        itm[3] = parse_name(itm[3])
        if itm[3] is not None and itm[3][1] == anime:
            result.append(itm)
    return result

def parse_name(name):
    """
    parse anime episode name
    [0]sGrp|[1]name|[2]ep|[3]res
    """
    matches = re.findall(r'^\[(.*?)\]\s(.*?)\s-\s(\d+(?:\.\d+|)).+?\[([0-9]{3,4})p\]\.mkv$', name)
    return [match for match in matches[0]] if matches else None

def get_value(pair):
    """get value key:{value}"""
    return pair[pair.find(":")+2:-1] if "\"" in pair else pair[pair.find(":")+1:]

def main():
    """main"""
    result = search("Castlevania", "720p")
    for res in result:
        print(res)

if __name__ == '__main__':
    main()
