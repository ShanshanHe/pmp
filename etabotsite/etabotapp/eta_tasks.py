"""Collection of tasks for updating ETAs."""

import etabotapp.TMSlib.data_conversion as dc
import etabotapp.TMSlib.TMS as TMSlib
import logging
import etabotapp.email_reports as email_reports
from typing import List
from etabotapp.models import TMS, Project
from datetime import datetime


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
            logging.debug(
                'project.project_settings {} before update with {}:'.format(
                    project.project_settings,
                    project_settings))
            project.project_settings = project_settings
            project.save()
            logging.debug('project.project_settings after save: {}'.format(
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

    logging.debug(
        'estimate_ETA_for_TMS started for TMS {}, projects: {}'.format(
            tms, projects_set))
    tms_wrapper = TMSlib.TMSWrapper(tms)
    tms_wrapper.init_ETApredict(projects_set, **kwargs)

    project_names = save_project_velocities(tms_wrapper, projects_set)

    tms_wrapper.estimate_tasks(
        project_names=project_names,
        **kwargs)

    raw_status_reports = tms_wrapper.generate_projects_status_report(
        project_names=project_names, **kwargs)

    email_report, full_report = email_reports.EmailReportProcess.generate_html_report(
        tms.owner, raw_status_reports)

    email_msg = email_reports.EmailReportProcess.format_email_msg(
        tms.owner, html_report=email_report)
    email_reports.EmailReportProcess.send_email(email_msg)

    for project in projects_set:
        project_settings = project.project_settings
        project_settings['report'] = full_report
        project_settings['report_date'] = str(datetime.utcnow())

        # todo: save basic report and report hierarchy in to project model

        logging.debug("saving project settings: {}".format(project_settings))
        project.project_settings = project_settings

        project.save()

    logging.debug('estimate_ETA_for_TMS finished')


def generate_email_report(tms, projects_set, user, **kwargs):
    """Generate the email report for a given TMS and projects_set.

    Arguments:
        tms - Django model of TMS.

    Todo:
    Build report structure
    """
    logging.debug(
        'generating email report for TMS {}, projects: {}'.format(
            tms, projects_set))
    tms_wrapper = TMSlib.TMSWrapper(tms)
    tms_wrapper.init_ETApredict(projects_set)
    raw_status_reports = tms_wrapper.generate_projects_status_report(**kwargs)
    email_msg = email_reports.EmailReportProcess.format_email_msg(
        user,
        email_reports.EmailReportProcess.generate_html_report(
            user, raw_status_reports))
    email_reports.EmailReportProcess.send_email(email_msg)
    logging.debug('generate_email_report finished.')
