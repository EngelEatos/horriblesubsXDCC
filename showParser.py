import urllib.parse
import requests
from bs4 import BeautifulSoup as bs

def getShows():
    rShows = {}
    url = "http://horriblesubs.info/shows/"
    soup = getSoup(url)
    shows = soup.find_all('div', attrs={'class':'ind-show linkful'})
    for show in shows:
        link = show.find('a')
        href = link.get('href')
        title = link.get('title')
        rShows[title] = "http://horriblesubs.info" + href
    return rShows

def getSoup(url):
    content = requests.get(url)
    return bs(content.text, 'html.parser')
