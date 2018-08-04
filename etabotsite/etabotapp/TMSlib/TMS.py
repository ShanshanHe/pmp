"""
	Task Management System (TMS) module
	abstract layer on TMSs (JIRA, Asana, etc)

	Author: Alex Radnaev (alexander.radnaev@gmail.com)

	Status: Prortotype
	Date last modified: 2018-04-13
	
	Python Version: 3.6
"""

from enum import Enum
import TMSlib.JIRA_API as JIRA_API
import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class TMSTypes(Enum):
	JIRA = 1


class ProtoTMS():
	"""
		TMS = Task Management System
		prototype for any TMS class to standardize critical methods and proprties
	"""
	def __init__(self, server_end_point, username_login, task_system_schema):
		self.server_end_point = server_end_point
		self.username_login = username_login
		self.task_system_schema = task_system_schema

	def get_projects(self):
		raise NotImplementedError('default get_projects is not implemented')

	def connect_to_TMS(self):
		raise NotImplementedError('default connect_to_TMS is not implemented')

	def get_all_tasks(self, tasks_framework):
		raise NotImplementedError('default get_all_tasks is not implemented')

	def estimate_tasks(self):
		raise NotImplementedError('default estimate task deadlines is not implemented')

class TMS_JIRA(ProtoTMS):
	
	def __init__(self, server_end_point, username_login, task_system_schema):

		ProtoTMS.__init__(self, server_end_point, username_login, task_system_schema)		
		self.defualt_task_system_schema = {
			'done_status_values':['Done'],
			'open_status_values':['To Do', 'Selected for Development']
		}

		self.jira = None
		
	def connect_to_TMS(self, password):
		try:
			self.jira = JIRA_API.JIRA_wrapper(self.server_end_point, self.username_login, password = password)
		except Exception as e:
			raise NameError("cannot connnect to TMS JIRA due to {}".format(e))

	def estimate_tasks(self):
		logging.info('Estimating tasks for JIRA: {}, hold tight!'.format(self))
		#TODO Shanshan Implement the method to call estimate algo



class TMSWrapper(TMS_JIRA):
	def __init__(self, TMS_type, server_end_point, username_login, task_system_schema):
		self.TMS_type = TMS_type
		if TMS_type == TMSTypes.JIRA:
			TMS_JIRA.__init__(self,server_end_point, username_login, task_system_schema)
			# self.TMS = TMS_JIRA()
		else:
			raise NameError("TMS_type {} is not supported at this time")


