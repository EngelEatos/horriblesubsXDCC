"""parse xdcc index site"""
import re
from urllib.parse import quote

import cfscrape
import requests
from pyparsing import commaSeparatedList


def search(anime, default_res):
    """
    search xdcc site and parse result
       0          1         2     3
    botname - packageNr - size - name
    """
    search_term = quote(anime + " " + default_res)
    url = "http://xdcc.horriblesubs.info/search.php?t=" + search_term
    content = get_content(url)
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
    Group 0. `HorribleSubs`
    Group 1. `Sagrada Reset`
    Group 2. `03`
    Group 3. `v2`
    Group 4. `720`
    """
    pattern = r'^\[(.*?)\]\s(.*?)\s-\s(\d+(?:\.\d+|))(v\d|).+?\[([0-9]{3,4})p\]\.mkv$'
    matches = re.findall(pattern, name)
    return [match for match in matches[0]] if matches else None


def get_value(pair):
    """get value key:{value}"""
    return pair[pair.find(":") + 2:-1] if "\"" in pair else pair[pair.find(":") + 1:]


def get_content(url):
    """get content - cfscrape"""
    request = requests.get(url)
    content = request.text
    if request.status_code == 503:
        scraper = cfscrape.create_scraper()
        content = scraper.get(url).content
    return content
