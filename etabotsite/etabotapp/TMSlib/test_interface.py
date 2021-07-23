from etabotapp.TMSlib.interface import HierarchicalReportNode, BasicReport
import json
import pandas as pd
import datetime
import numpy as np


def test_to_dict_json_serializable():
    hn = HierarchicalReportNode(BasicReport.empty_report('Test'), 'entity')
    d = hn.to_dict()
    hn_json = json.dumps(d, allow_nan=False)
    assert isinstance(hn_json, str)
    hn.report.velocity_report.df_sprint_stats = pd.DataFrame(
        {
            't': [datetime.datetime(2020, 3, 15), np.datetime64('2020'), np.datetime64('2021'), np.datetime64('2022')],
            'd': [np.nan, None, np.inf, -np.inf]})
    d2 = hn.to_dict()
    hn_json2 = json.dumps(d2, allow_nan=False)
    assert isinstance(hn_json2, str)
