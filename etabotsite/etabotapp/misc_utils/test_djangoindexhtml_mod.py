import unittest
import logging
import django_indexhtml_mod

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class TestDjangoIndexHTMLmod(unittest.TestCase):
	def test_html_to_django_template(self):
		src_html = 'test_index.html'
		target_html = 'test_index_modified.html'
		reference_html = 'test_index_django_template.html'

		django_indexhtml_mod.html_to_django_template(
			src_html,
			target_html,
			'ng_app_js/')

		with open(target_html) as f:
			t = f.readlines()

		with open(reference_html) as f:
			r = f.readlines()

		self.assertEqual(r, t)
unittest.main()