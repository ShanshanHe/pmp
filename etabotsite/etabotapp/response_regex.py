"""Collection of regex functions to parse http responses."""

import re


def get_login_url(s):
    """Return list of values of login-url."""
    res = re.findall(r'login-url=(.*?)\'', s)
    return res
