#!/usr/bin/env python

import argparse
import instabotpatrik
import os
import logging

print("[BOOTSTRAP] Setting up logging...")
logging.getLogger().setLevel(20)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%m/%d/%Y-%H:%M:%S')

parser = argparse.ArgumentParser(description='Instagram follow/unfollow/like automation')
parser.add_argument('--config', help='Path to configuration file', required=True)

logging.info("[BOOTSTRAP] Parsing arguments...")
args = vars(parser.parse_args())
config_path = args['config']
if not os.path.isabs(config_path):  # if path is relative, then build it from <cwd>/<relative path>
    config_path = os.path.join(os.getcwd(), config_path)

logging.info("[BOOTSTRAP] Bootstrapping bot from configuration file %s" % config_path)
config = instabotpatrik.config.Config(config_path)
bot_runner = instabotpatrik.runner.BasicSetup(cfg=config)

bot_runner.run()
