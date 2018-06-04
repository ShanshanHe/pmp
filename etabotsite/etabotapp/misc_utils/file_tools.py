"""Purpose: collect common file tools.

Author: Alex Radnaev

date created: 2018-06-03
"""
import fnmatch
import os


def find_all_recursively(pattern, path):
    """Return a list of files matching the pattern in path and directories within.

    arguments:
        pattern: string representing the filename pattern
        e.g. '*.txt'

        path: path where search is conducted
    """
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result
