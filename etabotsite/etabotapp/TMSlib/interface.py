from typing import List, Dict


class BasicReport:
    """
    Basic report data object for email and MVP dashboard
    """
    def __init__(
            self,
            *,
            projects: List[Dict],
            projects_on_track_names: List[str],
            deadlines_on_track: int,
            deadlines_total: int):
        self.projects_on_track_names = projects_on_track_names
        self.deadlines_on_track = deadlines_on_track
        self.deadlines_total = deadlines_total
        self.projects = projects
