"""TMS project class - mirror of Django project class."""


class TMS_project():
    def __init__(
            self,
            name,
            mode,
            open_status,
            grace_period,
            work_hours,
            vacation_days):

        self.name = name
        self.mode = mode
        self.open_status = open_status
        self.grace_period = grace_period
        self.work_hours = work_hours
        self.vacation_days = vacation_days
