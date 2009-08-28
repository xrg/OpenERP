#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright P. Christeas <p_christ@hol.gr> 2008,2009
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
#

import imp
import sys
import os
import glob
import subprocess
import re

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

#parser.add_option("-r", "--onlyver",
                  #action="store_true", dest="onlyver", default=False,
                  #help="Generates the version string and exits.")

parser.add_option("-H", "--host", dest="host", default='',
                  help="use HOST as serving address", metavar="HOST")

parser.add_option("-p", "--port", dest="port", default=8000,
                  help="bind to PORT", metavar="PORT")

#parser.add_option("-m", "--exclude-from",
                  #dest="exclude",
                  #help="Reads the file FROM_LIST and excludes those modules",
                  #metavar = "FROM_LIST")

(options, args) = parser.parse_args()

if not len(args):
	print "Usage: %s <command> [args...]" % 'http-client.py'
	exit(2)

import httplib

def simple_get(args):
	print "Getting http://%s" % args[0]
	conn = httplib.HTTPConnection(args[0])
	if len(args)>1:
		path = args[1]
	else:
		path = "/index.html"
	conn.request("GET", path )
	r1 = conn.getresponse()
	print "Reponse:",r1.status, r1.reason
	data1 = r1.read()
	print "Body:"
	print data1
	print "End of body\n"
	conn.close()

def multi_get(args):
	print "Getting http://%s" % args[0]
	conn = httplib.HTTPConnection(args[0])
	if len(args)>1:
		paths = args[1:]
	else:
		paths = ["/index.html"]
		
	for path in paths:
		print "getting ", path
		conn.request("GET", path, [], { 'Connection': 'keep-alive' } )
		r1 = conn.getresponse()
		print "Reponse:",r1.status, r1.reason
		data1 = r1.read()
		print "Body:"
		print data1
		print "End of body\n"
	conn.close()

def auth_get(args):
	import base64
	from time import sleep
	print "Getting http://%s" % args[0]
	conn = httplib.HTTPConnection(args[0])
	if len(args)>1:
		paths = args[1:]
	else:
		paths = ["/index.html"]
		
	for path in paths:
		print "getting ", path
		conn.request("GET", path, [], { 'Connection': 'keep-alive' } )
		try:
			r1 = conn.getresponse()
		except httplib.BadStatusLine, bsl:
			print "Bad status line:", bsl.line
			break
		if r1.status == 401: # and r1.headers:
			if 'www-authenticate' in r1.msg:
				(atype,realm) = r1.msg.getheader('www-authenticate').split(' ')
				data1 = r1.read()
				print r1.version,r1.isclosed(), r1.will_close
				print "Want to do auth %s for realm %s" % (atype, realm)
				if atype == 'Basic' :
					auths = base64.encodestring('user' + ':' + 'password')
					if auths[-1] == "\n":
						auths = auths[:-1]
					connhs = { 'Connection': 'keep-alive',
						'Authorization': 'Basic '+ auths }
					sleep(1)
					conn.request("GET",path,[], connhs)
					r1 = conn.getresponse()
				else:
					raise Exception("Unknown auth type %s" %atype)
			else:
				print "Got 401, cannot auth"
				raise Exception('No auth')
			
		print "Reponse:",r1.status, r1.reason
		data1 = r1.read()
		print "Body:"
		print data1
		print "End of body\n"
	conn.close()

def rpc_about(args):
	import xmlrpclib
	
	try:
		srv = xmlrpclib.ServerProxy(args[0]+'/xmlrpc/common');
		s = srv.about()
		print s
	except xmlrpclib.Fault, f:
		print "Fault:",f.faultCode
		print f.faultString
	
def rpc_listdb(args):
	import xmlrpclib
	
	try:
		srv = xmlrpclib.ServerProxy(args[0]+'/xmlrpc/db');
		li = srv.list()
		print "List db:",li
	except xmlrpclib.Fault, f:
		print "Fault:",f.faultCode
		print f.faultString

def rpc_login(args):
	import xmlrpclib
	import getpass
	try:
		srv = xmlrpclib.ServerProxy(args[0]+'/xmlrpc/common')
		passwd =getpass.getpass("Password for %s@%s: " %(args[2],args[1]) )
		if srv.login(args[1], args[2],passwd):
			print "Login OK"
		else:
			print "Login Failed"
	except xmlrpclib.Fault, f:
		print "Fault:",f.faultCode
		print f.faultString

cmd = args[0]
args = args[1:]
commands = { 'get' : simple_get , 'mget' : multi_get, 'aget': auth_get,
	'rabout': rpc_about, 'listdb': rpc_listdb, 'login': rpc_login  }

if not commands.has_key(cmd):
	print "No such command: %s" % cmd
	exit(1)

funct = commands[cmd]
if not funct(args):
	exit(1)

#eof
