# -*- coding: utf-8 -*-

from invoke import task
import json
from string import Template

db_init_prod_path = "db_prod_init.js"
db_init_template_path = "templates/db_init.template.js"
db_template_vars_path = "templates/db_init.vars.json"

mongo_host = "localhost"
mongo_port = 27017


@task
def test_api(ctx):
    ctx.run('coverage run --source=instabotpatrik/  -m unittest discover -v -s ./testsIntegrationAPI/ -p "test_*.py"')


@task
def test_db(ctx):
    ctx.run('coverage run --source=instabotpatrik/  -m unittest discover -v -s ./testsIntegrationDB/ -p "test_*.py"')


@task
def test_unit(ctx):
    ctx.run('coverage run --source=instabotpatrik/  -m unittest discover -v -s ./testsUnit/ -p "test_*.py"')


@task
def test_local(ctx):
    ctx.run('coverage run --source=instabotpatrik/  -m unittest discover -v -s ./testsUnit/ -p "test_*.py"')
    ctx.run('coverage run --append --source=instabotpatrik/  '
            '-m unittest discover -v -s ./testsIntegrationDB/ -p "test_*.py"')


@task
def test_all(ctx):
    ctx.run('coverage run --source=instabotpatrik/  -m unittest discover -v -s ./testsUnit/ -p "test_*.py"')
    ctx.run('coverage run --append --source=instabotpatrik/  '
            '-m unittest discover -v -s ./testsIntegrationDB/ -p "test_*.py"')
    ctx.run('coverage run --append --source=instabotpatrik/ '
            '-m unittest discover -v -s ./testsIntegrationAPI/ -p "test_*.py"')


@task
def generate_coverage_report(ctx):
    ctx.run('coverage html')


@task(pre=[generate_coverage_report])
def show_coverage(ctx):
    ctx.run('open htmlcov/index.html')


def generate_db_init_prod():
    var_dict = _get_env_config('prod')
    interpolate_template(db_init_template_path, var_dict, db_init_prod_path)


def _get_env_config(env_name):
    with open(db_template_vars_path, 'r') as var_file:
        json_data = json.loads(var_file.read())
    return json_data[env_name]


@task
def generate_db_init(ctx):
    generate_db_init_prod()


@task
def init_db(ctx):
    ctx.run("mongo -host '%s' -port %d '%s'" % (mongo_host, mongo_port, db_init_prod_path))


@task
def clean(ctx):
    ctx.run("rm '%s'" % db_init_prod_path)


@task
def clean_db(ctx):
    mongo_drop_script = 'db = db.getSiblingDB("instabot"); db.dropDatabase()'
    command = "mongo - -host '%s' -port %d --eval '%s'" % (mongo_host, mongo_port, mongo_drop_script)
    print(command)
    print("Do you really want to drop production database on %s %d\n (y/n)?" % (mongo_host, mongo_port))
    if is_confirmed():
        ctx.run(command)


def is_confirmed():
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        print("Please respond with 'yes' or 'no'")


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
