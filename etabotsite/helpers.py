from typing import Dict, List, Any
import logging
import os


def ensure_keys_exist(d: Dict, keys: List[str]) -> None:
    for key in keys:
        d[key] = get_key_value(d, key)


def get_key_value(d: Dict, key, default=None) -> Any:
    if key not in d:
        if key in os.environ:
            value = os.environ[key]
            logging.info('got key "{}" from environment.'.format(key))
        else:
            if default is not None:
                value = default
            else:
                raise NameError(
                    'key "{}" must be either in a settings json file or environmental variable'.format(key))
    else:
        value = d[key]
        logging.info('key "{}" is in dict.')
    return value
