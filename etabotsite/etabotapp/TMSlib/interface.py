from typing import List, Dict, Union
import duealert
import queue
from django.template.loader import render_to_string


class TargetDatesStats:
    """Due dates/sprint stats."""
    def __init__(self):
        self.summary_table = '{obj}'  # string with HTML table with tasks' status statistics
        self.tasks = {}  # {'<template_name_alert_status>': List[Dict]}
        self.counts = {'total': 0}  # len(List[Dict]) above"""
        for val in duealert.template_names_map.values():
            self.counts[val] = 0
            self.tasks[val] = []


class BasicReport:
    """
    Basic report data object for an entity (e.g. person or team) in a project
    """
    def __init__(
            self,
            *,
            project: str,
            project_on_track: Union[None, bool],
            entity_uuid: str,
            entity_display_name: str,
            due_dates_stats: TargetDatesStats,
            sprint_stats: TargetDatesStats,
            velocity_report,
            params: Dict,
            params_str: str,
            tms_name: str,
            aux=None):
        self.project = project
        self.project_on_track = project_on_track
        self.entity_uuid = entity_uuid
        self.entity_display_name = entity_display_name
        self.due_dates_stats = due_dates_stats
        self.sprint_stats = sprint_stats
        self.velocity_report = velocity_report
        self.aux = aux
        self.params = params
        self.params_str = params_str
        self.tms_name = tms_name
        self.html = self.render_to_html()

    def render_to_html(self):
        return render_to_string(
            'basic_report.html',
            {'basic_report': self})


class HierarchicalReportNode:
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
