"""load config"""
import os
import json
from shutil import copyfile

from datetime import date, datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (dict)):
        return obj
    raise TypeError("Type %s not serializable" % type(obj))

class configloader():
    config_file = "settings/config.json"
    def __init__(self):
        self.config_data = self.load()
    
    def create_config(self):
        if not os.path.isfile("settings/config.example.json"):
            print("couldn't find config and example config. exiting")
            exit(1)
        copyfile("settings/config.example.json", self.config_file)
    
    def load(self):
        if not os.path.isfile(self.config_file):
            self.create_config()
        with open(self.config_file, 'r', encoding='utf-8') as jfile:
            return json.load(jfile, object_hook=json_serial)
    
    def save(self):
        self.write_json_to_file(self.config_data)
    
    def write_json_to_file(self, data):
        with open(self.config_file, 'w', encoding='utf-8') as ofile:
            json.dump(data, ofile, ensure_ascii=False, default=json_serial, indent=4)
    
    def get_irc(self):
        if self.config_data == None:
            self.load()
        return self.config_data["irc"] if ("irc" in self.config_data) else None
    
    def get_animes(self):
        if self.config_data == None:
            self.load()
        return self.config_data["animes"] if ("animes" in self.config_data) else None
    
    def is_loaded(self):
        return self.config_data != None