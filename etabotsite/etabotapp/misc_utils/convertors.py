import datetime
import logging

import numpy as np
import pandas as pd


def timestamp2unix(t: datetime.datetime):
    if isinstance(t, datetime.datetime):
        return t.timestamp()  # todo: account for time zone (e.g. calendar module)
    return t


def nan2None(x):
    if isinstance(x, float):
        if np.isnan(x) or np.isinf(x):
            return None
    return x


def value2safejson(x):
    return timestamp2unix(nan2None(x))


def df_to_dict_for_json(df: pd.DataFrame) -> dict:
    logging.debug('df_to_dict_for_json input df: {}'.format(df))
    res = df.applymap(value2safejson).to_dict()
    logging.debug(res)
    return res
