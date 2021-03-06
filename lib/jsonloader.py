"""all constants in one file"""
import json
import os
from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (dict)):
        return obj
    raise TypeError("Type %s not serializable" % type(obj))


class JsonLoader():
    """Wrapper-class for json config file"""
    config_file = ""
    json_data = ""

    def load(self):
        """load json from file"""
        if not os.path.isfile(self.config_file):
            self.create_config()
        with open(self.config_file, 'r', encoding='utf-8') as config:
            return json.load(config, object_hook=json_serial)

    def is_loaded(self):
        """return bool if json_data is available"""
        return self.json_data != None

    def create_config(self):
        """gets overwritten"""
        return self.json_data

    def save(self):
        """save changes and reload"""
        self.write_json_to_file(self.json_data)
        self.json_reload()

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
        if not os.path.isdir(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))
        with open(self.config_file, 'w', encoding='utf-8') as outfile:
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
