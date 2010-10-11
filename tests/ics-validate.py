#!/usr/bin/python
#
# Copyright P. Christeas <p_christ@hol.gr> 2010
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################


import imp
import sys
import os
import glob
import re

from optparse import OptionParser
import vobject

parser = OptionParser()
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

parser.add_option("-H", "--host", dest="host", default='',
                  help="use HOST as serving address", metavar="HOST")

parser.add_option("-p", "--port", dest="port", default=8000,
                  help="bind to PORT", metavar="PORT")

(options, args) = parser.parse_args()

if not len(args):
	print "Usage: %s <command> file ... " % 'ics-validate.py'
	exit(2)
	
vobject.DEBUG=True
for fname in args:
    try:
	f = open(fname,'rb')
    except IOError, e:
	print "Cannot open %s, skipping" % fname
	continue
    
    try:
	print "Using input from %s" % fname
	for cal in vobject.readComponents(f, validate=True):
	    print "Imported component:", cal.behavior
	    print "Validate:", cal.validate()
	
    except Exception, e:
	print "Error while parsing:", e
	
    f.close()