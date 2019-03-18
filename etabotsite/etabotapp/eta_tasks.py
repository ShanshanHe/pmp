"""Collection of tasks for updating ETAs."""

import TMSlib.data_conversion as dc
import TMSlib.TMS as TMSlib
import logging


def estimate_ETA_for_TMS(tms, projects_set):
    """Estimates ETA for a given TMS and projects_set.

    Todo:
    add an option not to refresh velocities
    https://etabot.atlassian.net/browse/ET-521
    """
    logging.debug('estimate_ETA_for_TMS started')
    tms_wrapper = TMSlib.TMSWrapper(tms)
    tms_wrapper.init_ETApredict(projects_set)

    project_names = []
    for project in projects_set:
        project.velocities = dc.get_velocity_json(
            tms_wrapper.ETApredict_obj.user_velocity_per_project,
            project.name)
        project.save()
        project_names.append(project.name)

    tms_wrapper.estimate_tasks(
        project_names=project_names)
    logging.debug('estimate_ETA_for_TMS finished')
