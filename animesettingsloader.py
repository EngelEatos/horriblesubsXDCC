from jsonloader import JsonLoader
from datetime import datetime
import showparser

class AnimeSettingsLoader(JsonLoader):
    """Wrapper-class for anime-settings"""
    CONFIG_FILE = "settings/animes.json"
    
    def __init__(self):
        self.json_data = self.load()

    def create_config(self, watching=""):
        self.json_data = {"animes" : {"watching": watching, "airing": showparser.get_airing_shows(),
                "all": showparser.get_all_shows(), "modified_date": datetime.now()}}
        self.save()

    def get_anime_settings(self):
        """return anime-settings"""
        return self.get_value('animes')

    def set_anime_settings(self, anime_settings):
        """set anime-settings"""
        self.set_json_data(
            self.change_key('animes', anime_settings))

    def get_airing(self):
        """return airing"""
        return self.get_value('airing', self.get_anime_settings())

    def set_airing(self, airing):
        """set airing"""
        json_data = self.change_key(
            'airing', airing, self.get_anime_settings())
        self.set_anime_settings(json_data)

    def get_watching(self):
        """return watching"""
        return self.get_value('watching', self.get_anime_settings())

    def set_watching(self, watching):
        """set watching"""
        json_data = self.change_key(
            'watching', watching, self.get_anime_settings())
        self.set_anime_settings(json_data)

    def get_all_anime(self):
        """return all animes"""
        return self.get_value('all', self.get_anime_settings())

    def set_all_anime(self, all_anime):
        """set all animes"""
        self.set_anime_settings(self.change_key(
            'all', all_anime, self.get_anime_settings))

    def update(self):
        self.set_airing(showparser.get_airing_shows())
        self.set_all_anime(showparser.get_all_shows())
        self.set_modified_date(datetime.now())
        self.save()

    def get_modified_date(self):
        """return date"""
        return datetime.strptime(self.get_value('modified_date', self.get_anime_settings()), "%Y-%m-%dT%H:%M:%S.%f")

    def set_modified_date(self, modified_date):
        """set date"""
        self.set_anime_settings(self.change_key(
            "modified_date", modified_date, self.get_anime_settings()))

    def update_modified_date(self):
        """update date to current date"""
        self.set_anime_settings(self.change_key(
            "modified_date", datetime.now(), self.get_anime_settings()))
