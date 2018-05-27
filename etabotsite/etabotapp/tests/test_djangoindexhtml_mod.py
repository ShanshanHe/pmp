"""
purpose: tests django_indexhtml_mod.py using 
         reference django template

Author: Alex Radnaev

date created: 2018-05-27

Copyright (C) 2018 Alex Radnaev

"""

import unittest
import logging
import os
import sys
sys.path.append("..")
import misc_utils.django_indexhtml_mod as djhtml_mod

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class TestDjangoIndexHTMLmod(unittest.TestCase):
    work_dir = 'resources/'
    def test_html_to_django_template(self):
        src_html = self.work_dir + 'test_index.html'
        target_html = self.work_dir + 'test_index_modified.html'
        reference_html = self.work_dir + 'test_index_django_template.html'

        djhtml_mod.html_to_django_template(
            src_html,
            target_html,
            'ng_app_js/')

        with open(target_html) as f:
            t = f.readlines()
        os.remove(target_html)

        with open(reference_html) as f:
            r = f.readlines()

        self.assertEqual(r, t)

unittest.main()
