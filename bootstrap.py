#!/usr/bin/env bash

import argparse
import instabotpatrik

parser = argparse.ArgumentParser(description='Instagram follow/unfollow/like automation')
argparse.parser.add_argument('--config-file', default="dev.ini", help='Path to configuration file')
args = vars(parser.parse_args())

instabotpatrik.runner.BasicSetup(config_path=args['config-file'])
