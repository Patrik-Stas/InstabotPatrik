# -*- coding: utf-8 -*-

from invoke import task
import json
from string import Template


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


@task()
def generate_db_init_e2e(ctx, template_file):
    f_generate_db_init(template_file=template_file,
                       var_file="testse2e/dbinit_e2e.vars.json",
                       target_file="testse2e/db_e2e_init.js")


@task()
def generate_db_init(ctx, template_file, var_file, target_file):
    f_generate_db_init(template_file=template_file,
                       var_file=var_file,
                       target_file=target_file)


def f_generate_db_init(template_file, var_file, target_file):
    """
    :param ctx: invoke framework context
    :param template_file: path to DB-initialization template file
    :param var_file:  path to file with variable to be interpolated in template file
    :param target_file: path to file to which the interpolated template should be rendered
    :return:
    """
    print("will generate %s %s %s" % (template_file, var_file, target_file))
    with open(var_file, 'r') as f:
        json_data = json.loads(f.read())
    interpolate_template(template_file_path=template_file,
                         interpolation_dictionary=json_data["db_init_root"],
                         destination_path=target_file)


@task
def clean_db(ctx, mongo_host, mongo_port):
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
