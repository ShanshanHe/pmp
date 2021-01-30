"""Reports."""

from etabotapp.TMSlib.interface import BasicReport
import logging
from typing import Dict
from etabotapp.TMSlib.interface import BasicReport, HierarchicalReportNode, TargetDatesStats
from etabotapp.TMSlib.interface import DueAlert, TargetDatesStats


class ReportGenerator:
    def generate_status_reports(
            self,
            ETApredict_obj,
            **kwargs) -> Dict[str, HierarchicalReportNode]:
        """Generate total report.

        Arguments:
        ETApredict_obj - ETApredict class object, must have task_list.

        Returns:
        json with hierarchical information.

        """
        logging.debug('ETApredict_obj: {}'.format(ETApredict_obj))
        if ETApredict_obj is None:
            raise NameError('ETApredict_obj must be provided.')
        report = {
            'project': 'Awesome Project',
            'project_status': DueAlert.unknown_eta,
            'entity_uuid': '2358a398bcd',
            'entity_display_name': 'Cheburaskha',
            'due_dates_stats': TargetDatesStats(),
            'sprint_stats': TargetDatesStats(),
            'velocity_report': None,
            'params': {},
            'params_str': 'taram param params',
            'tms_name': 'JIRA-example'
            }
        return {'awesome project': HierarchicalReportNode(
            report=BasicReport(**report), entity_uuid='AI')}

#
# 'projects': [
#     {
#         'project_name': 'Cheburashka',
#         'overdue': [],
#         'on_track': [
#             {
#                 'task': 'clean river',
#                 'due_date': 'Feb 2020',
#                 'ETA': 'Jan 2020',
#                 'link': 'https://xkcd.com?id=123'
#             },
#             {
#                 'task': 'plan Japan trip',
#                 'due_date': 'March 2020',
#                 'ETA': 'Feb 2020',
#                 'link': 'https://xkcd.com?id=123'
#             }
#         ],
#         'off_track': [],
#     },
#     {
#         'project_name': 'Buckwheat',
#         'overdue': [
#             {
#                 'task': 'roast buckwheat',
#                 'due_date': 'Oct 2019',
#                 'ETA': 'Jan 2020',
#                 'link': 'https://xkcd.com?id=123'
#             }
#         ],
#         'on_track': [
#             {
#                 'task': 'buy buckwheat',
#                 'due_date': 'March 2020',
#                 'ETA': 'Feb 2020',
#                 'link': 'https://xkcd.com?id=123'
#             }
#         ],
#         'off_track': [],
#     }
# ]