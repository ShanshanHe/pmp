import datetime
import pandas as pd

from etabotapp.misc_utils.convertors import timestamp2unix


def test_timestamp2unix():
    d = datetime.datetime(2020, 3, 15)
    assert timestamp2unix(d) == 1584230400

    df = pd.DataFrame({'t': [datetime.datetime(2020, 3, 15)], 's': ['test']})
    df2 = df.applymap(timestamp2unix)
    assert df2['t'][0] == 1584230400
    assert df2['s'][0] == 'test'
