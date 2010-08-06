#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
# Copyright 2010, OpenERP SA. <www.openerp.com>
# Copyright 2010, P. Christeas <p_christ@hol.gr>
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software.

import logging
LOG_FILENAME = 'test-example.log'
logging.basicConfig(level=logging.DEBUG)

logging.debug('This message should go to the log file')

logging.getLogger('my.custom.logger').setLevel(logging.WARNING)
logging.getLogger('my.other.one')
logging.getLogger('my.other').setLevel(logging.ERROR)

print logging.root.manager

for n, log in logging.root.manager.loggerDict.items():
    if isinstance(log, logging.Logger):
	print "Log %s : %s" % (log.name, log.level or '-')
    else:
	print "Dict item %s is an %s" % (n, type(log))
	
import ConfigParser

cp = ConfigParser.SafeConfigParser()
cp.read('conf-logging.ini')
print cp.items('logging')
#eof
