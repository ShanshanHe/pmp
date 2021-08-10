"""Collection of tasks for updating ETAs."""

import etabotapp.TMSlib.data_conversion as dc
import etabotapp.TMSlib.TMS as TMSlib
import logging
import etabotapp.email_reports as email_reports

from typing import List, Tuple

from etabotapp.TMSlib.interface import HierarchicalReportNode
from etabotapp.models import TMS, Project
from datetime import datetime
logger = logging.getLogger()


def save_project_velocities(tms_wrapper, projects_set) -> List[str]:
    projects_dict = tms_wrapper.ETApredict_obj.task_system_schema['projects']
    project_names = []

    for project in projects_set:
        if tms_wrapper.ETApredict_obj.eta_engine is not None:
            project.velocities = dc.get_velocity_json(
                tms_wrapper.ETApredict_obj.eta_engine.user_velocity_per_project,
                project.name)
            project_settings = projects_dict.get(project.name, {}).get(
                        'project_settings', {})
            logger.debug(
                'project.project_settings {} before update with {}:'.format(
                    project.project_settings,
                    project_settings))
            project.project_settings = project_settings
            project.save()
            logger.debug('project.project_settings after save: {}'.format(
                project.project_settings))

        project_names.append(project.name)
    return project_names


def estimate_ETA_for_TMS(
        tms: TMS, projects_set: List[Project], **kwargs) -> None:
    """Estimates ETA for a given TMS and projects_set. This will generate and send reports, update velocities,
    push ETAs to destinations.

    Arguments:
        tms - Django model of TMS.

    Todo:
    add an option not to refresh velocities
    https://etabot.atlassian.net/browse/ET-521
    """
    logs = []
    logger.debug(
        'estimate_ETA_for_TMS started for TMS {}, projects: {}'.format(
            tms, projects_set))
    logs.append((datetime.utcnow(), 'TMS {} connectivity_status: {}'.format(str(tms), tms.connectivity_status)))
    tms_wrapper = TMSlib.TMSWrapper(tms, logs=logs)
    logs.append((datetime.utcnow(), 'tms wrapper initialized'))
    tms_wrapper.init_ETApredict(projects_set, **kwargs)
    logs.append((datetime.utcnow(), 'ETA prediction module initialized'))
    project_names = save_project_velocities(tms_wrapper, projects_set)
    logs.append((datetime.utcnow(), 'project names detected: {}'.format(project_names)))

    tms_wrapper.estimate_tasks(
        project_names=project_names,
        logs=logs,
        **kwargs)
    if tms_wrapper.ETApredict_obj is None:
        logs.append((datetime.utcnow(), 'Error: ETApredict_obj is None'))
    elif tms_wrapper.ETApredict_obj.df_tasks_with_ETAs is None:
        logs.append((datetime.utcnow(), 'Error: df_tasks_with_ETAs is None'))
    else:
        logs.append((datetime.utcnow(), 'generated ETAs for {} tasks'.format(
            tms_wrapper.ETApredict_obj.df_tasks_with_ETAs.shape[0])))
    raw_status_reports = tms_wrapper.generate_projects_status_report(
        project_names=project_names, **kwargs)
    logs.append((datetime.utcnow(), 'generated {} status reports for: {}'.format(
        len(raw_status_reports), ', '.join(list(raw_status_reports.keys())))))

    email_report, full_report = email_reports.EmailReportProcess.generate_html_report(
        tms.owner, raw_status_reports, logs=logs)
    images = []
    for report_name, report_node in raw_status_reports.items():
        for report in report_node.all_reports():
            for image in report.velocity_report.images_for_email.values():
                images.append(image)

    email_msg = email_reports.EmailReportProcess.format_email_msg(
        tms.owner, html_report=email_report, images=images)

    email_reports.EmailReportProcess.send_email(email_msg)

    for project in projects_set:
        project_settings = project.project_settings
        project_settings['report'] = full_report
        project_settings['report_date'] = str(datetime.utcnow())
        if project.name in raw_status_reports:
            hierarchical_report = raw_status_reports[project.name]
            if isinstance(hierarchical_report, HierarchicalReportNode):
                project_settings['hierarchical_report'] = hierarchical_report.to_dict()
                # todo: https://etabot.atlassian.net/browse/ET-879
                # del project_settings['hierarchical_report']['velocity_report']['df_sprint_stats']
                # del project_settings['hierarchical_report']['velocity_report']['df_velocity_vs_time']
                # del project_settings['hierarchical_report']['velocity_report']['df_velocity_stats']

            else:
                logger.warning('hierarchical_report ({}) is not of HierarchicalReportNode type'.format(
                    type(hierarchical_report)
                ))

        # logger.debug("saving project settings: {}".format(project_settings))
        # logger.debug("saving project settings hierarchical_report: {}".format(
        #     project_settings.get('hierarchical_report')))
        project.project_settings = project_settings

        project.save()

    logger.debug('estimate_ETA_for_TMS finished')

