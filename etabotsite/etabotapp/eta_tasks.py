"""Collection of tasks for updating ETAs."""

import TMSlib.data_conversion as dc
import TMSlib.TMS as TMSlib
import logging
import reports
import user_activation as ua
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def estimate_ETA_for_TMS(tms, projects_set, **kwargs):
    """Estimates ETA for a given TMS and projects_set.

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
    tms_wrapper.init_ETApredict(projects_set)
    projects_dict = tms_wrapper.ETApredict_obj.eta_engine.projects
    project_names = []
    for project in projects_set:
        project.velocities = dc.get_velocity_json(
            tms_wrapper.ETApredict_obj.user_velocity_per_project,
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

    tms_wrapper.estimate_tasks(
        project_names=project_names,
        **kwargs)
    logging.debug('estimate_ETA_for_TMS finished')

SYS_DOMAIN = getattr(settings, "SYS_DOMAIN", "127.0.0.1")
SYS_EMAIL = getattr(settings, "SYS_EMAIL", None)
SYS_EMAIL_PWD = getattr(settings, "SYS_EMAIL_PWD", None)

def generate_email_report(tms, projects_set, **kwargs):
    """Generate the email report for a given TMS and projects_set.

    Arguments:
        tms - Django model of TMS.

    Todo:
    Build report structure
    """
    logging.debug(
        'geneating email report for TMS {}, projects: {}'.format(
            tms, projects_set))
    tms_wrapper = TMSlib.TMSWrapper(tms)
    tms_wrapper.init_ETApredict(projects_set)
    raw_status_report = tms_wrapper.generate_projects_status_report(**kwargs)
    formatted_report = reports.generate_formatted_report(raw_status_report)

    #Format the Msg for email.
    try:
        msg = MIMEMultipart()
        msg['From'] = '"ETAbot" <no-reply@etabot.ai>'
        msg['To'] = user.email
        msg['Subject'] = '[ETAbot] Your Daily Project Report'
        msg_body = render_to_string(formatted_report)
        msg.attach(MIMEText(msg_body, 'html'))
        logging.info("User Email: {}".format(user.email))

        user_activation.ActivationProcessor.send_email(msg)
        
        logging.info('Successfully sent report email to User %s '
                     % user.username)
    except Exception as ex:
        logging.error('Failed to send report email to User %s: %s'
                      % (user.username, str(ex)))
