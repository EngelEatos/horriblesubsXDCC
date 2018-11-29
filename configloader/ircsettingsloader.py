"""loader for irc settings"""
from configloader.jsonloader import JsonLoader


class IrcSettingsLoader(JsonLoader):
    """Wrapper-class for IRC-settings"""
    config_file = "settings/irc.json"

    def __init__(self):
        self.json_data = self.load()

    def create_config(self):
        self.json_data = {"irc":
                          {"host": "irc.rizon.net", "port": 6667, "channel": "#horriblesubs",
                           "user": "bot123", "default_bot": "CR-RALEIGH|NEW",
                           "default_res": "720p", "anime_folder": "/mnt/media/airing/",
                           "multiprocessing": 0}}
        self.save()

    def get_irc_settings(self):
        """return irc_settings"""
        return self.get_value('irc')

    def set_irc_settings(self, irc_settings):
        """set irc_settings"""
        self.set_json_data(self.change_key('irc', irc_settings))

    def get_serverinfo(self):
        """return serverinfo"""
        return self.get_irc_settings()

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

    def get_anime_folder(self):
        """return anime_folder"""
        return self.get_value('anime_folder', self.get_irc_settings())

    def set_anime_folder(self, anime_folder):
        """set anime_folder"""
        self.set_irc_settings(self.change_key(
            'anime_folder', anime_folder, self.get_irc_settings()))

    def get_multiprocessing(self):
        """return bool multiprocessing"""
        return self.get_value('multiprocessing', self.get_irc_settings())

    def set_multiprocessing(self, bool_multiprocessing):
        """set bool multiprocessing"""
        self.set_irc_settings(self.change_key(
            'multiprocessing', bool_multiprocessing, self.get_irc_settings()))
