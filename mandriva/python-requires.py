#!/usr/bin/python
# -*- encoding: utf-8 -*-

#
# Copyright P. Christeas <xrg@hellug.gr> 2008-2013
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

''' A script that will parse files from the cmd line and, if they
   are OpenERP modules, it will list their provides
'''

import logging
import sys
import os

from optparse import OptionParser

sys.path.insert(0, '.')
from modulize_utils import get_module_info, get_ext_depends, get_extern_depends

parser = OptionParser()
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
(options, args) = parser.parse_args()

level = logging.WARNING
if options.verbose:
    level = logging.INFO

logging.basicConfig(level=level)
del level

def get_odepends(deps):
        ret = []
        for dep in deps:
                if dep == "base" : continue
                ret.append(dep)
        return set(ret)


openerp_reqs = []
openerp_provides = []
ext_reqs = []

for tfile in args:
        if os.path.basename(tfile) not in ('__terp__.py', '__openerp__.py'):
            continue
        tdir = os.path.dirname(tfile)
        info = get_module_info(tdir)
        if (info == {}):
                #no_dirs.append(bdir)
                pass
        else :
                openerp_provides.append(os.path.basename(os.path.dirname(tfile)))
                if 'depends' in info:
                        openerp_reqs.extend(get_odepends(info['depends']))
                if 'ext_depends' in info:
                        ext_reqs.append(get_ext_depends(info['ext_depends']))
                if 'external_dependencies' in info:
                        ext_reqs.append(get_extern_depends(info['external_dependencies']))

# Check if this package provides all the modules it would depend upon:

req_fail = []
for dep in openerp_reqs:
        if dep not in openerp_provides:
                req_fail.append(dep)

if len(req_fail):
        sys.stderr.write("Included modules do not contain these required ones:\n%s\n" % 
                ', '.join(req_fail))
        exit(1)

# Just print the external requires:
for d in ext_reqs:
        print d
