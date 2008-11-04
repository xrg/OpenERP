%define git_repo openerp
%define git_head HEAD

%define name openerp
#define version %
#define release %{git_get_rel}

%{?!pyver: %define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}


Name:		%name
Version:	%{git_get_ver}
Release:	%{git_get_rel}xrg
License:	GPLv2+
Group:		Databases
Summary:	ERP Client
URL:		http://www.openerp.com
Obsoletes:	tinyerp
# BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:	noarch
BuildRequires:	python, pygtk2.0-devel, pygtk2.0-libglade, python-libxslt
BuildRequires:	python-psycopg, python-dot
BuildRequires:	desktop-file-utils
Requires:       pygtk2.0, pygtk2.0-libglade
Requires:	openerp-client, openerp-server

%description
Open ERP is a free enterprise management software package. It
covers all domains for small to medium businesses; accounting,
stock management, sales, customer relationship, purchases,
project management...

%package client
Group:		Databases
Summary:	ERP Client
Requires:       pygtk2.0, pygtk2.0-libglade, python-dot, python-pytz
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description client
Client components for Open ERP.

%package client-kde
Group:		Databases
Summary:	ERP Client (KDE)
Requires:       python-dot, python-pytz, python-kde
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description client-kde
KDE client components for Open ERP.

%package server
Group:		System/Servers
Summary:	ERP Server
Requires:	pygtk2.0, pygtk2.0-libglade
Requires:	python-psycopg, python-libxslt, python-lxml
Requires:	postgresql-plpython >= 8.2
Requires:	python-imaging
Requires:	python-psycopg, python-reportlab
Requires:	graphviz, python-parsing
Requires:	postgresql-server >= 8.2
Requires:	ghostscript
Requires(pre):	rpm-helper
Requires(postun): rpm-helper

%description server
Server components for Open ERP.

IMPORTANT: Please read the INSTALL file in /usr/share/doc/openerp-server for
the first time run.

%prep
%git_clone_source
%git_prep_submodules

%build
cd %{name}-%{version}
pushd client
# %{_xvfb} :69 -nolisten tcp -ac -terminate &
DISPLAY= python ./setup.py build
popd

pushd client-kde
# %{_xvfb} :69 -nolisten tcp -ac -terminate &
DISPLAY= python ./setup.py build
popd

pushd server
DISPLAY= python ./setup.py build
popd

%install
cd %{name}-%{version}
rm -rf $RPM_BUILD_ROOT
pushd client
	DISPLAY= python ./setup.py install --root=$RPM_BUILD_ROOT
popd

pushd client-kde
	DISPLAY= python ./setup.py install --root=$RPM_BUILD_ROOT
popd

pushd server
	DISPLAY= python ./setup.py install --root=$RPM_BUILD_ROOT
popd
%find_lang %{name}-client

%find_lang ktiny

mv $RPM_BUILD_ROOT/%{_datadir}/openerp-client/* $RPM_BUILD_ROOT/%{python_sitelib}/openerp-client
rm -rf $RPM_BUILD_ROOT/%{_datadir}/openerp-client

mkdir $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Open ERP
Comment=Open Source ERP Client
Exec=%{_bindir}/%{name}
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=GNOME;GTK;Databases;
EOF

cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-ktiny.desktop << EOF
[Desktop Entry]
Name=Open ERP
Comment=Open Source ERP Client (KDE)
Exec=%{_bindir}/ktiny
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=KDE;Databases;
EOF

mkdir -p $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-%{version}
mv $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-server-5.0.0-alpha $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-server-%{version}
mv $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-client-5.0.0-alpha $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-client-%{version}
install -m 644 -D server/doc/openerp-server.conf $RPM_BUILD_ROOT%{_sysconfdir}/openerp-server.conf
install -m 755 -D server/doc/openerp-server.init $RPM_BUILD_ROOT%{_initrddir}/openerp-server
install -m 644 -D server/doc/openerp-server.logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/openerp-server
install -m 755 -D server/doc/README.urpmi $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}-%{version}/README.urpmi

#install -m 644 server/bin/import_xml.rng $RPM_BUILD_ROOT%{python_sitelib}/openerp-server/
mv $RPM_BUILD_ROOT%{_prefix}/import_xml.rng $RPM_BUILD_ROOT%{python_sitelib}/openerp-server/

install -d $RPM_BUILD_ROOT%{python_sitelib}/openerp-server/addons/base/security/
install -m 644 server/bin/addons/base/security/* $RPM_BUILD_ROOT%{python_sitelib}/openerp-server/addons/base/security/

#temp fixes for alpha builds
pushd $RPM_BUILD_ROOT%{python_sitelib}
	mv openerp_client-5.0.0_alpha-py2.5.egg-info openerp_client-%{version}-py2.5.egg-info
	mv openerp_server-5.0.0_alpha-py2.5.egg-info openerp_server-%{version}-py2.5.egg-info
popd

mkdir -p $RPM_BUILD_ROOT/var/log/openerp
mkdir -p $RPM_BUILD_ROOT/var/spool/openerp
mkdir -p $RPM_BUILD_ROOT/var/run/openerp

%clean
rm -rf $RPM_BUILD_ROOT
%files
%defattr(-,root,root)
%{_defaultdocdir}/%{name}-%{version}/README.urpmi

%files client -f %{name}-%{version}/%{name}-client.lang
%doc
%defattr(-,root,root)
%{_bindir}/openerp-client
%{python_sitelib}/openerp-client/
%{_defaultdocdir}/%{name}-client-%{version}/
%{_mandir}/man1/openerp-client.*
%{_datadir}/pixmaps/openerp-client/
%{_datadir}/applications/mandriva-%{name}.desktop
%{py_puresitedir}/openerp_client-%{version}-py2.5.egg-info

%files client-kde -f %{name}-%{version}/ktiny.lang
%doc
%defattr(-,root,root)
%{_bindir}/ktiny
%{python_sitelib}/ktiny/
%{_defaultdocdir}/ktiny/
%{_mandir}/man1/ktiny.*
%{_datadir}/ktiny/
%{_datadir}/applications/mandriva-ktiny.desktop
%{py_puresitedir}/ktiny-*-py2.5.egg-info

%post client
%{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null

%postun client
if [ -x %{_bindir}/update-desktop-database ]; then %{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null ; fi

%files server
%defattr(-,root,root)
%attr(0755,tinyerp,tinyerp) %dir /var/log/openerp
%attr(0755,tinyerp,tinyerp) %dir /var/spool/openerp
%attr(0755,tinyerp,tinyerp) %dir /var/run/openerp
%{_initrddir}/openerp-server
%attr(0644,tinyerp,tinyerp) %config(noreplace) %{_sysconfdir}/openerp-server.conf
%attr(0644,tinyerp,tinyerp) %config(noreplace) %{_sysconfdir}/logrotate.d/openerp-server
%{_bindir}/openerp-server
%{python_sitelib}/openerp-server/
%{_defaultdocdir}/%{name}-server-%{version}/
%{_mandir}/man1/openerp-server.*
%{py_puresitedir}/openerp_server-%{version}-py2.5.egg-info
%{_mandir}/man5/openerp_serverrc.5*

%pre server
%_pre_useradd tinyerp /var/spool/openerp /sbin/nologin

%post server
%_post_service openerp-server

%preun server
%_preun_service openerp-server

%postun server
%_postun_service openerp-server
%_postun_userdel tinyerp
