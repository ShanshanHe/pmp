"""Task Management System (TMS) module abstract layer on TMSs (JIRA, Asana,..).

Author: Alex Radnaev (alexander.radnaev@gmail.com)

Status: Prortotype
Date last modified: 2018-04-13

Python Version: 3.6
"""

from enum import Enum
import TMSlib.JIRA_API as JIRA_API
import logging
import sys

try:
    sys.path.append('etabot_algo/')
    logging.debug(sys.path)
    import etabot_algo.ETApredict as ETApredict
except Exception as e:
    logging.warning('cannot load ETApredict due to "{}"\
 Loading ETApredict_placeholder'.format(e))
    import TMSlib.ETApredict_placeholder as ETApredict

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

TMS_TYPES = (
        ('JI', 'JIRA'),
    )


class ProtoTMS():
    """
        TMS = Task Management System
        prototype for any TMS class to standardize critical methods and proprties
    """
    def __init__(self, server_end_point, username_login, task_system_schema):
        self.server_end_point = server_end_point
        self.username_login = username_login
        self.task_system_schema = task_system_schema

    def get_projects(self):
        raise NotImplementedError('default get_projects is not implemented')

    def connect_to_TMS(self):
        raise NotImplementedError('default connect_to_TMS is not implemented')

    def get_all_tasks(self, assignee):
        raise NotImplementedError('default get_all_tasks is not implemented')

    def get_all_open_tasks_ranked(self, assignee):
        raise NotImplementedError('default get_all_tasks is not implemented')

    def estimate_tasks(self):
        raise NotImplementedError(
            'default estimate task deadlines is not implemented')


class TMS_JIRA(ProtoTMS):

    default_open_status_values = ['Open', 'To Do', 'Selected for Development']

    def __init__(
            self, server_end_point, username_login, task_system_schema):

        if task_system_schema is None:
            task_system_schema = {
                'done_status_values': ['Done'],
                'open_status_values': default_open_status_values
            }

        ProtoTMS.__init__(
            self, server_end_point, username_login, task_system_schema)

        self.jira = None
        logging.debug('TMS_JIRA initalized')

    def connect_to_TMS(self, password):
        try:
            self.jira = JIRA_API.JIRA_wrapper(
                self.server_end_point,
                self.username_login,
                password=password)
        except Exception as e:
            raise NameError("cannot connnect to TMS JIRA due to {}".format(e))

        # all_issues = jira.get_jira_issues('assignee={username} ORDER BY Rank ASC'.format(username = self.username))

    def get_all_done_tasks_ranked(self, assignee=None):
        if assignee is None:
            assignee = 'currentUser()'

        done_issues = self.jira.get_jira_issues(
            'assignee={assignee} AND status in ({done_status_values}) \
ORDER BY Rank ASC'.format(
                assignee=assignee,
                done_status_values=', '.join(
                    ['"{}"'.format(x) for x in self.task_system_schema.get(
                        'done_status_values', ['Done'])])))
        logging.debug('acquired done tasks count: {}'.format(
            len(done_issues)))
        return done_issues

    def get_all_open_tasks_ranked(self, assignee=None):
        if assignee is None:
            assignee = 'currentUser()'

        open_status_values = self.task_system_schema.get(
                'open_status_values',
                self.default_open_status_values)
        if len(open_status_values) == 0:
            open_status_values = self.default_open_status_values
        open_status_vals_list = [
            '"{}"'.format(x)
            for x in open_status_values]
        open_status_values_css = ', '.join(open_status_vals_list)

        in_progress_issues_current_sprint = self.jira.get_jira_issues(
            'assignee={assignee} AND status="In Progress" \
AND sprint in openSprints() ORDER BY Rank ASC'.format(assignee=assignee))

        if len(in_progress_issues_current_sprint) > 0:
            logging.debug('task sample')
            logging.debug(in_progress_issues_current_sprint[0])
            logging.debug(in_progress_issues_current_sprint[0].fields.summary)

        in_progress_issues = self.jira.get_jira_issues(
            'assignee={assignee} AND status="In Progress" \
ORDER BY Rank ASC'.format(assignee=assignee))

        if len(open_status_values_css) > 0:
            open_issues_current_sprint = self.jira.get_jira_issues(
                    'assignee={assignee} AND status in ({open_status_values}) \
    AND sprint in openSprints()  ORDER BY Rank ASC'.format(
                        assignee=assignee,
                        open_status_values=open_status_values_css))

            open_issues = self.jira.get_jira_issues(
                'assignee={assignee} AND status in ({open_status_values}) \
    ORDER BY Rank ASC'.format(
                    assignee=assignee,
                    open_status_values=open_status_values_css))
        else:
            open_issues_current_sprint = []
            open_issues = []

        logging.debug("""acquired open tasks counts:
in_progress_issues_current_sprint: {},
in_progress_issues: {},
open_issues_current_sprint: {},
open_issues: {}""".format(
                    len(in_progress_issues_current_sprint),
                    len(in_progress_issues),
                    len(open_issues_current_sprint),
                    len(open_issues)))

        return in_progress_issues_current_sprint \
            + in_progress_issues \
            + open_issues_current_sprint \
            + open_issues


class TMSWrapper(TMS_JIRA):
    def __init__(
            self,
            tms_config,
            projects=None):
        """
        Arguments:
            tms_config - Django model of TMS"""
        logging.debug('initializing TMSWrapper with "{}"'.format(
            tms_config))
        self.tms_config = tms_config
        self.TMS_type = tms_config.type
        self.ETApredict_obj = None

        task_system_schema = {}

        if projects is not None:
            open_status_values = []
            for project in projects:
                open_status_values.append(project.open_status)
            task_system_schema['open_status_values'] = list(
                set(open_status_values))
            logging.debug('detected open_status_values: "{}"'.format(
                task_system_schema['open_status_values']))

        logging.debug('allowed TMS types: "{}"'.format(TMS_TYPES))
        if self.TMS_type == TMS_TYPES[0][0]:
            logging.debug('initalizing TMS JIRA class')
            TMS_JIRA.__init__(
                self,
                tms_config.endpoint,
                tms_config.username,
                task_system_schema)
            # self.TMS = TMS_JIRA()
        else:
            raise NameError(
                "TMS_type {} is not supported at this time".format(
                    self.TMS_type))

    def init_ETApredict(self, projects):
        logging.debug('init_ETApredict started')
        self.ETApredict_obj = ETApredict.ETApredict(TMS_interface=self)
        self.ETApredict_obj.init_with_Django_models(self.tms_config, projects)
        logging.debug('init_ETApredict finished')

    def estimate_tasks(self, project_names=None):
        logging.info('Estimating tasks for TMS "{}", \
projects: "{}", hold tight!'.format(self, project_names))
        # TODO Shanshan Implement the method to call estimate algo
        self.ETApredict_obj.generate_task_list_view_with_ETA(project_names)
