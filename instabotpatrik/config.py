import configparser
import logging


class Config:
    def __init__(self, config_path):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = configparser.ConfigParser()
        self.logger.info("Config reading values from %s", config_path)
        with open(config_path) as m:
            self.config.read_file(m)

    def get_db_host(self):
        return self.config['database']['db_host']

    def get_db_port(self):
        return self.config.getint('database', 'db_port')

    def get_db_name(self):
        return self.config['database']['db_name']

    def collection_users_name(self):
        return self.config['database']['db_collection_users']

    def collection_media_name(self):
        return self.config['database']['db_collection_media']

    def collection_config_name(self):
        return self.config['database']['db_collection_config']

    def get_instagram_username(self):
        return self.config['instagram']['username']

    def get_instagram_password(self):
        return self.config['instagram']['password']
