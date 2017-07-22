""" requests source and parse all/airing shows """
import requests
import cfscrape
from bs4 import BeautifulSoup as bs

def get_shows(url):
    """get all shows from url"""
    result = {}
    shows = get_soup(url).find_all('div', attrs={'class':'ind-show linkful'})
    for show in shows:
        link = show.find('a')
        title = link.get('title')
        result[title] = "http://horriblesubs.info" + link.get('href')
    return result

def get_airing_shows():
    """get airing shows"""
    return get_shows("http://horriblesubs.info/current-season/")

def get_all_shows():
    """get all shows"""
    return get_shows("http://horriblesubs.info/shows/")

def get_soup(url):
    """get soup of url"""
    content = requests.get(url)
    if content.status_code == 503:
        scraper = cfscrape.create_scraper()
        return bs(scraper.get(url).content, 'html.parser')
    return bs(content.text, 'html.parser')
