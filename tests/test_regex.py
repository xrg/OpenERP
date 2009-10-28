#!/usr/bin/python

import re


rege = re.compile(r'OpenERP-([\w|\.]+)_([0-9]+)@(\w+)$')

result = rege.match('OpenERP-project.task.work_324971@testdb')

print result
if result:
	print result.groups()