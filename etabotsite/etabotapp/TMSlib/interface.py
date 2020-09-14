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
            deadlines_total: int,
            params: Dict,
            tms_name: str,
            project_names: List[str],
            aux=None):
        self.projects_on_track_names = projects_on_track_names
        self.deadlines_on_track = deadlines_on_track
        self.deadlines_total = deadlines_total
        self.projects = projects
        self.aux = aux
        self.params = params
        self.tms_name = tms_name
        self.project_names = ''
        if project_names:
            self.project_names = ', '.join(sorted(project_names))
        self.projects_dict = {}
        for project in self.projects:
            project_name = project.get('project_name')
            if project_name:
                self.projects_dict[project_name] = project
