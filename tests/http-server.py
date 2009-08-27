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

parser.add_option("-r", "--onlyver",
                  action="store_true", dest="onlyver", default=False,
                  help="Generates the version string and exits.")

parser.add_option("-H", "--host", dest="host", default='',
                  help="use HOST as serving address", metavar="HOST")

parser.add_option("-p", "--port", dest="port", default=8000,
                  help="bind to PORT", metavar="PORT")

parser.add_option("-x", "--exclude-from",
                  dest="exclude",
                  help="Reads the file FROM_LIST and excludes those modules",
                  metavar = "FROM_LIST")

(options, args) = parser.parse_args()

from BaseHTTPServer import *

from SimpleHTTPServer import SimpleHTTPRequestHandler
class HTTPHandler(SimpleHTTPRequestHandler):
	def __init__(self,request, client_address, server):
		SimpleHTTPRequestHandler.__init__(self,request,client_address,server)
		print "Handler for %s inited" % str(client_address)
		self.protocol_version = 'HTTP/1.1'
	
	def handle(self):
		""" Classes here should NOT handle inside their constructor
		"""
		pass
	
	def finish(self):
		pass
	
	def setup(self):
		pass

class HTTPDir:
	""" A dispatcher class, like a virtual folder in httpd
	"""
	def __init__(self,path,handler, auth_provider = None):
		self.path = path
		self.handler = handler
		self.auth_provider = auth_provider
		
	def matches(self, request):
		""" Test if some request matches us. If so, return
		    the matched path. """
		if request.startswith(self.path):
			return self.path
		return False
	

class noconnection:
	""" a class to use instead of the real connection
	"""
	def makefile(self, mode, bufsize):
		return None

import SocketServer
class MultiHTTPHandler(BaseHTTPRequestHandler):
    """ this is a multiple handler, that will dispatch each request
        to a nested handler, iff it matches
    """

    def __init__(self, request, client_address, server):
	self.in_handlers = {}
	print "MultiHttpHandler init"
	SocketServer.StreamRequestHandler.__init__(self,request,client_address,server)

    def _handle_one_foreign(self,fore, path):
        """ This method overrides the handle_one_request for *children*
            handlers. It is required, since the first line should not be
	    read again..

        """
        fore.raw_requestline = "%s %s %s\n" % (self.command, path, self.version)
        if not fore.parse_request(): # An error code has been sent, just exit
            return
        mname = 'do_' + fore.command
        if not hasattr(fore, mname):
            fore.send_error(501, "Unsupported method (%r)" % fore.command)
            return
        method = getattr(fore, mname)
        method()
	if fore.close_connection:
		# print "Closing connection because of handler"
		self.close_connection = fore.close_connection

    def parse_rawline(self):
        """Parse a request (internal).

        The request should be stored in self.raw_requestline; the results
        are in self.command, self.path, self.request_version and
        self.headers.

        Return True for success, False for failure; on failure, an
        error is sent back.

        """
        self.command = None  # set in case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = 1
        requestline = self.raw_requestline
        if requestline[-2:] == '\r\n':
            requestline = requestline[:-2]
        elif requestline[-1:] == '\n':
            requestline = requestline[:-1]
        self.requestline = requestline
        words = requestline.split()
        if len(words) == 3:
            [command, path, version] = words
            if version[:5] != 'HTTP/':
                self.send_error(400, "Bad request version (%r)" % version)
                return False
            try:
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split(".")
                # RFC 2145 section 3.1 says there can be only one "." and
                #   - major and minor numbers MUST be treated as
                #      separate integers;
                #   - HTTP/2.4 is a lower version than HTTP/2.13, which in
                #      turn is lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                if len(version_number) != 2:
                    raise ValueError
                version_number = int(version_number[0]), int(version_number[1])
            except (ValueError, IndexError):
                self.send_error(400, "Bad request version (%r)" % version)
                return False
            if version_number >= (1, 1):
                self.close_connection = 0
            if version_number >= (2, 0):
                self.send_error(505,
                          "Invalid HTTP Version (%s)" % base_version_number)
                return False
        elif len(words) == 2:
            [command, path] = words
            self.close_connection = 1
            if command != 'GET':
                self.send_error(400,
                                "Bad HTTP/0.9 request type (%r)" % command)
                return False
        elif not words:
            return False
        else:
            self.send_error(400, "Bad request syntax (%r)" % requestline)
            return False
	self.command, self.path, self.version = command, path, version
	return True

    def handle_one_request(self):
        """Handle a single HTTP request.
	   Dispatch to the correct handler.
        """
        self.raw_requestline = self.rfile.readline()
	if not self.raw_requestline:
		self.close_connection = 1
		print "no requestline"
		return
	if not self.parse_rawline():
		print "could not parse rawline"
		return
        # self.parse_request(): # Do NOT parse here. the first line should be the only 
	for vdir in self.server.vdirs:
		p = vdir.matches(self.path)
		if p == False:
			continue
		if not self.in_handlers.has_key(p):
			self.in_handlers[p] = vdir.handler(noconnection(),self.client_address,self.server)
		hnd = self.in_handlers[p]
		hnd.rfile = self.rfile
		hnd.wfile = self.wfile
		self.rlpath = self.raw_requestline
		# FIXME: after one request, the rfile may still have buffer
		# data from previous one...
		npath = self.path[len(p):]
		if not npath.startswith('/'):
			npath = '/' + npath
		self._handle_one_foreign(hnd,npath)
		#print "Handled, closing = ", self.close_connection
		return
	# if no match:
        self.send_error(404, "Path not found: %s" % self.path)
        return

def server_run(options):
	httpd = HTTPServer((options.host,options.port),MultiHTTPHandler )
	httpd.vdirs =[ HTTPDir('/dir/',HTTPHandler), HTTPDir('/dir2/',HTTPHandler)]
	httpd.serve_forever()

server_run(options)

#eof
