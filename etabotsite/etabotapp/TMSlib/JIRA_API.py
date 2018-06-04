"""
    JIRA API access module
    supports storing encrypted JIRA password locally and decrypting
    using key in the macOS key chain

    Author: Alex Radnaev (alexander.radnaev@gmail.com)

    Status: Prortotype

    Python Version: 3.6
"""
import logging
from Crypto.Cipher import AES
from jira import JIRA
from jira.client import GreenHopper

from inspect import getsourcefile
import os.path
import sys
current_path = os.path.abspath(getsourcefile(lambda: 0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[:current_dir.rfind(os.path.sep)]
sys.path.insert(0, parent_dir)

from passwords.encrypted_passwords import passwords_dict
import keyring

encryption_key_name = 'Jtest1'


class JIRA_wrapper():
    # handles communication with JIRA API
    def __init__(self, server, username, password=None):
        self.gh = None
        self.jira = self.JIRA_connect(server, username, password=password)
        self.username = username
        self.max_results_jira_api = 50

    def JIRA_connect(self, server, username, password=None):
        options = {'server': server}

        if password is None:
            print('getting password stored locally')
            # try to get password stored locally
            if server not in passwords_dict:
                raise NameError('Server {} is not known'.format(server))
            if username not in passwords_dict[server]:
                raise NameError('User {} is not known'.format(username))

            encrypted_password = passwords_dict[server][username]
            # password = input('enter password\n')
            obj2 = AES.new(
                keyring.get_password('system', encryption_key_name)[:16],
                AES.MODE_CBC,
                'This is an IV456')
            password = obj2.decrypt(encrypted_password)
            password = str(password, 'utf-8').replace(' ', '')

        logging.info('authenticating with JIRA ({}, {})...'.format(
            username, options.get('server', 'unkown server')))

        try:
            logging.info('"{}" connecting to JIRA with options:'.format(
                username, options))
            jira = JIRA(basic_auth=(username, password), options=options)
            print('authenticated. ')
        except Exception as e:
            raise NameError('JIRA error: {}'.format(e))
        return jira

    def GreenHopper_connect(self, username, password, options):
        print('authenticating with JIRA Greenhopper...')
        gh = GreenHopper(basic_auth=(username, password), options=options)
        print('authenticated with GreenHopper. ')
        return gh

    def get_jira_issues(self, search_string, get_all=True):
        # get jira issues using the search_string
        returned_result_length = 50
        jira_issues = []
        while get_all and returned_result_length == self.max_results_jira_api:
            jira_issues_batch = self.jira.search_issues(
                search_string,
                maxResults=self.max_results_jira_api,
                startAt=len(jira_issues),
                expand='changelog')

            if returned_result_length > self.max_results_jira_api:
                raise NameError(
                    'JIRA API problem: returned more results {} \
                    than max = {}'.format(
                        returned_result_length, self.max_results_jira_api))
            returned_result_length = len(jira_issues_batch)
            jira_issues += jira_issues_batch

        print('{}: got {} issues'.format(search_string, len(jira_issues)))
        return jira_issues
