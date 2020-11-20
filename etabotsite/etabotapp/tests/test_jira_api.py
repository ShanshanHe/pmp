"""Test JIRA API.

TODO: FakeToken({"need_to_setup":"shared_token_pull"}
"""

import logging
logging.debug('loading jira api test')
import etabotapp.TMSlib.JIRA_API as JIRA_API
from django.test import TestCase
from django.conf import settings



logging.debug('imports done')
test_tms_data = getattr(settings, "TEST_TMS_DATA", {})


class FakeToken():
    """Simulate Django token class."""

    def __init__(self, token_dict):
        self.__dict__ = token_dict

    def to_token(self):
        return self.__dict__

class TestJIRAwrapper(TestCase):
    """Test JIRA wrapper connectivity."""

    def setUp(self):
        self.jira = None
        self.server_end_point = 'https://api.atlassian.com/ex/jira/d1083787-4491-40c9-9581-8625f52baf7e'
        self.username_login = test_tms_data['username']
        logging.debug('creating fake token')
        self.token = FakeToken({"need_to_setup":"shared_token_pull", "access_token": 1})
        logging.debug('created fake token with access token:')
        logging.debug(self.token.access_token)

    def test_token_connectivity(self):
        logging.debug("testing JIRA_wrapper")
        if self.token.access_token is not None:
            self.jira_wrapper = JIRA_API.JIRA_wrapper(
                self.server_end_point,
                self.username_login,
                password=test_tms_data['password'],
                TMSconfig=None)
            logging.debug('connect_to_TMS jira object: {}'.format(self.jira))
            jira = self.jira_wrapper.jira
            search_string = 'assignee=currentUser() ORDER BY Rank ASC'
            logging.debug('test jira query with search string: {}'.format(search_string))
            res =jira.search_issues(search_string)
            issue = res[0]
            logging.info(issue)
            jira.add_comment(issue, "Django test_jira_api")
        else:
            logging.warning('no access token to test JIRA OAuth')

logging.debug('loaded jira api test')
