#!/usr/bin/env
# -*- coding: utf-8 -*-

import json
from string import Template


def interpolate_template(template_file_path, interpolation_dictionary, destination_path):
    """
    :param template_file_path:
    :param interpolation_dictionary:
    :type interpolation_dictionary: dict
    :param destination_path:
    :return:
    """
    dict = {}
    for k, v in interpolation_dictionary.items():
        if isinstance(v, list):
            dict[k] = '["%s"]' % '","'.join(v)
        else:
            dict[k] = v

    print("going to interpolate file %s to target file %s" % (template_file_path, destination_path))
    with open(template_file_path, 'r') as myfile:
        interpolated = Template(myfile.read()).substitute(dict)
    destination_file = open(destination_path, 'w', encoding='utf8')
    destination_file.write(interpolated)
    destination_file.close()


if __name__ == '__main__':
    # interpolation_vars = {"db_name": "instabot",
    #                       "collection_media_name": "media",
    #                       "collection_users_name": "users",
    #                       "collection_config_name": "config",
    #                       "tag_list": ['praha', 'tagsareawesome']
    #                       }
    with open('db_init_vars.json', 'r') as var_file:
        json_data = json.loads(var_file.read())
    prod_vars = json_data['prod']
    test_vars = json_data['test']
    interpolate_template("db_init.template.js", prod_vars, "db_prod_init.js")
    interpolate_template("db_init.template.js", test_vars, "testsIntegrationDB/db_test_init.js")
