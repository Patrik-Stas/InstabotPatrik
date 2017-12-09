import configparser
import logging


class Config:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        logging.info("Config reading values from %s", config_path)
        with open(config_path) as m:
            self.config.read_file(m)

    def get_db_host(self):
        return self.config['database']['db_host']

    def get_db_port(self):
        return self.config.getint('database', 'db_port')

    def get_db_name(self):
        return self.config['database']['db_name']

    def get_collection_users_name(self):
        return self.config['database']['db_collection_users']

    def get_collection_media_name(self):
        return self.config['database']['db_collection_media']

    def get_collection_config_name(self):
        return self.config['database']['db_collection_config']

# example of config:
# database:
#   host: 'localhost'
#   port: 27017
#   name: "instabot_test"
#   collection_users : "users_test"
#   collection_media : "media_test"
#   collection_config : "config_test"
