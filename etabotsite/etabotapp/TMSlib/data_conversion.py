"""Collection of data conversion tools."""
import logging


def get_velocity_json(velocities, project_name):
    """Creates velocity json for UI from velocities python object
    for a project named project_name"""
    velocity = velocities.get(project_name)
    velocity_json = {}
    if velocity is not None:
        velocity_json['mean'] = velocity.value
        velocity_json['upper_estimate'] = velocity.higher_estimate()
        velocity_json['lower_estimate'] = velocity.lower_estimate()
    else:
        logging.debug('velocity is None for project {}'.format(
            project_name))
    return velocity_json
