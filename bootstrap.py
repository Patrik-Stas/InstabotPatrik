#!/usr/bin/env python

import argparse
import instabotpatrik
import os
import logging
import logging.config
import yaml


def load_logging_config_from_yaml(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            return yaml.safe_load(f.read())
    else:
        raise Exception("Can't locate logging configuration file.")


parser = argparse.ArgumentParser(description='Instagram follow/unfollow/like automation')

parser.add_argument('--appconfig', help='Path to application configuration .ini file', required=True)
parser.add_argument('--logconfig', help='Path to logging configuration .yaml file', required=True)
parser.add_argument('--logfile', help='Path to target output log file', required=True)


args = vars(parser.parse_args())

app_config_path = args['appconfig']
log_config_path = args['logconfig']
output_llogfile_path = args['logfile']
if not os.path.isabs(app_config_path):  # if path is relative, then build it from <cwd>/<relative path>
    app_config_path = os.path.join(os.getcwd(), app_config_path)
if not os.path.isabs(app_config_path):  # if path is relative, then build it from <cwd>/<relative path>
    log_config_path = os.path.join(os.getcwd(), log_config_path)

logging_cfg_dict = load_logging_config_from_yaml(log_config_path)
logging_cfg_dict['handlers']['daily_file_handler']['filename'] = output_llogfile_path
logging.config.dictConfig(logging_cfg_dict)

# logging.getLogger().setLevel(10)
# logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
#                     datefmt='%m/%d/%Y-%H:%M:%S')

logger = logging.getLogger(__name__)
logger.info("[BOOTSTRAP] Parsing arguments...")

logger.info("[BOOTSTRAP] Bootstrapping bot from configuration file %s" % app_config_path)
config = instabotpatrik.config.Config(app_config_path)
bot_runner = instabotpatrik.runner.BasicSetup(cfg=config)

bot_runner.run()
