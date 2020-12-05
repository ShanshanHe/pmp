"""
    JIRA API access module
    supports storing encrypted JIRA password locally and decrypting
    using key in the macOS key chain

    Author: Alex Radnaev (alexander.radnaev@gmail.com)

    Status: Prortotype

    Python Version: 3.6
"""
import threading
import logging
import etabotapp.TMSlib.Atlassian_API as Atlassian_API
from Crypto.Cipher import AES
from jira import JIRA

JIRA_TIMEOUT_FOR_PASSWORD_SECONDS = 10.
JIRA_TIMEOUT_FOR_OAUTH2_SECONDS = 30.
JIRA_CLOUD_API = Atlassian_API.ATLASSIAN_CLOUD_BASE + "ex/jira/"
logging.info('JIRA_CLOUD_API: {}'.format(JIRA_CLOUD_API))


class JIRA_wrapper():
    """Handles communication with JIRA API."""

    def __init__(
            self,
            server,
            username,
            password=None,
            TMSconfig=None):
        """Create JIRA_wrapper object for JIRA API communication.

        Arguments:

        server - URL to JIRA server
        username - JIRA username (not used for OAuth2.0 (password==None, token not None)
        password - JIRA password or API key (not needed if OAuth2.0 token is passed
        TMSconfig - TMS django model (not needed if password is passed)
        """
        self.username = username
        self.max_results_jira_api = 50
        self.TMSconfig = TMSconfig
        self.jira = self.JIRA_connect(
            server, username, password=password)

    def JIRA_connect(
            self,
            server,
            username,
            password=None):
        """Connect to jira api."""
        if password is not None:
            auth_method = 'password'
            jira_timout_seconds = JIRA_TIMEOUT_FOR_PASSWORD_SECONDS
        elif self.TMSconfig is not None and self.TMSconfig.oauth2_token is not None:
            auth_method = 'oauth2'
            jira_timout_seconds = JIRA_TIMEOUT_FOR_OAUTH2_SECONDS
        else:
            raise NameError('JIRA API key or TMSconfig with token must be provided')

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
                    if auth_method=='password':
                        logging.debug('using basic auth with password')
                        jira = JIRA(
                            basic_auth=(username, password),
                            options=options)
                    else:
                        token = self.TMSconfig.get_fresh_token()
                        options['headers'] = {
                            'Authorization': 'Bearer {}'.format(token.access_token),
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'}
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

    def get_team_members(self, project, get_all=True, time_frame=365):
        """This function will gather all the team members in a given time range.
        Default is one 1 year.
        TODO: one issue at a time search request to mitigate max results limitation:
            search assignee != None limit = 1 -> assignees.append(new_assignee)
            repeat until no results: search assignee != None limit = 1 and assignee not in {assignees}

        TODO: extract 'emailAddress'
        """
        # Error Checking
        if time_frame < 0:
            time_frame = 365

        search_string = 'project={project} AND \
            (created > -{timeFrame}d and created < now()) \
            AND assignee IS NOT EMPTY \
            ORDER BY assignee'.format(project=project, timeFrame=time_frame)

        jira_issues = self.get_jira_issues(search_string)

        # Gather Team members and create a dictionary using accountId as
        # key. accountId is unique, so we avoid same displayName issues.
        team_members = {}
        for jira_issue in jira_issues:
            item = jira_issue.raw
            account_id = item['fields']['assignee']['accountId']
            if account_id not in team_members:
                logging.debug(item['fields']['assignee'])
                display_name = item['fields']['assignee']['displayName']
                team_members[account_id] = display_name

        return team_members
