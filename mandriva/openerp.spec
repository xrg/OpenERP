%define git_repo openerp
%define git_head Fedora

%define name openerp
#define verstr 5.0.3-0
#define verstr2 5.0.3_0
#define release %{git_get_rel}

%define release_class fedora

%{?!pyver: %define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%if %{_target_vendor} == mandriva
%define NoDisplay	DISPLAY=

%if %mdkver > 200900
%define build_kde	1
%define build_web	0
%else
%define build_kde	0
%define build_web	0
%endif

%else
%define NoDisplay	NODISPLAY=n
%define build_kde	0
%define build_web	0
%endif


%{?_without_kde:	%global build_kde 0}
%{?_with_kde:		%global build_kde 1}

%{?_without_web:	%global build_web 0}
%{?_with_web:		%global build_web 1}

%define __find_provides   %{u2p:%{_builddir}}/%{name}-%{git_get_ver}/mandriva/find-provides.sh
%define __find_requires   %{u2p:%{_builddir}}/%{name}-%{git_get_ver}/mandriva/find-requires.sh


Name:		%name
Version:	%{git_get_ver}
Release:	%mkrel %{git_get_rel}
License:	GPLv2+
Group:		Databases
Summary:	ERP Client
URL:		http://www.openerp.com
Obsoletes:	tinyerp
# BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	desktop-file-utils
Requires:	openerp-client, openerp-server
%if %{_target_vendor} == mandriva
BuildRequires:	 pygtk2.0-devel, pygtk2.0-libglade, python-libxslt
BuildRequires:	python-psycopg2, python-dot, python-pychart
Requires:       pygtk2.0, pygtk2.0-libglade
%else 
%if %{_target_vendor} == redhat
BuildRequires:	 pygtk2-devel, libxslt-python, mx
Requires:       pygtk2, mx
%endif
%endif


%description
Open ERP is a free enterprise management software package. It
covers all domains for small to medium businesses; accounting,
stock management, sales, customer relationship, purchases,
project management...

%package client
Group:		Databases
Summary:	ERP Client
Requires:       pygtk2.0, pygtk2.0-libglade, python-dot
Requires:	python-matplotlib, python-egenix-mx-base
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description client
Client components for Open ERP.

%if %{build_kde}
%package client-kde
Group:		Databases
Summary:	ERP Client (KDE)
Requires:       python-dot, python-pytz, python-kde4
Obsoletes:	ktiny
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description client-kde
KDE client components for Open ERP.

%package client-kde-apidoc
Group:		Documentation
Summary:	API documentation for ERP Client (KDE)

%description client-kde-apidoc
Technical documentation for the API of OpenERP KDE client (koo).
%endif

%if %{build_web}
%package client-web
Group:		Databases
Summary:	Web Client of OpenERP, the Enterprise Management Software
#BuildRequires: ....
Requires:       python-pytz

%description client-web
OpenERP Web is the web client of the OpenERP, a free enterprise management 
software: accounting, stock, manufacturing, project mgt...
%endif

%package server
Group:		System/Servers
Summary:	ERP Server
Requires:	pygtk2.0, pygtk2.0-libglade
Requires:	python-psycopg, python-libxslt, python-lxml
Requires:	postgresql-plpython >= 8.2
Requires:	python-imaging
Requires:	python-psycopg2, python-reportlab
Requires:       python-parsing
Requires:	postgresql-server >= 8.2
Requires:	ghostscript
# perhaps the matplotlib could yield for pytz, in Mdv >=2009.0
Requires:	python-pyxml, python-matplotlib
Requires:	python-pychart
Requires(pre):	rpm-helper
Requires(postun): rpm-helper

%description server
Server components for Open ERP.

IMPORTANT: Please read the INSTALL file in /usr/share/doc/openerp-server for
the first time run.

Note: at Mandriva 2008.1, python-pychart is needed from backports,
instead of the "pychart" package.

%prep
%git_clone_source
%git_prep_submodules
%git_gen_changelog -n 100

echo "Preparing for addons build.."
./mandriva/modulize.py -C %{release_class} -x addons/server_modules.list addons/* > %{_specdir}/openerp-addons.spec
rm -f %{_builddir}/openerp-addons-$(./mandriva/modulize.py --onlyver)
ln -sf $(pwd)/addons %{_builddir}/openerp-addons-$(./mandriva/modulize.py --onlyver)
echo "Prepared addons"

echo "Preparing koo addons.."
./mandriva/modulize.py -n openerp-addons-koo -C %{release_class} -x addons/server_modules.list client-kde/server-modules/* > %{_specdir}/openerp-addons-koo.spec
rm -f %{_builddir}/openerp-addons-koo-$(./mandriva/modulize.py --onlyver)
ln -sf $(pwd)/client-kde/server-modules %{_builddir}/openerp-addons-koo-$(./mandriva/modulize.py --onlyver)

echo "Prepared koo addons."

%build
cd %{name}-%{version}
pushd client
	%{NoDisplay} python ./setup.py build
popd

%if %{build_kde}
pushd client-kde
	%{NoDisplay} python ./setup.py build
popd
%endif

%if %{build_web}
pushd client-web
	%{NoDisplay} python ./setup.py build
popd
%endif

pushd server
%{NoDisplay} python ./setup.py build
popd

%install
cd %{name}-%{version}
rm -rf $RPM_BUILD_ROOT
pushd client
	%{NoDisplay} python ./setup.py install --root=$RPM_BUILD_ROOT
popd

%if %{build_kde}
pushd client-kde
	%{NoDisplay} python ./setup.py install --root=$RPM_BUILD_ROOT
popd
%endif

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}

%if %{build_web}
pushd client-web
	%{NoDisplay} python ./setup.py install --root=$RPM_BUILD_ROOT
popd
	#remove the default init script
rm $RPM_BUILD_ROOT/usr/scripts/openerp-web

mv $RPM_BUILD_ROOT/%{python_sitelib}/openerp  $RPM_BUILD_ROOT/%{python_sitelib}/openerp-web
mv $RPM_BUILD_ROOT/usr/config/default.cfg $RPM_BUILD_ROOT/%{_sysconfdir}/openerp-web.cfg
mkdir -p $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-client-web-%{version}/
mv $RPM_BUILD_ROOT/usr/doc/CHANGES.txt $RPM_BUILD_ROOT/usr/doc/README.txt $RPM_BUILD_ROOT/usr/doc/LICENSE.txt \
	 $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-client-web-%{version}/

pushd $RPM_BUILD_ROOT/%{python_sitelib}/locales
	rm -f messages.pot
	for LOCFI in */LC_MESSAGES/messages.mo ; do
		LFF=$(dirname "$LOCFI")
		if [ ! -d $RPM_BUILD_ROOT/%{_prefix}/share/locale/$LFF ] ; then
			mkdir $RPM_BUILD_ROOT/%{_prefix}/share/locale/$LFF
		fi
		mv $LOCFI $RPM_BUILD_ROOT/%{_prefix}/share/locale/$LFF/openerp-web.mo
	done
popd
%endif

pushd server
	%{NoDisplay} python ./setup.py install --root=$RPM_BUILD_ROOT
popd

# the Python installer plants the RPM_BUILD_ROOT inside the launch scripts, fix that:
pushd $RPM_BUILD_ROOT/%{_bindir}/
	for BIN in %{name}-server %{name}-client ; do
		mv $BIN $BIN.old
		cat $BIN.old | sed "s|$RPM_BUILD_ROOT||" > $BIN
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

mv $RPM_BUILD_ROOT/%{_datadir}/openerp-client/* $RPM_BUILD_ROOT/%{python_sitelib}/openerp-client
rm -rf $RPM_BUILD_ROOT/%{_datadir}/openerp-client

mkdir $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-openerp-client.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=Open ERP
GenericName=Open Source ERP
Comment=Open Source ERP Client
Exec=%{_bindir}/openerp-client
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=Office;GNOME;GTK;
EOF

%if %{build_kde}
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-koo.desktop << EOF
[Desktop Entry]
Name=Open ERP
Comment=Open Source ERP Client (KDE)
Exec=%{_bindir}/ktiny
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=Office;KDE;
EOF
%endif

mkdir -p $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}-%{version}
pushd $RPM_BUILD_ROOT/%{_defaultdocdir}
	if [ -d %{name}-server-5.0.*-* ] ; then
		mv %{name}-server-5.0.*-* %{name}-server-%{version}
	fi
	if [ -d %{name}-client-5.0.*-* ] ; then
		mv %{name}-client-5.0.*-* %{name}-client-%{version}
	fi
popd
install -m 644 -D server/doc/openerp-server.conf $RPM_BUILD_ROOT%{_sysconfdir}/openerp-server.conf
install -m 755 -D server/doc/openerp-server.init $RPM_BUILD_ROOT%{_initrddir}/openerp-server
install -m 644 -D server/doc/openerp-server.logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/openerp-server
install -m 755 -D server/doc/README.urpmi $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}-%{version}/README.urpmi
install -m 755 -D server/doc/README.userchange $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}-server-%{version}/README.userchange

install -m 750 -D server/bin/ssl/cert.cfg $RPM_BUILD_ROOT%{_sysconfdir}/openerp/cert.cfg

install -m 644 server/bin/import_xml.rng $RPM_BUILD_ROOT%{python_sitelib}/openerp-server/
# mv $RPM_BUILD_ROOT%{_prefix}/import_xml.rng $RPM_BUILD_ROOT%{python_sitelib}/openerp-server/

install -d $RPM_BUILD_ROOT%{python_sitelib}/openerp-server/addons/base/security/
install -m 644 server/bin/addons/base/security/* $RPM_BUILD_ROOT%{python_sitelib}/openerp-server/addons/base/security/

#temp fixes for alpha builds
pushd $RPM_BUILD_ROOT%{python_sitelib}
	if [ -f openerp_client-5.0.*-*-py%{pyver}.egg-info ] ; then
		mv openerp_client-5.0.*-*-py%{pyver}.egg-info openerp_client-%{version}-py%{pyver}.egg-info
	fi
	if [ -f openerp_server-5.0.*-*-py%{pyver}.egg-info ] ; then
		mv openerp_server-5.0.*-*-py%{pyver}.egg-info openerp_server-%{version}-py%{pyver}.egg-info
	fi
popd

 #some files for the web-client
#install -D client-web/openerp-web.mdv $RPM_BUILD_ROOT/%{_initrddir}/%{name}-web

mkdir -p $RPM_BUILD_ROOT/var/log/openerp
mkdir -p $RPM_BUILD_ROOT/var/spool/openerp
mkdir -p $RPM_BUILD_ROOT/var/run/openerp

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_defaultdocdir}/%{name}-%{version}/README.urpmi

%if %{build_web}
%files client-web -f %{name}-%{version}/%{name}-web.lang
%doc
%defattr(-,root,root)
%{_bindir}/start-openerp-web
%attr(0755,root,root) %{_initrddir}/openerp-web
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp-web.cfg
%{python_sitelib}/openerp-web/
%{_defaultdocdir}/%{name}-client-web-%{version}/
%{py_puresitedir}/openerp_web-*-py%{pyver}.egg-info
%endif

%files client -f %{name}-%{version}/%{name}-client.lang
%doc
%defattr(-,root,root)
%{_bindir}/openerp-client
%{python_sitelib}/openerp-client/
%{_defaultdocdir}/%{name}-client-%{version}/
%{_mandir}/man1/openerp-client.*
%{_datadir}/pixmaps/openerp-client/
%{_datadir}/applications/mandriva-openerp-client.desktop
%{py_puresitedir}/openerp_client-%{version}-py%{pyver}.egg-info

%if %{build_kde}
%files client-kde -f %{name}-%{version}/koo.lang
%doc
%defattr(-,root,root)
%{_bindir}/koo
%{python_sitelib}/Koo/
%{_defaultdocdir}/koo/
%exclude %{_defaultdocdir}/koo/api/
%{_mandir}/man1/koo.*
%{_datadir}/Koo/
%{_datadir}/applications/mandriva-koo.desktop
%{py_puresitedir}/koo-*-py%{pyver}.egg-info

%files client-kde-apidoc
%defattr(-,root,root)
%{_defaultdocdir}/koo/api/
%endif

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
%attr(0755,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp/cert.cfg
%{_initrddir}/openerp-server
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp-server.conf
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/logrotate.d/openerp-server
%{_bindir}/openerp-server
%{python_sitelib}/openerp-server/
%{_defaultdocdir}/%{name}-server-%{version}/
%{_defaultdocdir}/%{name}-server-%{version}/README.userchange
%{_mandir}/man1/openerp-server.*
%{py_puresitedir}/openerp_server-%{version}-py%{pyver}.egg-info
%{_mandir}/man5/openerp_serverrc.5*

%pre server
%_pre_useradd openerp /var/spool/openerp /sbin/nologin

%post server
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

cat '-' <<EOF

Important NOTE:

As of this version, the OpenERP user has changed
 from "tinyerp" to "openerp" !


If you are upgrading from a previous build, please read 
%{_defaultdocdir}/%{name}-server-%{version}/README.userchange
and carefully follow those instructions to migrate your system!

EOF

%_post_service openerp-server

%preun server
%_preun_service openerp-server

%postun server
%_postun_service openerp-server
%_postun_userdel openerp

%changelog -f %{name}-%{version}/Changelog.git.txt