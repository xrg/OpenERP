%if %mdkversion
%if %mdkversion < 200700
# default to non-modular X on MDV < 200700
%define _modular_X 0%{?_with_modular_x:1}
%else
# default to modular X on MDV >= 200700
%define _modular_X 0%{!?_without_modular_x:1}
%endif
%else
# default to modular X elsewhere
%define _modular_X 0%{!?_without_modular_x:1}
%endif

%{?!pyver: %define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}


Name:		tinyerp
Version:	4.2.3
Release:	%mkrel 1
License:	GPLv2+
Group:		Databases
Summary:	ERP Client
URL:		http://tinyerp.org
Source0:	http://tinyerp.org/download/sources/tinyerp-server-%{version}.tar.bz2
Source1:	http://tinyerp.org/download/sources/tinyerp-client-%{version}.tar.bz2
Source2:	tinyerp-server.conf
Source3:	tinyerp-server.init
Source4:	tinyerp-server.logrotate
Source5:	tinyerp-README.urpmi
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:	noarch
BuildRequires:	python, pygtk2.0-devel, pygtk2.0-libglade, python-libxslt
BuildRequires:	python-psycopg, python-dot
BuildRequires:	desktop-file-utils
%if %_modular_X
BuildRequires:	x11-server-xvfb
%define _xvfb /usr/bin/Xvfb
%else
BuildRequires:	xorg-x11-Xvfb
%define _xvfb /usr/X11R6/bin/Xvfb
%endif
Requires:       pygtk2.0, pygtk2.0-libglade
Requires:	tinyerp-client, tinyerp-server
Patch0:		tinyerp-client.patch
Patch1:		tinyerp-server.patch

%description
Tiny ERP is a free enterprise management software package. It
covers all domains for small to medium businesses; accounting,
stock management, sales, customer relationship, purchases,
project management...

%package client
Group:		Databases
Summary:	ERP Client
Requires:       pygtk2.0, pygtk2.0-libglade, python-dot
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description client
Client components for Tiny ERP.

%package server
Group:		System/Servers
Summary:	ERP Server
Requires:	pygtk2.0, pygtk2.0-libglade
Requires:	python-psycopg, python-libxslt
Requires:	postgresql8.2-plpython
Requires:	python-imaging
Requires:	python-psycopg, python-reportlab
Requires:	graphviz, python-parsing, postgresql8.2-server
Requires:	ghostscript
Requires(pre):	rpm-helper
Requires(postun):	rpm-helper

%description server
Server components for Tiny ERP.

IMPORTANT: Please read the INSTALL file in /usr/share/doc/tinyerp-server for
the first
time run.

%prep
%setup -q -a 1 -c %{name}-%{version}
#%patch0
#%patch1

%build
cd client
%{_xvfb} :69 -nolisten tcp -ac -terminate &
DISPLAY=:69 ./setup.py build
cd ../server
DISPLAY=:69 ./setup.py build

%install
rm -rf $RPM_BUILD_ROOT
cd client
%{_xvfb} :69 -nolisten tcp -ac -terminate &
DISPLAY=:69 ./setup.py install --root=$RPM_BUILD_ROOT
cd ../server
DISPLAY=:69 ./setup.py install --root=$RPM_BUILD_ROOT
cd ..
%find_lang tinyerp-client

mv $RPM_BUILD_ROOT/%{_datadir}/tinyerp-client/* $RPM_BUILD_ROOT/%{python_sitelib}/tinyerp-client
rm -rf $RPM_BUILD_ROOT/%{_datadir}/tinyerp-client

mkdir $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Tiny ERP
Comment=Open Source ERP Client
Exec=%{_bindir}/%{name}
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=GNOME;GTK;Databases;
EOF

mkdir -p $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-%{version}
install -m 644 -D %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/tinyerp-server.conf
install -m 755 -D %{SOURCE3} $RPM_BUILD_ROOT%{_initrddir}/tinyerp-server
install -m 644 -D %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/tinyerp-server
install -m 755 -D %{SOURCE5} $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}-%{version}/README.urpmi
mkdir -p $RPM_BUILD_ROOT/var/log/tinyerp
mkdir -p $RPM_BUILD_ROOT/var/spool/tinyerp
mkdir -p $RPM_BUILD_ROOT/var/run/tinyerp

%clean
rm -rf $RPM_BUILD_ROOT
%files
%defattr(-,root,root)
%{_defaultdocdir}/%{name}-%{version}/README.urpmi

%files client -f %{name}-client.lang
%doc
%defattr(-,root,root)
%{_bindir}/tinyerp-client
%{python_sitelib}/tinyerp-client/
%{_defaultdocdir}/%{name}-client-%{version}/
%{_mandir}/man1/tinyerp-client.*
%{_datadir}/pixmaps/tinyerp-client/
%{_datadir}/applications/*.desktop
%{py_puresitedir}/tinyerp_client-%{version}-py2.5.egg-info

%post client
%{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null

%postun client
if [ -x %{_bindir}/update-desktop-database ]; then %{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null ; fi

%files server
%defattr(-,root,root)
%attr(0755,tinyerp,tinyerp) %dir /var/log/tinyerp
%attr(0755,tinyerp,tinyerp) %dir /var/spool/tinyerp
%attr(0755,tinyerp,tinyerp) %dir /var/run/tinyerp
%{_initrddir}/tinyerp-server
%attr(0644,tinyerp,tinyerp) %config(noreplace) %{_sysconfdir}/tinyerp-server.conf
%attr(0644,tinyerp,tinyerp) %config(noreplace) %{_sysconfdir}/logrotate.d/tinyerp-server
%{_bindir}/tinyerp-server
%{python_sitelib}/tinyerp-server/
%{_defaultdocdir}/%{name}-server-%{version}/
%{_mandir}/man1/tinyerp-server.*
%{py_puresitedir}/tinyerp_server-%{version}-py2.5.egg-info
%{_mandir}/man5/terp_serverrc.5*

%pre server
%_pre_useradd tinyerp /var/spool/tinyerp /sbin/nologin

%post server
%_post_service tinyerp-server

%preun server
%_preun_service tinyerp-server

%postun server
%_postun_service tinyerp-server
%_postun_userdel tinyerp
