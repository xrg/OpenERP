#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#
# Copyright P. Christeas <p_christ@hol.gr> 2008
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
# Convert an OpenERP module to RPM package

import imp
import sys
import os
import glob

from optparse import OptionParser

knight = """Name:	openerp-addons
Version:	%{git_get_ver}
Release:	%{git_get_rel}xrg
License:	GPLv2+
Group:		Databases
Summary:	ERP Client
URL:		http://www.openerp.com
Obsoletes:	tinyerp
BuildArch:	noarch

"""

class release:
	version = '4.3.x'

def get_module_info(name):
	try:
		f = open(os.path.join(name, '__terp__.py'),"r")
		data = f.read()
		info = eval(data)
		if 'version' in info:
			info['version'] = release.version.rsplit('.', 1)[0] + '.' + info['version']
		f.close()
	except IOError:
		print "Dir at %s may not be an OpenERP module." % name
		return {}
	except:
		print sys.exc_info()
		return {}
	return info

def get_depends(deps):
	ret = []
	for dep in deps:
		if dep == "base" : continue
		ret.append("openerp-addons-"+dep)
	ret = set(ret)
	if not ret : return ""
	return "Requires: %s \n" % (", ".join(ret))

def fmt_spec(name,info):
	""" Format the info object fields into a SPEC submodule section
	"""
	nii = "\n"
	nii += '%%package %s\n' % name;
	if 'version' in info:
		nii+= "Version: %s\n" % info['version']
	nii += """Group: Databases
Summary: %s
Requires: openerp-server = %s
""" % (info['name'], release.version.rsplit('.', 1)[0])
	if 'depends' in info:
		nii += get_depends(info['depends'])
	if 'author' in info:
		nii+= "Author: %s\n" % info['author']
	if 'website' in info:
		nii+= "URL: %s\n" % info['website']
	if 'description' in info:
		nii += "\n%%description %s\n%s\n" % (name, info['description'])
	else:
		nii += "\n%%description %s\n%s\n" % (name, info['name'])
	nii +="""
%%files %s
%%defattr(-,root,root)
%%{python_sitelib}/openerp-server/addons/%s
""" % (name, name)
	return nii

parser = OptionParser()
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

print knight

for tdir in args:
	info = get_module_info(tdir)
	print fmt_spec(os.path.basename(tdir),info)

#eof
