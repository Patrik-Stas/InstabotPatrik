#!/usr/bin/env python

import argparse
import instabotpatrik
import os

parser = argparse.ArgumentParser(description='Instagram follow/unfollow/like automation')
parser.add_argument('--config', help='Path to configuration file', required=True)

args = vars(parser.parse_args())
config_path = args['config']
if not os.path.isabs(config_path):  # if path is relative, then build it from <cwd>/<relative path>
    config_path = os.path.join(os.getcwd(), config_path)

bot_runner = instabotpatrik.runner.BasicSetup(config_path=config_path)

bot_runner.run()
