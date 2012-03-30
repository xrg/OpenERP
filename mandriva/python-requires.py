#!/usr/bin/python

# -*- encoding: utf-8 -*-

#
# Copyright P. Christeas <xrg@hellug.gr> 2008-2012
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

import sys
import os

import subprocess
import ConfigParser
import imp
import errno

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
(options, args) = parser.parse_args()


def get_module_info(tname):
    try:
        f = open(tname,"r")
        data = f.read()
        info = eval(data)
        #if 'version' in info:
        #   info['version'] = rel.version.rsplit('.', 1)[0] + '.' + info['version']+rel.subver
        f.close()
    except IOError:
        sys.stderr.write("Dir at %s may not be an OpenERP module.\n" % tname)
        return {}
    except:
        sys.stderr.write(str( sys.exc_info()))
        return {}
    return info

def get_ext_depends(deps):
    ret = []
    for dep in deps:
        if type(dep) == type(tuple()):
            ret.append(dep[0]+' '+ dep[1] + ' ' + dep[2])
        else:
            ret.append(dep)
    ret = set(ret)
    return ret

def which(dep, paths=[]):
    """ Locate `dep` among `paths`

        Note: paths will be preserved accross calls
    """

    if not paths:
        paths = [ p for p in os.environ['PATH'].split(':') \
                    if not p.startswith(('/usr/local','/home','/net','.')) ]

    for p in paths:
        needle = os.path.join(p, dep)
        if os.path.exists(needle):
            return needle

    raise IOError(errno.ENOENT, "Cannot locate binary %s" % dep)

ext_depends_parser = None

def init_ext_depends():
    global ext_depends_parser
    if ext_depends_parser:
        return

    ext_depends_parser = ConfigParser.SafeConfigParser()
    ext_depends_parser.optionxform = str # we want case-sensitive names
    ext_depends_parser.read(os.path.expanduser('~/.openerp/modulize-overrides.conf'))

def get_extern_depends(deps):
    global ext_depends_parser
    ret = []
    to_find = []
    init_ext_depends()
    if 'python' in deps:
        for dep in deps['python']:
            if ext_depends_parser and ext_depends_parser.has_option('python', dep):
                ret.append('Requires: %s' % ext_depends_parser.get('python', dep))
                continue
            try:
                res = imp.find_module(dep)
            except ImportError:
                raise ValueError("This system does not provide the %s python module" % dep)
            if not res:
                continue
            if res[1].startswith(('/usr/local','/home','/net','.')):
                raise ValueError("Required python package '%s' is at %s" % \
                                (dep, res[1]))

            to_find.append(res[1])
    if 'bin' in deps:
        for dep in deps['bin']:
            if ext_depends_parser and ext_depends_parser.has_option('bin', dep):
                ret.append('Requires: %s' % ext_depends_parser.get('bin', dep))
                continue
            try:
                to_find.append(which(dep))
            except EnvironmentError:
                raise ValueError("This system does not have the %s binary" % dep)

    for tf in to_find:
        try:
            res = subprocess.check_output(['rpm', '-q', \
                        '--queryformat=Requires: %{NAME}\\n',
                        '-f', tf], shell=False)
            ret.append(res.strip())
        except Exception, e:
            raise ValueError("Cannot locate dependency for %s: %s" %(tf, e))

    return ret

def get_depends(deps):
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
        info = get_module_info(tfile)
        if (info == {}):
                #no_dirs.append(bdir)
                pass
        else :
                openerp_provides.append(os.path.basename(os.path.dirname(tfile)))
                if 'depends' in info:
                        openerp_reqs.extend(get_depends(info['depends']))
                if 'ext_depends' in info:
                        ext_reqs.extend(get_ext_depends(info['ext_depends']))
                if 'external_dependencies' in info:
                        ext_reqs += get_extern_depends(info['external_dependencies'])

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
