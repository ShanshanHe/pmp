import logging
from enum import Enum
from typing import List, Dict, Union
import queue
from django.template.loader import render_to_string
import pandas as pd


due_alert_names_map = {
    'DueAlert.on_track': 'on_track',
    'DueAlert.at_risk': 'at_risk',
    'DueAlert.off_track': 'off_track',
    'DueAlert.unknown': 'unknown',
    'DueAlert.overdue': 'overdue',
    None: 'unknown',
    'None': 'unknown'
}


class DueAlert(Enum):
    on_track = 0
    at_risk = 1
    off_track = 2
    unknown = 3
    overdue = 4


def due_alert_display_name(x):
    res = due_alert_names_map.get(str(x))
    if res is None:
        logging.error('unknown due alert status {}'.format(x))
        res = str(x)
    return res


class TargetDatesStats:
    """Due dates/sprint stats that shows up in the reports."""
    def __init__(self):
        self.summary_table = '{obj}'  # string with HTML table with tasks' status statistics
        self.tasks = {}  # {'<template_name_alert_status>': List[task_Dict]}
        # task_Dict {'task': str, 'due_date': due_date, etc} todo make the task an object instead of the Dict
        self.counts = {'total': 0}  # {<duealert.template_names_map.values>: len(List[Dict])} above"""
        for val in due_alert_names_map.values():
            self.counts[val] = 0
            self.tasks[val] = []


class VelocityReport:
    def __init__(self, summary: str, df_sprint_stats: pd.DataFrame, aux: str = ''):
        self.summary = summary
        self.df_sprint_stats = df_sprint_stats  # rows - sprints, columns: scope, velocity, etc
        self.df_velocity_vs_time = pd.DataFrame()  # rows - sprints, columns - entities/measureables
        self.df_velocity_stats = pd.DataFrame()  # rows - stats (mean, std, sum), columns - entities/measureable stats
        self.html = self.to_html()
        self.images = {}  # '{image_name: img_tag}'
        self.aux = aux

    def to_html(self, **params) -> str:
        if self.df_sprint_stats is not None:
            return self.df_sprint_stats.rename(columns={'id': 'done_issues in sprint'}).to_html(**params)
        return 'No Velocity report html.'


class BasicReport:
    """
    Basic report data object for an entity (e.g. person or team) in a project.

    Purpose - deliver a self-contained report that can be shared without additional context.
    """
    def __init__(
            self,
            *,
            project: str,  # project name
            project_status: DueAlert,
            entity_uuid: str,
            entity_display_name: str,
            due_dates_stats: TargetDatesStats,
            sprint_stats: TargetDatesStats,
            velocity_report: VelocityReport,
            params: Dict,  # parameters that were used to generate the report
            params_str: str,  # human readable params
            tms_name: str,
            aux=None):
        self.project = project
        self.project_on_track = project_status
        self.entity_uuid = entity_uuid
        self.entity_display_name = entity_display_name
        self.due_dates_stats = due_dates_stats
        self.sprint_stats = sprint_stats
        self.velocity_report = velocity_report
        if aux is None:
            self.aux = {}
        else:
            self.aux = aux
        self.params = params
        self.params_str = params_str
        self.tms_name = tms_name
        self.html = self.render_to_html()
        self.short_html = self.render_to_html_short()

    def render_to_html(self):
        return render_to_string(
            'basic_report.html',
            {'basic_report': self})

    def render_to_html_short(self):
        return render_to_string(
            'short_report.html',
            {'basic_report': self})

    @staticmethod
    def empty_report(project: str):
        return BasicReport(
            project=project,
            project_status=DueAlert.unknown,
            entity_uuid='Unknown',
            entity_display_name='Unknown',
            due_dates_stats=TargetDatesStats(),
            sprint_stats=TargetDatesStats(),
            velocity_report=VelocityReport('No velocity data yet.', pd.DataFrame()),
            params={},
            params_str='',
            tms_name='',
            aux='<h2>No data available to generate report for this project.</h2>')


class HierarchicalReportNode:
    """Tree data structure for hierarchical report.

    Example #1:

        Team A
    Bob   Alice    Eve

    Example #2:

                Beer production Division
        Team Pale Ale       Team Lager         Team Porter
    Alex  Steve  Yarik       Chad  Koy             Jacob

    """
    def __init__(self, report: BasicReport, entity_uuid: str):
        self.parent = None
        self.report = report
        self.children = []
        self.entity_uuid = entity_uuid

    def add_child(self, report_node: 'HierarchicalReportNode'):
        self.children.append(report_node)
        report_node.parent = self

    def all_nodes(self) -> List['HierarchicalReportNode']:
        result = []
        q = queue.Queue()
        q.put(self)
        while not q.empty():
            node = q.get()
            result.append(node)
            for child in node.children:
                q.put(child)
        return result

    def all_reports(self) -> List[BasicReport]:
        return [node.report for node in self.all_nodes()]
