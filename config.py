"""all constants in one file"""
import os
import json
from datetime import date, datetime
import showparser


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (dict)):
        return obj
    raise TypeError("Type %s not serializable" % type(obj))


class JsonLoader():
    """Wrapper-class for json config file"""
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.json_data = self.load()
        self.modified_date = self.get_modified_date()
        self.base_url = self.get_base_url()

    def load(self):
        """load json from file"""
        if not os.path.isfile(self.CONFIG_FILE):
            self.create_config()
        with open(self.CONFIG_FILE, 'r') as config:
            return json.load(config, object_hook=json_serial)

    def save(self):
        """save changes and reload"""
        self.write_json_to_file(self.json_data)
        self.json_reload()

    def create_config(self, watching=""):
        self.json_data = {"animes": {}, "irc": {}}
        animes = {"watching": watching, "airing": showparser.get_airing_shows(),
                  "all": showparser.get_all_shows(), "anime_folder": "G:/summer"}
        irc = {"host": "irc.rizon.net", "port": 6667,
               "channel": "#horriblesubs", "user": "engeleatosbot2",
               "default_bot": "CR-RALEIGH|NEW", "default_res": "720p"}
        self.json_data["animes"] = animes
        self.json_data["irc"] = irc
        self.json_data["base_url"] = "http://horriblesubs.info"
        self.json_data["modified_date"] = datetime.now()
        self.save()

    def json_reload(self):
        """reload constant"""
        self.json_data = self.load()

    def set_json_data(self, json_data):
        """set constant"""
        self.json_data = json_data
        self.save()

    def get_json_data(self):
        """return json_data"""
        return self.json_data

    def write_json_to_file(self, data):
        """write json to file"""
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False,
                      default=json_serial, indent=4, sort_keys=True)

    def change_key(self, key, value, json_data=None):
        """change value of key in json"""
        json_data = self.check_loaded() if json_data is None else json_data
        if key in json_data:
            json_data[key] = value
            return json_data
        raise KeyError("KeyError: %s is not a key in the dictionary." % key)

    def get_value(self, key, json_data=None):
        """get value by key"""
        json_data = self.check_loaded() if json_data is None else json_data
        if key in json_data:
            return json_data[key]
        raise KeyError("KeyError: %s is not a key in the dictionary." % key)

    def check_loaded(self):
        """check if JSON_DATA is loaded else load"""
        return self.json_data if self.json_data else self.json_reload()

    def get_base_url(self):
        """return base_url"""
        return self.get_value('base_url')

    def set_base_url(self, base_url):
        """set base_url"""
        self.set_json_data(self.change_key("base_url", base_url))

    def get_modified_date(self):
        """return date"""
        return datetime.strptime(self.get_value('modified_date'), "%Y-%m-%dT%H:%M:%S.%f")

    def set_modified_date(self, modified_date):
        """set date"""
        self.set_json_data(self.change_key("modified_date", modified_date))

    def update_modified_date(self):
        """update date to current date"""
        self.set_json_data(self.change_key("modified_date", datetime.now()))


class IrcSettingsLoader(JsonLoader):
    """Wrapper-class for IRC-settings"""

    def __init__(self):
        self.json_data = self.load()
        self.host = self.get_host()
        self.port = self.get_port()
        self.channel = self.get_channel()
        self.user = self.get_user()
        self.default_bot = self.get_default_bot()
        self.default_res = self.get_default_res()

    def get_irc_settings(self):
        """return irc_settings"""
        return self.get_value('irc')

    def set_irc_settings(self, irc_settings):
        """set irc_settings"""
        self.set_json_data(self.change_key('irc', irc_settings))

    def get_host(self):
        """return host"""
        return self.get_value('host', self.get_irc_settings())

    def set_host(self, host):
        """set host"""
        json_data = self.change_key('host', host, self.get_irc_settings())
        self.set_irc_settings(json_data)

    def get_port(self):
        """return port"""
        return self.get_value('port', self.get_irc_settings())

    def set_port(self, port):
        """set port"""
        json_data = self.change_key('port', port, self.get_irc_settings())
        self.set_irc_settings(json_data)

    def get_channel(self):
        """return channel"""
        return self.get_value('channel', self.get_irc_settings())

    def set_channel(self, channel):
        """set channel"""
        json_data = self.change_key(
            'channel', channel, self.get_irc_settings())
        self.set_irc_settings(json_data)

    def get_user(self):
        """return user"""
        return self.get_value('user', self.get_irc_settings())

    def set_user(self, user):
        """set user"""
        json_data = self.change_key('user', user, self.get_irc_settings())
        self.set_irc_settings(json_data)

    def get_default_bot(self):
        """return default_bot"""
        return self.get_value('default_bot', self.get_irc_settings())

    def set_default_bot(self, default_bot):
        """set default_bot"""
        json_data = self.change_key('default_bot', default_bot,
                                    self.get_irc_settings())
        self.set_irc_settings(json_data)

    def get_default_res(self):
        """return default_res"""
        return self.get_value('default_res', self.get_irc_settings())

    def set_default_res(self, default_res):
        """set default_res"""
        json_data = self.change_key('default_res', default_res,
                                    self.get_irc_settings())
        self.set_irc_settings(json_data)


class AnimeSettingsLoader(JsonLoader):
    """Wrapper-class for anime-settings"""

    def __init__(self):
        self.json_data = self.load()
        self.airing = self.get_airing()
        self.watching = self.get_watching()
        self.all = self.get_all_anime()

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

    def get_anime_folder(self):
        """return anime_folder"""
        return self.get_value('anime_folder', self.get_anime_settings())

    def set_anime_folder(self, anime_folder):
        """set anime_folder"""
        self.set_anime_settings(change_key("anime_folder", anime_folder,
                                           self.get_anime_settings()))

    def update(self):
        self.set_airing(showparser.get_airing_shows())
        self.set_all_anime(showparser.get_all_shows())
        self.set_modified_date(datetime.now())
        self.save()
