"""Atlassian API helper functions."""

import requests

ATLASSIAN_CLOUD_BASE = "https://api.atlassian.com/" 
ATLASSIAN_CLOUD_PROFILE = ATLASSIAN_CLOUD_BASE + "me"


class AtlassianAPI:
    def __init__(self, token):
        self.token = token
        self.accessible_resources_api = \
            "https://api.atlassian.com/oauth/token/accessible-resources"

    def default_headers(self):
        return {
            'Authorization': 'Bearer {}'.format(self.token.access_token),
            'Accept': 'application/json'
        }

    @staticmethod
    def mock_get_accessible_resources(self):
        return [{
            "id": "d1083787-4491-40c9-9581-8625f52baf7e",
            "url": "https://etabot.atlassian.net",
            "name": "etabot",
            "scopes": ["write:jira-work", "read:jira-work", "read:jira-user"],
            "avatarUrl":"https://site-admin-avatar-cdn.prod.public.atl-paas.net/avatars/240/site.png"}]

    def get_accessible_resources(self):
        """Example:
        [{"id":"d1083787-4491-40c9-9581-8625f52baf7e","url":"https://etabot.atlassian.net","name":"etabot","scopes":["write:jira-work","read:jira-work","read:jira-user"],"avatarUrl":"https://site-admin-avatar-cdn.prod.public.atl-paas.net/avatars/240/site.png"}]
        """
        headers = self.default_headers()
        res = requests.get(
            self.accessible_resources_api, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            raise NameError('Could not get resources with given token. Status code: {}, message {}:'.format(
                res.status_code, res.json()
            ))

