"""animeinfo"""
import os
import requests
from showparser import get_soup
from jsonloader import JsonLoader


def download_image(image):
    """download image"""
    image_file = "cache/{}".format(image[image.rfind("/") + 1:])
    if not os.path.isdir(os.path.dirname(image_file)):
        os.makedirs(os.path.dirname(image_file))
    with open(image_file, 'wb') as file:
        file.write(requests.get(image).content)
    return image_file


class AnimeInfo(JsonLoader):
    """Animeinfo"""
    config_file = "cache/anime_cache.json"

    def __init__(self, name, url):
        self.json_data = self.load()
        self.soup = get_soup(url)
        self.name = name

    def create_config(self):
        """create config"""
        self.json_data = {}
        self.save()

    def add_anime_info(self, image, desc):
        """add anime info"""
        self.json_data[self.name] = [image, desc]
        self.save()

    def get_anime_info(self):
        """get anime info"""
        if self.name in self.json_data:
            info = self.json_data[self.name]
            return info[0], info[1]
        image_file, desc = self.get_info()
        self.add_anime_info(image_file, desc)
        return image_file, desc

    def get_info(self):
        """get info"""
        image = self.soup.find(
            "img", attrs={"class": "size-full alignleft"})['src']
        desc = self.soup.find(
            "div", attrs={"class": "series-desc"}).text.strip()
        image_file = download_image(image)
        return image_file, desc
