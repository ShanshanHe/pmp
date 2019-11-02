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
import threading
# current_path = os.path.abspath(getsourcefile(lambda: 0))
# current_dir = os.path.dirname(current_path)
# parent_dir = current_dir[:current_dir.rfind(os.path.sep)]
# sys.path.insert(0, parent_dir)

# from passwords.encrypted_passwords import passwords_dict
# import keyring
JIRA_CLOUD_BASE = "https://api.atlassian.com/" 
JIRA_CLOUD_API = JIRA_CLOUD_BASE + "ex/jira/"
JIRA_CLOUD_PROFILE = JIRA_CLOUD_BASE + "me"

jira_timout_seconds = 10.


class JIRA_wrapper():
    """Handles communication with JIRA API."""

    def __init__(
            self,
            server,
            username,
            password=None,
            token=None,
            oauth_obj=None):
        """Create JIRA_wrapper object for JIRA API communication.

        Arguments:

        server - URL to JIRA server
        username - JIRA username (not used for OAuth2.0 (password==None, token not None)
        password - JIRA password or API key (not needed if OAuth2.0 token is passed
        token - OAuth2.0 token (not needed if password is passed)
        oauth_obj - authlib oauth object for automatically refreshing token
        """
        self.gh = None
        self.jira = self.JIRA_connect(
            server, username, password=password, token=token)
        self.username = username
        self.max_results_jira_api = 50
        self.oauth_obj=oauth_obj

    def JIRA_connect(
            self,
            server,
            username,
            password=None,
            token=None):

        if password is None and token is None:
            raise NameError('JIRA API key or token must be provided')

        options = {
            'max_retries': 1,
            'server': server}

        logging.debug('authenticating with JIRA ({}, {})...'.format(
            username, options.get('server', 'unkown server')))

        jira = None
        try:
            jira_place = []
            errors_place = {}

            def get_jira_object(target_list, errors_dict):
                logging.info('"{}" connecting to JIRA with options: {}'.format(
                    username, options))
                try:
                    if token is None:
                        logging.debug('token is None, using basic auth with password')
                        jira = JIRA(
                            basic_auth=(username, password),
                            options=options)
                    else:
                        if self.oauth_obj is not None:
                            logging.info('getting user profile to test connection and update token...')
                            res = self.oauth_obj.atlassian.get(JIRA_CLOUD_PROFILE)
                            logging.info(res)
                        options['headers'] = {
                            'Authorization': 'Bearer {}'.format(token)}     
                        logging.debug('connecting with options: {}'.format(options))                      
                        jira = JIRA(options=options)
                        search_string = 'assignee=currentUser() ORDER BY Rank ASC'
                        logging.debug('test jira query with search string: {}'.format(search_string))
                        res =jira.search_issues(search_string) 
                        logging.debug('search result: {}'.format(res))
                        logging.info('found {} issues'.format(len(res)))
                    logging.debug('Authenticated with JIRA. {}'.format(jira))
                    target_list.append(jira)
                except Exception as e:
                    error_message = str(e)
                    logging.debug(error_message)
                    errors_dict['error_message'] = error_message

            auth_thread = threading.Thread(
                target=get_jira_object, args=(jira_place, errors_place))
            auth_thread.start()
            logging.debug('waiting for {} seconds before checking for thread \
status'.format(jira_timout_seconds))
            auth_thread.join(jira_timout_seconds)
            logging.debug('thread join done. checking for thread')
            if auth_thread.isAlive():
                logging.debug('thread is still alive - time out occurred')
                raise Exception('Could not login in a given time - please \
check the team name with credentials and try again')
            else:
                logging.debug('thread is done, getting jira object')
                if len(jira_place) > 0:
                    jira = jira_place[0]
                    logging.debug('jira object acquired: {}. \
Errors: "{}"'.format(jira, errors_place))
                else:
                    logging.debug('no JIRA object passed, rasing error.')
                    raise NameError(errors_place.get(
                        'error_message',
                        'Unknown error while authenticating with JIRA'))

        except Exception as e:
            raise NameError('JIRA error: {}'.format(e))
        return jira


    def get_jira_issues(self, search_string, get_all=True):
        # Return list of jira issues using the search_string.
        logging.debug('jira search_string = "{}"'.format(search_string))
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
