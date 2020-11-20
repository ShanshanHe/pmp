from typing import Dict, List, Any
import logging
import os


def ensure_keys_exist(d: Dict, keys: List[str]) -> None:
    for key in keys:
        d[key] = get_key_value(d, key)


def get_key_value(d: Dict, key, default=None) -> Any:
    """Return value for the key either from the dict or environmental variable or default.
    Raises error if value is not found and there is no default."""

    if key not in d:
        if key in os.environ:
            value = os.environ[key]
            logging.warning('got key "{}" from environment.'.format(key))
        else:
            if default is not None:
                value = default
            else:
                raise NameError(
                    'key "{}" must be either in a settings json file or environmental variable'.format(key))
    else:
        value = d[key]
        logging.warning('key "{}" is already in dict.'.format(key))
    if isinstance(value, str) and len(str) == 0:
        logging.warning('Zero length string for key "{}" value.')
    return value


def deep_update_dict_with_environ(d: Dict):
    for k, v in d.items():
        if isinstance(v, dict):
            deep_update_dict_with_environ(v)
        else:
            if k in os.environ:
                d[k] = os.environ[k]
                logging.info('updated {} with {}'.format(k, d[k]))
