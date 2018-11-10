"""test suite for set_api_url.py."""

import unittest
import sys
import os
sys.path.append("..")
import set_api_url
import logging
import misc_utils.unittest_extend as ute

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestSetAPIUrl(unittest.TestCase):
    """Test suite for set_api_url.py."""

    def test_set_api_url(self):
        """Returns NOne. Tests replacement of api url on test .js files."""
        UI_path = './resources/'
        test_js_filename = 'test_main.js'
        new_js_filename = UI_path + 'main_blabla.js'
        reference_js = UI_path + 'test_main_reference.js'

        os.system('cp {} {}'.format(
            UI_path + test_js_filename,
            new_js_filename))

        api_url = 'https://app.etabot.ai:8000/api/'
        set_api_url.set_api_url(
            UI_path, api_url, api_url_var_name='apiUrl')

        ute.assertFileEqual(new_js_filename, reference_js, self)
        os.remove(new_js_filename)

unittest.main()
