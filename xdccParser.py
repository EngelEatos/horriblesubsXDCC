"""parse xdcc index site"""
import re
from urllib.parse import quote

import requests
from pyparsing import commaSeparatedList

# result
#    0          1         2     3
# botname - packageNr - size - name


def search(anime, default_res):
    """search xdcc site and parse result"""
    term = anime + " " + default_res
    content = requests.get(
        "http://xdcc.horriblesubs.info/search.php?t=" + quote(term)).text
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
    Group 1. `HorribleSubs`
    Group 2. `Sagrada Reset`
    Group 3. `03`
    Group 4. `v2`
    Group 5. `720`
    """
    pattern = r'^\[(.*?)\]\s(.*?)\s-\s(\d+(?:\.\d+|))(v\d|).+?\[([0-9]{3,4})p\]\.mkv$'
    matches = re.findall(pattern, name)
    return [match for match in matches[0]] if matches else None


def get_value(pair):
    """get value key:{value}"""
    return pair[pair.find(":") + 2:-1] if "\"" in pair else pair[pair.find(":") + 1:]


def main():
    """main"""
    result = search("Castlevania", "720p")
    for res in result:
        print(res)
