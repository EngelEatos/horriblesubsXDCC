"""parse xdcc index site"""
import re
from urllib.parse import quote

import requests
import cfscrape


def search(anime, default_res):
    """
    search xdcc site and parse result
       0          1         2     3
    botname - packageNr - size - name
    """
    search_term = quote(anime + " " + default_res)
    url = "http://xdcc.horriblesubs.info/search.php?t=" + search_term
    content = get_content(url)
    result = []
    for line in content.split("\n"):
        if not line:
            continue
        package = {}
        matches = re.match(
            r'^p.k\[\d+\]\s=\s\{b:.(.+?).,\sn:(\d+),\ss:(\d+),\sf:.(.+?).\};', line)
        parsed_name = parse_name(matches[4])
        if not parsed_name:
            continue
        package['bot'] = matches[1]
        package['package_nr'] = matches[2]
        package['size'] = matches[3]
        package['name'] = matches[4]
        package.update(parsed_name)
        result.append(package)
    return result


def parse_name(name):
    """
    return parsed name as dict or None
    {subgrp, anime, episode, version, resolution}
    """
    pattern = r'^\[(.*?)\]\s(.*?)\s-\s(\d+(?:\.\d+|))(v\d|).+?\[([0-9]{3,4})p\]\.mkv$'
    matches = re.match(pattern, name)
    if matches and len(matches.groups()) >= 5:
        return {"subgrp": matches[1], "anime": matches[2], "episode": matches[3],
                "version": matches[4], "resolution": matches[5]}
    return None

def get_content(url):
    """get content - cfscrape"""
    request = requests.get(url)
    content = request.text
    if request.status_code == 503:
        scraper = cfscrape.create_scraper()
        content = scraper.get(url).content
    return content
