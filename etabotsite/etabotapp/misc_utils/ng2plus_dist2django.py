"""ng2plus_dist2django.py

Purpose: deploys Angular2+ built files to Django server:
        copies built static html/js/css files from
        angular 2+ build destination folder to
        Django static and templates folder.

        index.html is converted to Django template to
        load static files properly

Author: Alex Radnaev

date created: 2018-05-27

Copyright (C) 2018 Alex Radnaev
"""

import misc_utils.django_indexhtml_mod as django_indexhtml_mod
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def deploy_ng2plus(
        source_dir,
        django_static_dir,
        django_template_path,
        django_angular_static_subpath):
    """source_dir - path from where all files are copied using cp
    django_static_dir - path to where all files except index.html are copied
    django_template_path - path to where modified index.html is placed
    django_angular_static_subpath - location of angular files
        with respect to Django static dir (e.g. 'ng_app/')"""
    results = []
    ui_target_dir = django_static_dir + '/' + django_angular_static_subpath
    results.append(os.system("rm -rf {}".format(ui_target_dir)))
    results.append(os.system("mkdir {}".format(ui_target_dir)))
    results.append(os.system("cp -rf {} {}".format(
        source_dir, ui_target_dir)))
    logging.info('copy ng built dist result: {}'.format(results[-1]))

    indexhtml_src = ui_target_dir + '/index.html'
    django_indexhtml_mod.html_to_django_template(
        indexhtml_src,
        django_template_path + '/index.html',
        django_angular_static_subpath)

    results.append(os.remove(indexhtml_src))
    logging.info('adding to git repo')
    results.append(os.system("git add {}".format(ui_target_dir)))
    logging.info('results log: {}'.format(results))
    logging.info('deploy_ng2plus is done')
