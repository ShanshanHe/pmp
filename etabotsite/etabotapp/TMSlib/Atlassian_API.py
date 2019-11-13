"""Atlassian API helper funcrions."""

import requests

class AtlassianAPI():
    def __init__(self, token):
        self.token = token
        self.accessible_resources_api = \
            "https://api.atlassian.com/oauth/token/accessible-resources"

    def default_headers(self):
        return {
            'Authorization': 'Bearer {}'.format(self.token.access_token),
            'Accept': 'application/json'
        }

    def get_accessible_resources(self):
        """Example:
        [{"id":"d1083787-4491-40c9-9581-8625f52baf7e","url":"https://etabot.atlassian.net","name":"etabot","scopes":["write:jira-work","read:jira-work","read:jira-user"],"avatarUrl":"https://site-admin-avatar-cdn.prod.public.atl-paas.net/avatars/240/site.png"}]
        """
        headers = self.default_headers()
        res = requests.get(
            self.accessible_resources_api, headers=headers)
        return res.json()
