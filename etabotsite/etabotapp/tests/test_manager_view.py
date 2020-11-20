"""Test JIRA gather get_team_members."""
import logging
logging.debug('loading jira api test')
import etabotapp.TMSlib.JIRA_API as JIRA_API
from django.test import TestCase
from django.conf import settings

test_tms_data = getattr(settings, "TEST_TMS_DATA", {})

class TestJIRAwrapper(TestCase):
    """Test JIRA wrapper connectivity."""

    def setUp(self):
        self.jira = None
        self.server_end_point = '\
            https://api.atlassian.com/ex/jira/d1083787-4491-40c9-9581-8625f52baf7e'
        self.username_login = test_tms_data['username']
        self.token = True

    def test_get_all_team_members(self):
        """Test the get all team members functionality of JIRA API"""
        logging.debug("testing JIRA_wrapper")
        if self.token is not None:
            self.jira_wrapper = JIRA_API.JIRA_wrapper(
                self.server_end_point,
                self.username_login,
                password=test_tms_data['password'],
                TMSconfig=None)
            logging.debug('connect_to_TMS jira object: {}'.format(self.jira))
            team_members = self.jira_wrapper.get_team_members(
                project="ETAbot-demo",
                time_frame=-1)
            logging.info(team_members)
            self.assertTrue(isinstance(team_members,dict))
        else:
            logging.warning('no access token to test JIRA OAuth')
