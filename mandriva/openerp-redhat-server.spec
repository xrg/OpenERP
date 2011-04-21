# Redhat, crippled, static version of the spec file


%if 1
# Where is that officially defined?
    %define _iconsdir %{_datadir}/icons
%endif

%define tarball_extra -4-g0e50801

Name:		openerp-server
Version:	6.0.2
Release:	4%{?dist}
License:	AGPLv3
Group:		System Environment/Daemons
Summary:	OpenERP Server
URL:		http://www.openerp.com
Source0:	http://www.openerp.com/download/stable/source/%{name}-%{version}%{tarball_extra}.tar.gz
#                   All non-official patches are contained in:
#                   http://git.hellug.gr/?p=xrg/openerp  and referred submodules
#                   look for the ./mandriva folder there, where this .spec file is held, also.
Source2:	openerp-server-check.sh
Patch0: 	openerp-server-init.patch
# BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	desktop-file-utils, python-setuptools
BuildRequires:	pygtk2-devel, libxslt-python
BuildRequires:	python2-devel
Requires:	python-lxml
Requires:	python-imaging
Requires:	python-psycopg2, python-reportlab
Requires:       pyparsing
# Suggests:	postgresql-server >= 8.2
Requires:	ghostscript
# perhaps the matplotlib could yield for pytz, in Mdv >=2009.0
Requires:	PyXML
# Requires: python-matplotlib
Requires:	PyYAML, python-mako
Requires:	pychart
Requires(post):	chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts

%description
Server component for Open ERP.

%prep
%setup -q

# I don't understand why this is needed at this stage
rm -rf win32 debian setup.nsi

# Hope that the upstream one will do.
rm -rf bin/pychart

%patch -P0 -p1

# Remove prebuilt binaries
pushd bin/addons
    rm -f outlook/plugin/openerp-outlook-addin.exe \
	thunderbird/plugin/openerp_plugin.xpi

# Well, we'd better exclude all the client-side plugin, until
# we can build it under Fedora (doubt it).
    rm -rf outlook/plugin/
    
# Remove unwanted files in addons
    rm -f .bzrignore
    
popd

# Tmp, as long as server-check is not in official sources:
mkdir -p tools/
cp %{SOURCE2} tools/server-check.sh


%build
NO_INSTALL_REQS=1 python ./setup.py build --quiet

# TODO: build the thunderbird plugin and the report designer

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

mkdir -p %{buildroot}/%{_sysconfdir}

python ./setup.py install --root=%{buildroot}

# the Python installer plants the RPM_BUILD_ROOT inside the launch scripts, fix that:
pushd %{buildroot}/%{_bindir}/
	for BIN in %{name} ; do
		mv $BIN $BIN.old
		cat $BIN.old | sed "s|%{buildroot}||" > $BIN
		chmod a+x $BIN
		rm $BIN.old
	done
popd

# When setup.py copies files, it removes the executable bit, so we have to
# restore it here for some scripts:
pushd %{buildroot}%{python_sitelib}/%{name}/
    chmod a+x addons/document_ftp/ftpserver/ftpserver.py \
	addons/document/odt2txt.py \
	addons/document/test_cindex.py \
	addons/document_webdav/test_davclient.py \
	addons/email_template/html2text.py \
	addons/mail_gateway/scripts/openerp_mailgate/openerp_mailgate.py \
	addons/wiki/web/widgets/rss/feedparser.py openerp-server.py \
	report/render/rml2txt/rml2txt.py \
	tools/graph.py \
	tools/which.py
popd

# Install the init scripts and conf
install -m 644 -D doc/openerp-server.conf %{buildroot}%{_sysconfdir}/openerp-server.conf
install -m 755 -D doc/openerp-server.init %{buildroot}%{_initrddir}/openerp-server
install -m 644 -D doc/openerp-server.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/openerp-server

install -d %{buildroot}%{_sysconfdir}/openerp/start.d
install -d %{buildroot}%{_sysconfdir}/openerp/stop.d

install -m 644 bin/import_xml.rng %{buildroot}%{python_sitelib}/%{name}/

install -d %{buildroot}%{_libexecdir}/%{name}
install -m 744 tools/server-check.sh %{buildroot}%{_libexecdir}/%{name}/

install -d %{buildroot}%{python_sitelib}/openerp-server/addons/base/security/
install -m 644 bin/addons/base/security/* %{buildroot}%{python_sitelib}/openerp-server/addons/base/security/

install -d %{buildroot}/%{_datadir}/pixmaps/openerp-server
install -m 644 -D pixmaps/* %{buildroot}/%{_datadir}/pixmaps/openerp-server/

mkdir -p %{buildroot}/var/log/openerp
mkdir -p %{buildroot}/var/spool/openerp
mkdir -p %{buildroot}/var/run/openerp

%if 0
#Left here for future backporting
%clean
rm -rf %{buildroot}
%endif

%files
%defattr(-,root,root)
%doc LICENSE README doc/INSTALL doc/Changelog
%attr(0755,openerp,openerp) %dir /var/log/openerp
%attr(0755,openerp,openerp) %dir /var/spool/openerp
%attr(0755,openerp,openerp) %dir /var/run/openerp
%attr(0755,openerp,openerp) %dir %{_sysconfdir}/openerp
%{_initrddir}/openerp-server
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp-server.conf
%config(noreplace)	%{_sysconfdir}/logrotate.d/openerp-server
	%dir 		%{_sysconfdir}/openerp/start.d/
	%dir 		%{_sysconfdir}/openerp/stop.d/
%{_bindir}/openerp-server
%{python_sitelib}/openerp-server/
%dir %{_libexecdir}/%{name}
%attr(0755,root,root)	%{_libexecdir}/%{name}/server-check.sh
%{_datadir}/pixmaps/openerp-server/
%{_mandir}/man1/openerp-server.*
%{python_sitelib}/openerp_server-%{version}-py%{python_version}.egg-info
%{_mandir}/man5/openerp_serverrc.5*

%pre
    getent group openerp >/dev/null || groupadd -r openerp
    getent passwd openerp >/dev/null || \
        useradd -r -d /var/spool/openerp -s /sbin/nologin \
        -c "OpenERP Server" openerp
    exit 0

%post
# Trigger the server-check.sh the next time openerp-server starts
touch /var/run/openerp-server-check
/sbin/chkconfig --add openerp-server

%preun
if [ $1 = 0 ] ; then
    /sbin/service openerp-server stop >/dev/null 2>&1
    /sbin/chkconfig --del openerp-server
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service openerp-server condrestart >/dev/null 2>&1 || :
fi

%changelog
* Sat Apr 9 2011 P. Christeas <p_christ@hol.gr> 0037772
  + Redhat: more cleanup, offer default docs
  + Redhat: remove the kde client
  + Redhat: remove the serverinit sub-package
  + Redhat: cleanup macros, requires
  + Redhat: python build --quiet

* Fri Apr 8 2011 P. Christeas <p_christ@hol.gr> e7eab62
  + Radhat: 6.0.2-2 fix groups, cert script, changelog
  + Mandriva: a few changes in .spec file

* Mon Apr 4 2011 P. Christeas <p_christ@hol.gr> b4c22fc
  + redhat: update to 6.0.2
  + redhat: a couple of fixes for rpmlint
  + redhat: improvements at .spec to comply with Guidelines

* Sun Apr 3 2011 P. Christeas <p_christ@hol.gr> 45596e1
  + redhat: bring the server-check.sh and a patch for init.d
  + RedHat: cleanup the .spec file, fix dependencies

* Sat Apr 2 2011 P. Christeas <p_christ@hol.gr> 3a88941
  + mandriva: demote the class, again, to public

* Fri Apr 1 2011 P. Christeas <p_christ@hol.gr> 7d8252a
  + Mandriva: add some dependencies to .spec file
  + Update to 6.0.2+
  + Redhat spec: strip much of the mandriva logic, make it static
  + RPM: copy spec file from Mandriva/Mageia to RedHat

* Thu Mar 24 2011 P. Christeas <p_christ@hol.gr> b9154b0
  + Initialize submodule for 'libcli', the client library

* Mon Mar 21 2011 P. Christeas <p_christ@hol.gr> 469aa48
  + Remove tests/ , they are in the sandbox now.

* Sun Mar 20 2011 P. Christeas <p_christ@hol.gr> 067bf38
  + Add README about this repository

* Thu Mar 17 2011 P. Christeas <p_christ@hol.gr> 968601a
  + Rewrite last gtk-client patch for SpiffGtkWidgets setup
  + mandriva: require python-lxml for gtk client
  + Updated submodules addons, buildbot, client, client-kde, server
  + tests: one for mails, one to dump the doc nodes cache
  + git: Fix submodule URL of buildbot

* Wed Mar 9 2011 P. Christeas <p_christ@hol.gr> fed8f66
  + Updated submodules addons, client, client-kde, extra-addons, server

* Wed Feb 23 2011 P. Christeas <p_christ@hol.gr> 9beefb7
  + Updated submodules addons, client, client-kde, extra-addons, server

* Sat Feb 19 2011 P. Christeas <p_christ@hol.gr> 23f26ca
  + Updated submodules addons, buildbot, client, client-kde, client-web, extra-addons, server

* Fri Jan 21 2011 P. Christeas <p_christ@hol.gr> a1e11b1
  + Merge branch 'official' into xrg-60
  + RPM spec: adapt to official release, dirs have the right names now.

* Thu Jan 20 2011 P. Christeas <xrg@openerp.com> 939c332
  + Official Release 6.0.1 + debian changelogs

* Thu Jan 20 2011 P. Christeas <p_christ@hol.gr> 536461f
  + Merge release 6.0.1

* Wed Jan 19 2011 P. Christeas <p_christ@hol.gr> 4635463
  + Merge commit 'v6.0.0' into xrg-60
  + Merge 6.0.0 into xrg-60
  + Updated submodules addons, client, server
  + Release 6.0.0
  + RPM spec: have all-modules list, skip bad addons, skip server-check.sh
  + RPM: allow modulize.py to skip bad modules.
  + Reset submodules addons, client*, addons, server to official
  + Mandriva: let spec go closer to other RPM distros
  + Updated submodules addons, client, client-kde, client-web, extra-addons, server

* Sat Jan 15 2011 P. Christeas <p_christ@hol.gr> 7486fe9
  + Updated submodules addons, client, client-kde, client-web, server

* Thu Jan 13 2011 P. Christeas <p_christ@hol.gr> a9b50da
  + Updated submodule client, using improved installer

* Mon Jan 3 2011 P. Christeas <p_christ@hol.gr> bd6aa12
  + Version 6.0.0-rc2 with addons, client, client-web, server

* Sun Jan 2 2011 P. Christeas <p_christ@hol.gr> 7266984
  + Further attempt for a correct client-web installation.
  + client-web: fix installation, under "site-packages/openobject/"

