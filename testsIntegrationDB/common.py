from testsUnit.context import instabotpatrik
import os


def get_path_to_file_in_directory_of_this_file(file_name):
    this_directory_absolute = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(this_directory_absolute, file_name)


def get_config():
    return instabotpatrik.config.Config(config_path=get_path_to_file_in_directory_of_this_file("test.ini"))


def create_repo(config, mongo_client):
    return instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=mongo_client,
                                                          database_name=config.get_db_name(),
                                                          users_collection_name=config.get_collection_users_name(),
                                                          media_collection_name=config.get_collection_media_name())
