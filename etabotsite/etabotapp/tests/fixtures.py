import pytest
import pandas as pd
import numpy as np
import sprint as s
from sprints import Sprints
import logging
from datetime import datetime

done_str = 'Done'
todo_str = 'To Do'


@pytest.fixture()
def task_system_schema():
    return {
        'projects': {
            'projectA': {
                'mode': 'scrum'
            },
            'projectB': {
                'mode': 'scrum'
            },

        }
    }


@pytest.fixture()
def schedule_start_datetime():
    return np.datetime64(datetime.now())


@pytest.fixture()
def df_all_tasks():
    projects = [
        'projectA', 'projectB', 'projectB', 'projectA',
        'projectA', 'projectB', 'projectB', 'projectA']
    scopes = [1, 2, 4, 13, 0.5, 3, 3, 21]
    sprints = [
        'A-S1', 'B-S10', 'B-S10', 'A-S1',
        'A-S2', 'B-S11', 'B-S11', 'A-S2']
    sprint_start_dates_map = {
        'A-S1': pd.to_datetime('2020-06-01'),
        'B-S10': pd.to_datetime('2020-06-02'),
        'A-S2': pd.to_datetime('today'),
        'B-S11': pd.to_datetime('today')
    }

    summaries = []
    for project, scope, sprint, idx in zip(projects, scopes, sprints, range(len(projects))):
        summaries.append('{}-{}-{}-{}'.format(project, idx, scope, sprint))

    sprint_start_dates = [
        sprint_start_dates_map[x] for x in sprints
    ]
    sprint_end_dates = [
        x + pd.Timedelta(2, unit='W') for x in sprint_start_dates]

    df_tasks = pd.DataFrame({
        'id': ['TS-{}'.format(i) for i in range(100, 100 + len(projects))],
        'project': projects,
        'scope': scopes,
        'summary': summaries,
        'status': [done_str] * 4 + [todo_str] * 4,
        'target_sprint_id': sprints,
        'target_sprint_name': sprints,
        'target_sprint_end_date': sprint_end_dates,
        'target_sprint_start_date': sprint_start_dates,
        'planned': [True] * 8,
        'active_sprint': [False] * 4 + [True] * 4,
        'assignee': ["ETA"] * 4 + ["BOT"] * 8
    })
    return df_tasks


@pytest.fixture()
def df_done_issues(df_all_tasks):
    return df_all_tasks[df_all_tasks['status'] == done_str]


@pytest.fixture()
def df_open_issues(df_all_tasks):
    return df_all_tasks[df_all_tasks['status'] == todo_str]


@pytest.fixture()
def all_sprints(df_all_tasks, task_system_schema):
    sprints = Sprints(task_system_schema=task_system_schema)

    def parse_sprint(x):
        sprint_id = x['target_sprint_id']
        if sprint_id not in sprints:
            sprint_params = {
                'id': sprint_id,
                'name': x['target_sprint_name'],
                'state': 'ACTIVE' if x['active_sprint'] else 'CLOSED',
                'start_date': x['target_sprint_start_date'],
                'end_date': x['target_sprint_end_date'],
                'project': x['project']
            }
            sprints.add_sprint(s.Sprint(
                sprint_string='',
                sprint_param_list=sprint_params,
                task_system_schema=task_system_schema))

    df_all_tasks.apply(parse_sprint, axis=1)
    logging.debug('sprints mocked: {}'.format(sprints.sprints_by_id.values()))

    return sprints
