"""sets api url in UI.

author: Alex Radnaev

usage:

python set_api_url.py UI_path api_url
python set_api_url.py static/ng2_app https://0.0.0.0:8000/api/
"""
import sys
import re
import os
import misc_utils.file_tools as ft
import logging


def set_api_url(UI_path, api_url, api_url_var_name='apiUrl'):
    """Return None. Replaces api_url_var_name value with api_url."""
    pattern = r'({}:\")(.*?)(\")'.format(api_url_var_name)
    logging.info('pattern: "{}"'.format(pattern))
    for filename in ft.find_all_recursively('main*.js', UI_path):
        logging.info('modifying file "{}"'.format(filename))

        with open(filename) as f:
            s = '\n'.join((f.readlines()))

        logging.info('found apiUrls: "{}"'.format(re.findall(pattern, s)))

        s = re.sub(pattern,
                   r'\1{}\3'.format(api_url),
                   s)

        with open(filename, 'w+') as f:
            f.write(s)

        logging.info('modified file {} saved'.format(filename))

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    print(set_api_url.__doc__)
    if len(sys.argv) < 3:
        raise NameError('need at least two arguments, e.g.:\n\
python set_api_url.py UI_path api_url')

    UI_path = sys.argv[1]
    api_url = sys.argv[2]

    if len(sys.argv) > 3:
        api_url_var_name = sys.argv[3]
        set_api_url(UI_path, api_url, api_url_var_name)
    else:
        set_api_url(UI_path, api_url)
