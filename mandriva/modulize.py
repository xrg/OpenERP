#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#
# Copyright P. Christeas <xrg@linux.gr> 2008-2013
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
# as published by the Free Software Foundation; version 2
# of the License.
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
# Convert an OpenERP/F3 module to RPM package

import sys
import os
#import glob
import re
import subprocess
import jinja2
from jinja2.utils import evalcontextfunction, contextfunction
import platform
import logging


from optparse import OptionParser

sys.path.insert(0, '.')
from modulize_utils import get_depends, get_module_info, get_ext_depends, get_extern_depends

parser = OptionParser()
parser.add_option("-q", "--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="don't print status messages to stderr")

parser.add_option("-d", "--debug",
                  action="store_true", dest="verbose", default=False,
                  help="verbose messages to stderr")

parser.add_option("-r", "--onlyver",
                  action="store_true", dest="onlyver", default=False,
                  help="Generates the version string and exits.")

parser.add_option("-R", "--onlyrel",
                  action="store_true", dest="onlyrel", default=False,
                  help="Generates the release string and exits.")

parser.add_option("-g", "--gitver",
                  dest="gitver",
                  help="Reads the version information from file",
                  metavar = "GITVER_FILE")

parser.add_option("-C", "--rclass", dest="rclass",
                  help="use RCLASS release class", metavar="RCLASS")

parser.add_option("-x", "--exclude-from",
                  dest="exclude",
                  help="Reads the file FROM_LIST and excludes those modules",
                  metavar = "FROM_LIST")
parser.add_option("-T", "--target-platform", help="Target platform or linux distro")


parser.add_option("-n", "--name",
                  dest="name",
                  help="The name of the base package (openerp-addons)",
                  metavar = "NAME")
parser.add_option("--skip-unnamed", dest="skip_unnamed", action="store_true", default=False,
                  help="Relax checks and tolerate name errors, skipping addons")

(options, args) = parser.parse_args()

level = logging.INFO
if options.quiet:
    level = logging.WARNING
elif options.verbose:
    level = logging.DEBUG

logging.basicConfig(level=level)
del level
log = logging.getLogger('modulize')

class release:
    version = '4.3.x'
    release = '1'
    def __init__(self, gitver=None):
        #sys.stderr.write("Init\n")
        self.version = ''
        self.subver = ''
        self.release = ''
        self.extraver = None
        self.mainver = ''
        if gitver:
            try:
                f = open(gitver, 'rb')
                for line in f:
                    if not ':' in line:
                        continue
                    key, val = line.split(':',1)
                    val = val.strip()
                    if key == 'Version':
                        self.version = val
                    elif key == 'Release':
                        self.release = val
                    elif key == 'Extra':
                        self.extraver = val
                f.close()
                log.info("Got version from file: v: %s (%s) , r: %s", self.version,self.subver,self.release)
            except Exception:
                log.exception("Get release exception: ")
        else:
            try:
                p = subprocess.Popen(["git", "describe", "--tags"], bufsize=4096, \
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
                (child_stdout, child_stdin) = (p.stdout, p.stdin)
                rescode = p.wait()
                if rescode != 0 : raise subprocess.CalledProcessError, rescode
                res= child_stdout.read()
                #sys.stderr.write("Git version: %s\n" % res)
                resc = res.split('-')
                if re.match('g.*',resc[len(resc)-1]) :
                    resc.pop()
                if len(resc)>1 :
                    self.release = resc.pop().strip()
                else:
                    self.release = '0'
                self.version = resc[0].lstrip('v')
                if self.version:
                    ma = re.match(r'([0-9\.]+)([a-z][\w]+)?',
                                self.version)
                    if ma:
                        self.version = ma.group(1)
                        self.extraver = ma.group(2)

                self.subver ="-".join(resc[1:])
                log.info("Got version from git: v: %s (%s) , r: %s", self.version,self.subver,self.release)
            except Exception:
                log.exception("Get release exception:")

        self.mainver = '.'.join(self.version.split('.')[:2])
        self.extrarel = ''
        if self.extraver:
            self.extrarel += '0.'+ self.extraver + '.'
        self.extrarel += self.release

rel = release(options.gitver)

info_dirs = []
no_dirs = []

if ( options.onlyver):
    print rel.mainver+rel.subver
    exit(0)

if ( options.onlyrel):
    print rel.extrarel
    exit(0)

class SysInfo(object):
    def __init__(self, options):
        self.__options = options
        
    def _init_platform(self):
        if platform.system() == 'Linux':
            if not self.__options.target_platform:
                self.target_platform = platform.linux_distribution()[0].lower()
                # It's your responsibility to adapt to each version!
            else:
                self.target_platform = self.__options.target_platform
        else:
            raise RuntimeError("Unsupported system: %s" %  platform.system())

        log.debug("Target platform: %s", self.target_platform)

    def init_all(self):
        self._init_platform()

class InfoDir(object):
    def __init__(self, info, parent):
        self.__info = info
        self.__parent = parent

    @property
    def name(self):
        return self.__info['dir']

    @property
    def info(self):
        return self.__info['info']

    @property
    def installable(self):
        return self.__info['info'].get('installable', True)

    @contextfunction
    def get_depends(self, context):
        return get_depends(self.__info['info']['depends'], self.__parent.allnames,
                    oname=context['name'])

    @property
    def ext_deps(self):
        return self.__info['ext_deps']

    def get_website(self):
        ws = self.__info['info']['website']
        if ',' in ws:
            ws = ws.split(', ')[0].strip()
        if '- ' in ws:
            ws = ws.split('- ')[0].strip()
        return ws

class InfoDirList(object):
    def __init__(self, options, args, rel):
        self._info_dirs = []
        self.no_dirs = []
        self.exclude_modules = []
        self.allnames = set()
        self._rel = rel
        self.scan(options, args)
        
    def scan(self, options, args):
        if options.exclude and len(options.exclude):
            log.debug("Scanning excludes from: %s", options.exclude)
            f = open(options.exclude,'r')
            mods = f.readlines()
            for mname in mods:
                mname = mname.strip()
                if not mname:
                    continue
                self.exclude_modules.append(mname)
            f.close()
            log.debug("Excludes loaded: %d", len(self.exclude_modules))

        for tdir in args:
            bdir = os.path.basename(tdir)
            if bdir in self.exclude_modules:
                self.no_dirs.append(bdir)
                continue
            if not os.path.isdir(tdir):
                log.debug("Path \"%s\" is not a dir", tdir)
                self.no_dirs.append(bdir)
                continue

            log.debug("Scanning module: %s", tdir)
            info = get_module_info(tdir, self._rel)
            if not (info and info.get('installable',True)):
                self.no_dirs.append(bdir)
            elif not (options.skip_unnamed or info.get('name', False)):
                # bail out when an unnamed module exists
                raise Exception("Addon %s should specify a name for summary!" % tdir)
            else:
                ext_deps = ''
                # TODO more like a list, cross-distro
                try:
                    if 'ext_depends' in info:
                        #if True:
                        #    raise ValueError("Deprecated ext_depends keyword found")
                        ext_deps += get_ext_depends(info['ext_depends'])
                        
                    if 'external_dependencies' in info:
                        ext_deps += get_extern_depends(info['external_dependencies'])
                except ValueError, e:
                    sys.stderr.write("Cannot use %s module: %s\n" % (tdir, e))
                    self.no_dirs.append(bdir)
                    continue

                for field in ('name', 'description', 'author'):
                    if isinstance(info.get(field, False), str):
                        info[field] = info[field].decode('utf-8')

                self._info_dirs.append({'dir': bdir.decode('utf-8'), 'info': info, 'ext_deps': ext_deps})

        # compute all the names
        self.allnames = set(map(lambda i: i['dir'], self._info_dirs))


    def __iter__(self):
        for info in self._info_dirs:
            if not info['info'].get('name', False):
                continue
            yield InfoDir(info, self)

    def __len__(self):
        return len(self._info_dirs)

try:
    our_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    floader = jinja2.FileSystemLoader(os.path.join(our_dir, 'templates'))
    env = jinja2.Environment(loader=floader, trim_blocks=True,
                extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols', 'jinja2.ext.with_'])
    sys_info = SysInfo(options)
    sys_info.init_all()
    mod_dirs = InfoDirList(options, args, rel)
    tmpl = env.get_template(sys_info.target_platform + '.tmpl.spec')
    res = tmpl.render(system=sys_info, args=args, rel=rel, modules=mod_dirs,
                release_class=options.rclass or 'pub',
                name=options.name or 'openerp-addons' )
    print res.encode('utf-8')

    log.info("Modules created: %d", len(mod_dirs))
except Exception:
    log.exception("Fail:")
    exit(-1)


#sys.stderr.write("Don't forget to create the archive, with:\n" \
        #"git archive --format=tar --prefix=openerp-addons-%s/ HEAD | gzip -c > openerp-addons-%s.tar.gz\n" \
        #% (rel.version.rsplit('.', 1)[0],rel.version.rsplit('.', 1)[0]));
#eof
