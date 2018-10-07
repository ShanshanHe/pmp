"""ETApredict placeholder."""
import logging
import TMSlib.TMS_project as TMS_project


class ETApredict():
    def __init__(
            self,
            TMS_interface=None):
        self.TMS_interface = TMS_interface
        self.projects = []
        logging.debug('ETApredict initialized')

    def init_with_Django_models(
            self,
            tms_config,
            projects):
        if len(projects) > 0:
            self.projects = projects
        else:
            self.get_projects()

    def generate_task_list_view_with_ETA(
            self):
        self.TMS_interface.connect_to_TMS(
            self.TMS_interface.tms_config.password)
        logging.info('placeholder ETAs have been generated')

    def get_projects(self):
        logging.debug('get_projects started')
        self.TMS_interface.connect_to_TMS(
            self.TMS_interface.tms_config.password)

        project1 = TMS_project.TMS_project(
            name='Project Buckwheat',
            mode='Scrum',
            open_status='To Do',
            grace_period='4.0',
            work_hours={
                "Monday": [

                    {"end": 21, "start": 19}

                ],

                "Thursday": [

                    {"end": 21, "start": 19}

                ],

                "Time Zone": "GMT +8",

                "Tuesday": [

                    {"end": 21, "start": 19}

                ],
                "Wednesday": [

                    {"end": 20, "start": 19},
                    {"end": 23, "start": 22}

                ]},
            vacation_days=[

                {"start": "2017-04-01", "end": "2017-05-02"},
                {"start": "2018-07-01", "end": "2018-07-02"},
                {"start": "2018-09-14", "end": "2018-09-21"}

            ])

        project2 = TMS_project.TMS_project(
            name='Project Cheburashka',
            mode='Kanban',
            open_status='To Do',
            grace_period='8.0',
            work_hours={
                "Sunday": [

                    {"end": 15, "start": 13}

                ],

                "Saturday": [

                    {"end": 15, "start": 13}

                ],

                "Time Zone": "GMT +7",

                },
            vacation_days=[

                {"start": "2017-04-01", "end": "2017-05-02"},
                {"start": "2018-07-01", "end": "2018-07-02"},
                {"start": "2018-09-14", "end": "2018-09-21"}

            ])
        self.projects.append(project1)
        self.projects.append(project2)
        logging.debug('get_projects finished')
