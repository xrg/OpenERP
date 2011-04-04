# Redhat, reduced, static version of the spec file
%define name openerp

%{?!pyver: %define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{?!py_puresitedir: %define py_puresitedir %(python -c 'import distutils.sysconfig; print distutils.sysconfig.get_python_lib()' 2>/dev/null || echo PYTHON-LIBDIR-NOT-FOUND)}

%define NoDisplay	NODISPLAY=n
%define build_kde	0
%define build_web	0

%{?_without_kde:	%global build_kde 0}
%{?_with_kde:		%global build_kde 1}

%{?_without_web:	%global build_web 0}
%{?_with_web:		%global build_web 1}

%{?_use_tarball: %global use_git_clone 0}

%define clone_prefixdir ./

%define _iconsdir %{_datadir}/icons
%define _kde_iconsdir %_kde_prefix/share/icons


Name:		%name
Version:	6.0.2
Release:	1
License:	AGPLv3
Group:		Other
Summary:	Client and Server for the OpenERP suite
URL:		http://www.openerp.com
Obsoletes:	tinyerp
Source0:	http://www.openerp.com/download/stable/source/%{name}-server-%{version}.tar.gz
Source1:	http://www.openerp.com/download/stable/source/%{name}-client-%{version}.tar.gz
#                   All non-official patches are contained in:
#                   http://git.hellug.gr/?p=xrg/openerp  and referred submodules
#                   look for the ./mandriva folder there, where this .spec file is held, also.
Source2:	openerp-server-check.sh
Patch0: 	openerp-server-init.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	desktop-file-utils, python-setuptools
Requires:	openerp-client, openerp-server
BuildRequires:	 pygtk2-devel, libxslt-python

%description
Open ERP is a free enterprise management software package. It
covers all domains for small to medium businesses; accounting,
stock management, sales, customer relationship, purchases,
project management...

%package client
# note: we want the gtk client even w/o GNOME full desktop
Group:		Office
Summary:	OpenERP Client
Requires:       pygobject2, pygtk2-libglade, pydot, python-lxml
# Requires:	python-matplotlib
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
Requires:	hippo-canvas-python
Requires:	python-dateutil
Requires:       pygtk2, mx

%description client
Client components for Open ERP.

%if %{build_kde}
%package client-kde
Group:		Office
Summary:	OpenERP Client (KDE)
Requires:       python-dot, python-pytz, python-kde4
Obsoletes:	ktiny
BuildRequires:	python-qt4
BuildRequires:	qt4-devel, kde4-macros
BuildRequires:  python-lxml, python-qt4-devel
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description client-kde
KDE client (aka. koo) components for Open ERP.

%package client-kde-apidoc
Group:		Documentation
Summary:	API documentation for ERP Client (KDE)

%description client-kde-apidoc
Technical documentation for the API of OpenERP KDE client (koo).
%endif

%if %{build_web}
%package client-web
Group:		Servers
Summary:	Web Client of OpenERP, the Enterprise Management Software
#BuildRequires: ....
Requires:       python-pytz
Requires:       python-cherrypy, python-formencode
Requires:       python-simplejson, python-mako
Requires:	python-Babel
Requires:	python-pkg-resources

%description client-web
OpenERP Web is the web client of the OpenERP, a free enterprise management 
software: accounting, stock, manufacturing, project management...

%endif

%package server
Group:		Servers
Summary:	OpenERP Server
Requires:	pygtk2, pygtk2-libglade
Requires:	python-lxml
Requires:	postgresql-plpython >= 8.2
Requires:	python-imaging
Requires:	python-psycopg2, python-reportlab
Requires:       pyparsing
# Suggests:	postgresql-server >= 8.2
Requires:	ghostscript
# perhaps the matplotlib could yield for pytz, in Mdv >=2009.0
Requires:	PyXML
# Requires: python-matplotlib
Requires:	PyYAML, python-mako
# Requires:	python-pychart # embedded, still

%description server
Server components for Open ERP.

%package serverinit
Group:		Servers
Summary:	Full server Metapackage for OpenERP
Requires:       %{name}-server
Requires:	postgresql-server >= 8.2


%description serverinit
With this, all necessary packages and modules for a complete OpenERP server
are installed. This also triggers the installation of a PostgreSQL server.

%prep
%setup -q -c
%setup -q -c -T -D -a1
mv openerp-server-%{version} server
mv openerp-client-%{version} client
pushd server
%patch -P0 -p1
popd

# Remove prebuilt binaries
pushd server/bin/addons
    rm -f outlook/plugin/openerp-outlook-addin.exe \
	thunderbird/plugin/openerp_plugin.xpi
popd

# Tmp, as long as server-check is not in official sources:
mkdir server/tools/
cp %{SOURCE2} server/tools/server-check.sh


%build

pushd client
	%{NoDisplay} python ./setup.py build
popd

%if %{build_kde}
pushd client-kde
	make
	%{NoDisplay} python ./setup.py build
popd
%endif

%if %{build_web}
pushd client-web
	%{NoDisplay} python ./setup.py build
popd
%endif

pushd server
	NO_INSTALL_REQS=1 %{NoDisplay} python ./setup.py build
popd

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

pushd client
	%{NoDisplay} python ./setup.py install --root=%{buildroot}
	install -D bin/pixmaps/openerp-icon.png %{buildroot}%{_iconsdir}/openerp-icon.png
popd

%if %{build_kde}
pushd client-kde
	%{NoDisplay} python ./setup.py install --root=%{buildroot}
	install -D Koo/ui/images/koo-icon.png %{buildroot}%{_kde_iconsdir}/koo-icon.png
popd
%endif

mkdir -p %{buildroot}/%{_sysconfdir}

%if %{build_web}
pushd client-web
# 	  First, compile all the i18n messages
	%{NoDisplay} python ./admin.py i18n -c ALL
	%{NoDisplay} python ./setup.py install --root=%{buildroot}
popd

#remove the default init script

pushd %{buildroot}/%{python_sitelib}
    mv addons openobject/addons
popd

if [ -d %{buildroot}/usr/doc/openerp-web ] ; then
    mkdir -p %{buildroot}/%{_defaultdocdir}/
    mv %{buildroot}/usr/doc/openerp-web/openerp-web.mdv.cfg %{buildroot}/%{_sysconfdir}/openerp-web.cfg
    mv %{buildroot}/usr/doc/openerp-web  %{buildroot}/%{_defaultdocdir}/%{name}-client-web-%{version}/
else
    mkdir -p %{buildroot}/%{_defaultdocdir}/%{name}-client-web-%{version}/
    pushd %{buildroot}/%{python_sitelib}/openobject/
	    mv doc/ChangeLog doc/LICENSE.txt doc/README.txt \
		    %{buildroot}/%{_defaultdocdir}/%{name}-client-web-%{version}/
	    mv doc/openerp-web.mdv.cfg %{buildroot}/%{_sysconfdir}/openerp-web.cfg
    popd
fi

%endif

pushd server
	%{NoDisplay} python ./setup.py install --root=%{buildroot}
popd

# the Python installer plants the RPM_BUILD_ROOT inside the launch scripts, fix that:
pushd %{buildroot}/%{_bindir}/
	for BIN in %{name}-server %{name}-client ; do
		mv $BIN $BIN.old
		cat $BIN.old | sed "s|%{buildroot}||" > $BIN
		chmod a+x $BIN
		rm $BIN.old
	done
popd

%find_lang %{name}-client

%if %{build_web}
%find_lang %{name}-web
%endif

%if %{build_kde}
%find_lang koo
%endif

mv %{buildroot}/%{_datadir}/openerp-client/* %{buildroot}/%{python_sitelib}/openerp-client
rm -rf %{buildroot}/%{_datadir}/openerp-client

mkdir %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/openerp-client.desktop << EOF
[Desktop Entry]
Version=1.0
Name=Open ERP
GenericName=GTK ERP Client
Comment=A gtk client for the open source ERP
Exec=%{_bindir}/openerp-client
Icon=openerp-icon
Terminal=false
Type=Application
StartupNotify=true
Categories=Office;GNOME;GTK;
EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/openerp-client.desktop

%if %{build_kde}
cat > %{buildroot}%{_datadir}/applications/openerp-koo.desktop << EOF
[Desktop Entry]
Version=1.0
Name=Open ERP
GenericName=OpenERP KDE Client
Comment=The KDE client for the open source ERP
Exec=%{_bindir}/koo
Icon=koo-icon
Terminal=false
Type=Application
StartupNotify=true
Categories=Office;KDE;
EOF
desktop-file-validate %{buildroot}%{_datadir}/applications/openerp-koo.desktop
%endif

# Make sure that all doc directories are like %{name}-foo-%{version}
mkdir -p %{buildroot}/%{_defaultdocdir}/%{name}-%{version}
pushd %{buildroot}/%{_defaultdocdir}
	if [ -d %{name}-server-* ] && [ %{name}-server-* != %{name}-server-%{version} ] ; then
		mv %{name}-server-* %{name}-server-%{version}
	fi
	if [ -d %{name}-client-web-* ] ; then
		# put it aside, first
		mv %{name}-client-web-* %{name}-clientweb-%{version}
	fi
	if [ -d %{name}-client-* ] && [ %{name}-client-* != %{name}-client-%{version} ] ; then
		mv %{name}-client-* %{name}-client-%{version}
	fi
	if [ -d %{name}-clientweb-%{version} ] ; then
		# now, move it to the right place
		mv %{name}-clientweb-%{version} %{name}-client-web-%{version}
	fi
popd

# Install the init scripts and conf
install -m 644 -D server/doc/openerp-server.conf %{buildroot}%{_sysconfdir}/openerp-server.conf
install -m 755 -D server/doc/openerp-server.init %{buildroot}%{_initrddir}/openerp-server
install -m 644 -D server/doc/openerp-server.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/openerp-server

install -m 644 -D server/README %{buildroot}%{_defaultdocdir}/%{name}-%{version}/README

install -d %{buildroot}%{_sysconfdir}/openerp/start.d
install -d %{buildroot}%{_sysconfdir}/openerp/stop.d

install -m 644 server/bin/import_xml.rng %{buildroot}%{python_sitelib}/openerp-server/
# mv %{buildroot}%{_prefix}/import_xml.rng %{buildroot}%{python_sitelib}/openerp-server/

install -d %{buildroot}%{_libexecdir}/%{name}-server
install -m 744 server/tools/server-check.sh %{buildroot}%{_libexecdir}/%{name}-server/

install -d %{buildroot}%{python_sitelib}/openerp-server/addons/base/security/
install -m 644 server/bin/addons/base/security/* %{buildroot}%{python_sitelib}/openerp-server/addons/base/security/

install -d %{buildroot}/%{_datadir}/pixmaps/openerp-server
install -m 644 -D server/pixmaps/* %{buildroot}/%{_datadir}/pixmaps/openerp-server/

#temp fixes for alpha builds (rename the .egg files to remove extra version decorators)
pushd %{buildroot}%{python_sitelib}
	if [ -r openerp_client-*-py%{pyver}.egg-info ] && \
	    [ openerp_client-*-py%{pyver}.egg-info != openerp_client-%{version}-py%{pyver}.egg-info ]; then
		mv openerp_client-*-py%{pyver}.egg-info openerp_client-%{version}-py%{pyver}.egg-info
	fi
	if [ -r openerp_server-*-py%{pyver}.egg-info ] && \
	    [ openerp_server-*-py%{pyver}.egg-info openerp_server-%{version}-py%{pyver}.egg-info ]; then
		mv openerp_server-*-py%{pyver}.egg-info openerp_server-%{version}-py%{pyver}.egg-info
	fi
popd

%if %{build_web}
#some files for the web-client
# TODO install -D client-web/scripts/init.d/openerp-web.mdv %{buildroot}/%{_initrddir}/%{name}-web
%endif

mkdir -p %{buildroot}/var/log/openerp
mkdir -p %{buildroot}/var/spool/openerp
mkdir -p %{buildroot}/var/run/openerp

# A script that will install the Postgres User, but *after* the database
# has started (even at %post it is too early, the cluster may not have started)
# This will run at "/etc/init.d/openerp-server start" time
pushd %{buildroot}%{_sysconfdir}/openerp/start.d
cat > 10server-check <<EOF
#!/bin/sh

%{_libexecdir}/%{name}-server/server-check.sh -s

EOF
popd

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_defaultdocdir}/%{name}-%{version}/README

%if %{build_web}
%files client-web -f %{clone_prefixdir}%{name}-web.lang
%doc
%defattr(-,root,root)
%attr(0755,root, root) %{_bindir}/openerp-web
%attr(0755,root,root) %{_initrddir}/openerp-web
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp-web.cfg
%{python_sitelib}/openobject/
%{_defaultdocdir}/%{name}-client-web-%{version}/
%{py_puresitedir}/openerp_web-*-py%{pyver}.egg-info
%endif

%files client -f %{clone_prefixdir}%{name}-client.lang
%doc
%defattr(-,root,root)
%{_bindir}/openerp-client
%{_iconsdir}/openerp-icon.png
%{python_sitelib}/openerp-client/
%{_defaultdocdir}/%{name}-client-%{version}/
%{_mandir}/man1/openerp-client.*
%{_datadir}/pixmaps/openerp-client/
%{_datadir}/applications/openerp-client.desktop
%{py_puresitedir}/openerp_client-%{version}-py%{pyver}.egg-info

%if %{build_kde}
%files client-kde -f %{clone_prefixdir}koo.lang
%doc
%defattr(-,root,root)
%{_bindir}/koo
%{_kde_iconsdir}/koo-icon.png
%{python_sitelib}/Koo/
%{_defaultdocdir}/koo/
%exclude %{_defaultdocdir}/koo/api/
%{_mandir}/man1/koo.*
%{_datadir}/Koo/
%{_datadir}/applications/openerp-koo.desktop
%{py_puresitedir}/koo-*-py%{pyver}.egg-info

%files client-kde-apidoc
%defattr(-,root,root)
%{_defaultdocdir}/koo/api/
%endif

%files serverinit
%defattr(-,root,root)

%post client
%{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null

%postun client
if [ -x %{_bindir}/update-desktop-database ]; then %{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null ; fi

%files server
%defattr(-,root,root)
%attr(0755,openerp,openerp) %dir /var/log/openerp
%attr(0755,openerp,openerp) %dir /var/spool/openerp
%attr(0755,openerp,openerp) %dir /var/run/openerp
%attr(0750,openerp,openerp) %dir %{_sysconfdir}/openerp
# attr(0755,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp/cert.cfg
%{_initrddir}/openerp-server
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp-server.conf
%config(noreplace)	%{_sysconfdir}/logrotate.d/openerp-server
	%dir 		%{_sysconfdir}/openerp/start.d/
	%dir 		%{_sysconfdir}/openerp/stop.d/
%attr(0755,root,root)	%{_sysconfdir}/openerp/start.d/10server-check
%{_bindir}/openerp-server
%{python_sitelib}/openerp-server/
%dir %{_libexecdir}/%{name}-server
%attr(0755,root,root)	%{_libexecdir}/%{name}-server/server-check.sh
%{_datadir}/pixmaps/openerp-server/
%{_defaultdocdir}/%{name}-server-%{version}/
# exclude %{_defaultdocdir}/%{name}-server-%{version}/demo
%{_mandir}/man1/openerp-server.*
%{py_puresitedir}/openerp_server-%{version}-py%{pyver}.egg-info
%{_mandir}/man5/openerp_serverrc.5*

%pre server
#getent group GROUPNAME >/dev/null || groupadd -r GROUPNAME
    getent passwd openerp >/dev/null || \
        useradd -r -d /var/spool/openerp -s /sbin/nologin \
        -c "OpenERP Server" openerp

%post server
# *-*
if [ ! -r "%{_sysconfdir}/openerp/server.cert" ] ; then
	if [ ! -x "$(which certtool)" ] ; then
		echo "OpenERP server: certtool is missing. Cannot create SSL certificates"
	else
		pushd %{_sysconfdir}/openerp/
		if [ ! -r "server.key" ] ; then
			certtool -p --outfile server.key
		fi
		certtool -s --load-privkey server.key --outfile server.cert --template cert.cfg
		echo "Created a self-signed SSL certificate for OpenERP. You may want to revise it or get a real one."
		chown openerp:openerp server.cert server.key
		popd
	fi
fi

# Trigger the server-check.sh the next time openerp-server starts
touch /var/run/openerp-server-check

/sbin/chkconfig --add openerp-server

%preun server
if [ $1 = 0 ] ; then
    /sbin/service openerp-server stop >/dev/null 2>&1
    /sbin/chkconfig --del openerp-server
fi


%postun server
if [ "$1" -ge "1" ] ; then
    /sbin/service openerp-server condrestart >/dev/null 2>&1 || :
fi

%post serverinit
chkconfig postgresql on
chkconfig openerp-server on

%changelog -f %{_sourcedir}/%{name}-changelog.gitrpm.txt
