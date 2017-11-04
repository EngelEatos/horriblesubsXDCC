"""MAL-API"""
import logging
import urllib.parse
import xml.etree.ElementTree as ET

import requests

logging.basicConfig(level=logging.INFO)


def xml_to_json(xml, tag):
    """xml to json"""
    if not xml or not tag:
        return None
    xml = ET.ElementTree(ET.fromstring(xml)).getroot()
    animes = []
    for anime in xml.findall(tag):
        new_anime = dict()
        for attr in anime:
            new_anime[attr.tag] = attr.text
        animes.append(new_anime)
    return animes


class MalAPI():
    """API CLASS"""
    BASEURL = "https://myanimelist.net/api"

    def __init__(self, user, password=None):
        self.user = user
        self.password = password
        self.animes = None
        self.logger = logging.getLogger(__name__)

    def make_api_request(self, url):
        """create api request"""
        url = self.BASEURL + url
        self.logger.debug("requesting: " + str(url))
        request = requests.get(url, auth=(self.user, self.password))
        self.logger.debug("request_code: " + str(request.status_code))
        if request.status_code == 200:
            self.logger.debug("request_text: " + request.text[0, 100])
            return request.text
        return None

    def verify_account(self):
        """verify account"""
        if self.make_api_request("/account/verify_credentials.xml"):
            self.logger.debug("verify_account: ok")
            return True
        self.logger.debug("verfiy_account: invalid")
        return False

    def search_anime(self, phrase):
        """search anime"""
        phrase = urllib.parse.urlencode({'q': phrase})
        self.logger.debug("search_phrase: " + str(phrase))
        return xml_to_json(self.make_api_request("/anime/search.xml?" + phrase), "entry")

    def get_animes(self):
        """return all animes"""
        url = "http://myanimelist.net/malappinfo.php?u=" + \
            self.user + "&status=all&type=anime"
        request = requests.get(url)
        if request.status_code != 200:
            self.logger.debug("request_code: " + str(request.status_code))
            return None
        raw_animes = request.text
        self.logger.debug("request_text: " + request.text[0, 100])
        return xml_to_json(raw_animes, "anime")

    def get_animes_by_status(self, status):
        """get anime by status"""
        if not self.animes:
            self.animes = self.get_animes()
        filtered_animes = []
        for anime in self.animes:
            if int(anime['my_status']) == status:
                filtered_animes.append(anime)
        return filtered_animes

    def get_watching_animes(self):
        """get currently watching animes"""
        return self.get_animes_by_status(1)

    def get_completed_animes(self):
        """get completed animes"""
        return self.get_animes_by_status(2)

    def get_onhold_animes(self):
        """get onhold animes"""
        return self.get_animes_by_status(3)

    def get_dropped_animes(self):
        """get dropped animes"""
        return self.get_animes_by_status(4)

    def get_plantowatch_animes(self):
        """get plan to watch animes"""
        return self.get_animes_by_status(6)


if __name__ == '__main__':
    API = MalAPI("", "")
    print(API.search_anime("naruto"))
