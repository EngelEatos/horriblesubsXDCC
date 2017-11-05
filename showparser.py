"""requests source and parse all/airing shows """
import cfscrape
import requests
from bs4 import BeautifulSoup as bs


def get_shows(url):
    """get all shows from url"""
    result = {}
    shows = get_soup(url).find_all('div', attrs={'class': 'ind-show'})
    for show in shows:
        link = show.find('a')
        title = link.get('title') if link else show.text
        if not title:
            continue
        href = "http://horriblesubs.info" + \
            link.get('href') if link else "not yet"
        result[title] = href
    return result


def get_airing_shows():
    """get airing shows"""
    return get_shows("http://horriblesubs.info/current-season/")


def get_all_shows():
    """get all shows"""
    return get_shows("http://horriblesubs.info/shows/")


def get_soup(url):
    """get soup of url"""
    request = requests.get(url)
    content = request.text
    if request.status_code == 503:
        scraper = cfscrape.create_scraper()
        content = scraper.get(url).content
    return bs(content, 'html.parser')
