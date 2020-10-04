"""Reports."""

from etabotapp.TMSlib.interface import BasicReport
import logging


def generate_status_report(ETApredict_obj, **kwargs):
    """Generate total report.

    Arguments:
    ETApredict_obj - ETApredict class object, must have task_list.

    Returns:
    json with hierarchical information.

    """
    logging.debug('ETApredict_obj: {}'.format(ETApredict_obj))
    if ETApredict_obj is None:
        raise NameError('ETApredict_obj must be provided.')
    report = {
          'projects_on_track_names': 'Cheburashka',
          'deadlines_on_track': 3,
          'deadlines_total': 4,
          'projects': [
              {
                    'project_name': 'Cheburashka',
                    'overdue': [],
                    'on_track': [
                        {
                            'task': 'clean river',
                            'due_date': 'Feb 2020',
                            'ETA': 'Jan 2020',
                            'link': 'https://xkcd.com?id=123'
                        },
                        {
                            'task': 'plan Japan trip',
                            'due_date': 'March 2020',
                            'ETA': 'Feb 2020',
                            'link': 'https://xkcd.com?id=123'
                        }
                        ],
                    'off_track': [],
              },
              {
                    'project_name':'Buckwheat',
                    'overdue':[
                        {
                            'task': 'roast buckwheat',
                            'due_date': 'Oct 2019',
                            'ETA': 'Jan 2020',
                            'link': 'https://xkcd.com?id=123'
                        }
                        ],
                    'on_track': [
                        {
                            'task': 'buy buckwheat',
                            'due_date': 'March 2020',
                            'ETA': 'Feb 2020',
                            'link': 'https://xkcd.com?id=123'
                        }
                        ],
                    'off_track': [],
              }
              ]
          }
    return BasicReport(**report)
