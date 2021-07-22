"""Reports."""

from etabotapp.TMSlib.interface import BasicReport, VelocityReport
import logging
from typing import Dict
from etabotapp.TMSlib.interface import BasicReport, HierarchicalReportNode, TargetDatesStats
from etabotapp.TMSlib.interface import DueAlert, TargetDatesStats
import pandas as pd


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
        project_name = 'ETAbot-Demo'
        report = {
            'project': project_name,
            'project_status': DueAlert.unknown,
            'entity_uuid': '2358a398bcd',
            'entity_display_name': 'Cheburaskha',
            'due_dates_stats': TargetDatesStats(),
            'sprint_stats': TargetDatesStats(),
            'velocity_report': VelocityReport('mock velocity report', pd.DataFrame()),
            'params': {},
            'params_str': 'taram param params',
            'tms_name': 'JIRA-example',
            }
        return {project_name: HierarchicalReportNode(
            report=BasicReport(**report), entity_uuid='AI')}
