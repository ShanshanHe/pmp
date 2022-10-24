"""Purpose: tests django_indexhtml_mod.py.

Uses reference django template

Author: Alex Radnaev

date created: 2018-05-27

Copyright (C) 2018 Alex Radnaev
"""

import unittest
import logging
import os
import sys
# sys.path.append("..")
import etabotapp.misc_utils.django_indexhtml_mod as djhtml_mod
import etabotapp.misc_utils.unittest_extend as ute

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class TestDjangoIndexHTMLmod(unittest.TestCase):

    work_dir = './etabotapp/tests/resources/'

    def test_html_to_django_template(self):
        logging.info('current dir: {}'.format(os.getcwd()))            
        src_html = self.work_dir + 'index_test.html'
        target_html = self.work_dir + 'index_modified.html'
        reference_html = self.work_dir + 'index_django_template_test.html'

        djhtml_mod.html_to_django_template(
            src_html,
            target_html,
            'ng_app_js/')
        ute.assertFileEqual(target_html, reference_html, self)
        os.remove(target_html)
# unittest.main()
