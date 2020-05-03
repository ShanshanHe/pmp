"""test suite for set_api_url.py."""

import unittest
import sys
import os
import logging
import etabotapp.misc_utils.unittest_extend as ute
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestSetAPIUrl(unittest.TestCase):
    """Test suite for set_api_url.py."""

    def test_set_api_url(self):
        """Returns NOne. Tests replacement of api url on test .js files."""
        logging.info('current dir: {}'.format(os.getcwd()))
        UI_path = './etabotapp/tests/resources/'
        test_js_filename = 'input_for_test.js'
        new_js_filename = UI_path + 'main_modified.js'
        reference_js = UI_path + 'reference_test_main.js'

        res = os.system('cp {} {}'.format(
            UI_path + test_js_filename,
            new_js_filename))
        logging.info('copy result: {}'.format(res))

        api_url = 'https://app.etabot.ai:8000/api/'

        byteOutput = subprocess.check_output(
            ['python', 'set_api_url.py', UI_path.replace('/etabotapp', ''), api_url],
            cwd='etabotapp/')
        print(byteOutput)
        logging.info(byteOutput.decode('UTF-8'))

        ute.assertFileEqual(new_js_filename, reference_js, self)
        os.remove(new_js_filename)

# unittest.main()
