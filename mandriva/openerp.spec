%define git_repo openerp
%define git_head tests-52

%define name openerp
%define release_class experimental

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

%define use_git_clone	0

%{?_without_kde:	%global build_kde 0}
%{?_with_kde:		%global build_kde 1}

%{?_without_web:	%global build_web 0}
%{?_with_web:		%global build_web 1}

%define __find_provides   %{u2p:%{_builddir}}/%{name}-%{git_get_ver}/mandriva/find-provides.sh
%define __find_requires   %{u2p:%{_builddir}}/%{name}-%{git_get_ver}/mandriva/find-requires.sh

%{?_use_clone:	%global use_git_clone 1}

Name:		%name
Version:	%{git_get_ver}
Release:	%mkrel %{git_get_rel2}
License:	AGPLv3+
Group:		Databases
Summary:	OpenERP Client and Server
URL:		http://www.openerp.com
Obsoletes:	tinyerp
%if ! %{use_git_clone}
Source:		%git_bs_source %{name}-%{version}.tar.gz
%endif
# BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	desktop-file-utils
Requires:	openerp-client, openerp-server
%if %{_target_vendor} == mandriva
BuildRequires:	 pygtk2.0-devel, pygtk2.0-libglade, python-libxslt
BuildRequires:	python-psycopg2, python-dot, python-pychart
%else 
%if %{_target_vendor} == redhat
BuildRequires:	 pygtk2-devel, libxslt-python, mx
%endif
%endif


%description
Open ERP is a free enterprise management software package. It
covers all domains for small to medium businesses; accounting,
stock management, sales, customer relationship, purchases,
project management...

%package client
Group:		Databases
Summary:	OpenERP Client
Requires:       pygtk2.0, pygtk2.0-libglade, python-dot
Requires:	python-matplotlib, python-egenix-mx-base
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
%if %{_target_vendor} == mandriva
Requires:       pygtk2.0, pygtk2.0-libglade
%if %mdkver > 200900
Requires:	python-hippo-canvas
%endif
%else 
%if %{_target_vendor} == redhat
Requires:       pygtk2, mx
%endif
%endif

%description client
Client components for Open ERP.

%if %{build_kde}
%package client-kde
Group:		Databases
Summary:	OpenERP Client (KDE)
Requires:       python-dot, python-pytz, python-kde4
Obsoletes:	ktiny
BuildRequires:	python-qt4
BuildRequires:	qt4-devel, kde4-macros
BuildRequires:  python-lxml
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
Group:		Databases
Summary:	Web Client of OpenERP, the Enterprise Management Software
#BuildRequires: ....
Requires:       python-pytz
Requires:       python-cherrypy, python-formencode
Requires:       python-simplejson, python-mako
Requires:	python-Babel

%description client-web
OpenERP Web is the web client of the OpenERP, a free enterprise management 
software: accounting, stock, manufacturing, project mgt...

%endif

%package server
Group:		System/Servers
Summary:	OpenERP Server
Requires:	pygtk2.0, pygtk2.0-libglade
Requires:	python-psycopg, python-libxslt, python-lxml
Requires:	postgresql-plpython >= 8.2
Requires:	python-imaging
Requires:	python-psycopg2, python-reportlab
Requires:       python-parsing
Suggests:	postgresql-server >= 8.2
Requires:	ghostscript
# perhaps the matplotlib could yield for pytz, in Mdv >=2009.0
Requires:	python-pyxml, python-matplotlib
Requires:	python-pychart, python-yaml, python-mako
Requires(pre):	rpm-helper
Requires(postun): rpm-helper

%description server
Server components for Open ERP.

IMPORTANT: Please read the INSTALL file in /usr/share/doc/openerp-server for
the first time run.

Note: at Mandriva 2008.1, python-pychart is needed from backports,
instead of the "pychart" package.

%package serverinit
Group:		Databases/Demo
Summary:	Full server Metapackage for OpenERP
Requires:       %{name}-server
Requires:	postgresql-server >= 8.2
Requires:	postgresql-plpgsql
Requires:	run-parts


%description serverinit
With this, all necessary packages and modules for a complete OpenERP server
are installed. This also triggers the installation of a PostgreSQL server.

%package alldemo
Group:		Databases/Demo
Summary:	Demo Metapackage for OpenERP
Requires:       %{name}-serverinit, %{name}-client
Requires: openerp-addons-account
Requires: openerp-addons-account_analytic_analysis
Requires: openerp-addons-account_asset
Requires: openerp-addons-account_chart
Requires: openerp-addons-account_greek_fiscal
Requires: openerp-addons-account_reporting
Requires: openerp-addons-account_simulation
Requires: openerp-addons-account_tax_include
Requires: openerp-addons-base
Requires: openerp-addons-base_contact
Requires: openerp-addons-base_iban
Requires: openerp-addons-base_setup
Requires: openerp-addons-base_vat
Requires: openerp-addons-board
Requires: openerp-addons-board_project
Requires: openerp-addons-crm
Requires: openerp-addons-crm_configuration
Requires: openerp-addons-document
Requires: openerp-addons-document_webdav
Requires: openerp-addons-event
Requires: openerp-addons-event_project
Requires: openerp-addons-hotel
Requires: openerp-addons-hotel_restaurant
Requires: openerp-addons-hr
Requires: openerp-addons-hr_attendance
Requires: openerp-addons-hr_expense
Requires: openerp-addons-hr_timesheet
Requires: openerp-addons-hr_timesheet_invoice
Requires: openerp-addons-hr_timesheet_sheet
Requires: openerp-addons-l10n_chart_gr
Requires: openerp-addons-mrp
Requires: openerp-addons-process
Requires: openerp-addons-product
Requires: openerp-addons-product_ean_always
Requires: openerp-addons-profile_hotel
Requires: openerp-addons-profile_service
Requires: openerp-addons-project
Requires: openerp-addons-project_event
Requires: openerp-addons-project_retro_planning
Requires: openerp-addons-purchase
Requires: openerp-addons-report_analytic_line
Requires: openerp-addons-report_analytic_planning
Requires: openerp-addons-report_crm
Requires: openerp-addons-report_task
Requires: openerp-addons-report_timesheet
Requires: openerp-addons-sale
Requires: openerp-addons-stock
Requires: openerp-addons-stock_location
Requires: openerp-addons-thunderbird

# Hint: issue 
# SELECT 'Requires: openerp-addons-' || name FROM ir_module_module  WHERE state = 'installed' ORDER BY name;
# to get the modules


%description alldemo
With this demo, all necessary packages and modules for a complete OpenERP server
and client are installed. The server also has a default database with some data.

%if %{use_git_clone}
%define modulize_g    -g %{_sourcedir}/%{name}-gitrpm.version
%endif

%prep
%if %{use_git_clone}
%git_clone_source
%git_prep_submodules
%else
%git_get_source_sm
%setup -q
%endif

echo "Preparing for addons build.."
./mandriva/modulize.py -C %{release_class} %modulize_g -x addons/server_modules.list addons/* > %{_specdir}/openerp-addons.spec
rm -f %{_builddir}/openerp-addons-$(./mandriva/modulize.py %modulize_g --onlyver)
ln -sf $(pwd)/addons %{_builddir}/openerp-addons-$(./mandriva/modulize.py %modulize_g --onlyver)
echo "Prepared addons"

echo "Preparing for extra addons build.."
./mandriva/modulize.py -C %{release_class} -n openerp-extra-addons %modulize_g -x addons/server_modules.list extra-addons/* > %{_specdir}/openerp-extra-addons.spec
rm -f %{_builddir}/openerp-extra-addons-$(./mandriva/modulize.py %modulize_g --onlyver)
ln -sf $(pwd)/extra-addons %{_builddir}/openerp-extra-addons-$(./mandriva/modulize.py %modulize_g --onlyver)
echo "Prepared extra addons"

echo "Preparing koo addons.."
./mandriva/modulize.py -n openerp-addons-koo %modulize_g -C %{release_class} -x addons/server_modules.list client-kde/server-modules/* > %{_specdir}/openerp-addons-koo.spec
rm -f %{_builddir}/openerp-addons-koo-$(./mandriva/modulize.py %modulize_g --onlyver)
ln -sf $(pwd)/client-kde/server-modules %{_builddir}/openerp-addons-koo-$(./mandriva/modulize.py %modulize_g --onlyver)

echo "Prepared koo addons."

%build
%if %{use_git_clone}
cd %{name}-%{version}
%endif

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
%{NoDisplay} python ./setup.py build
popd

%install
%if %{use_git_clone}
cd %{name}-%{version}
%endif
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
	%{NoDisplay} python ./setup.py install --root=%{buildroot}
popd
	#remove the default init script
rm %{buildroot}/usr/scripts/openerp-web

mv %{buildroot}/%{python_sitelib}/openerp  %{buildroot}/%{python_sitelib}/openerp-web
mv %{buildroot}/usr/config/openerp-web.cfg %{buildroot}/%{_sysconfdir}/openerp-web.cfg
mkdir -p %{buildroot}/%{_defaultdocdir}/%{name}-client-web-%{version}/
mv %{buildroot}/usr/doc/ChangeLog %{buildroot}/usr/doc/LICENSE.txt \
	%{buildroot}/usr/doc/README.txt \
	 %{buildroot}/%{_defaultdocdir}/%{name}-client-web-%{version}/

pushd %{buildroot}/%{python_sitelib}/locales
	rm -f messages.pot
	for LOCFI in */LC_MESSAGES/messages.mo ; do
		LFF=$(dirname "$LOCFI")
		if [ ! -d %{buildroot}/%{_prefix}/share/locale/$LFF ] ; then
			mkdir -p %{buildroot}/%{_prefix}/share/locale/$LFF
		fi
		mv $LOCFI %{buildroot}/%{_prefix}/share/locale/$LFF/openerp-web.mo
	done
popd
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
cat > %{buildroot}%{_datadir}/applications/mandriva-openerp-client.desktop << EOF
[Desktop Entry]
Version=1.0
Encoding=UTF-8
Name=Open ERP
GenericName=GTK ERP Client
Comment=A gtk client for the open source ERP
Exec=%{_bindir}/openerp-client
Icon=openerp-icon
Terminal=false
Type=Application
StartupNotify=true
Categories=Office;GNOME;GTK;X-MandrivaLinux-CrossDesktop;
EOF

%if %{build_kde}
cat > %{buildroot}%{_datadir}/applications/mandriva-koo.desktop << EOF
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
Categories=Office;KDE;X-MandrivaLinux-CrossDesktop;
EOF
%endif

mkdir -p %{buildroot}/%{_defaultdocdir}/%{name}-%{version}
pushd %{buildroot}/%{_defaultdocdir}
	if [ -d %{name}-server-* ] ; then
		mv %{name}-server-* %{name}-server-%{version}
	fi
	if [ -d %{name}-client-* ] ; then
		mv %{name}-client-* %{name}-client-%{version}
	fi
popd
install -m 644 -D server/doc/openerp-server.conf %{buildroot}%{_sysconfdir}/openerp-server.conf
install -m 755 -D server/doc/openerp-server.init %{buildroot}%{_initrddir}/openerp-server
install -m 644 -D server/doc/openerp-server.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/openerp-server
install -m 755 -D server/doc/README.urpmi %{buildroot}%{_defaultdocdir}/%{name}-%{version}/README.urpmi
install -m 755 -D server/doc/README.userchange %{buildroot}%{_defaultdocdir}/%{name}-server-%{version}/README.userchange

install -d %{buildroot}%{_sysconfdir}/openerp/start.d
install -d %{buildroot}%{_sysconfdir}/openerp/stop.d

install -m 750 -D server/bin/ssl/cert.cfg %{buildroot}%{_sysconfdir}/openerp/cert.cfg

install -m 644 server/bin/import_xml.rng %{buildroot}%{python_sitelib}/openerp-server/
# mv %{buildroot}%{_prefix}/import_xml.rng %{buildroot}%{python_sitelib}/openerp-server/

install -d %{buildroot}%{python_sitelib}/openerp-server/addons/base/security/
install -m 644 server/bin/addons/base/security/* %{buildroot}%{python_sitelib}/openerp-server/addons/base/security/

#temp fixes for alpha builds
pushd %{buildroot}%{python_sitelib}
	if [ -f openerp_client-*-py%{pyver}.egg-info ] ; then
		mv openerp_client-*-py%{pyver}.egg-info openerp_client-%{version}-py%{pyver}.egg-info
	fi
	if [ -f openerp_server-*-py%{pyver}.egg-info ] ; then
		mv openerp_server-*-py%{pyver}.egg-info openerp_server-%{version}-py%{pyver}.egg-info
	fi
popd

%if %{build_web}
 #some files for the web-client
install -D client-web/openerp-web.mdv %{buildroot}/%{_initrddir}/%{name}-web
%endif

mkdir -p %{buildroot}/var/log/openerp
mkdir -p %{buildroot}/var/spool/openerp
mkdir -p %{buildroot}/var/run/openerp

install -d %{buildroot}%{_defaultdocdir}/%{name}-server-%{version}/demo/
install -m 744 mandriva/prep_database.sh %{buildroot}%{_defaultdocdir}/%{name}-server-%{version}/demo/
install -m 644 mandriva/demodb.sql %{buildroot}%{_defaultdocdir}/%{name}-server-%{version}/demo/

pushd %{buildroot}%{_sysconfdir}/openerp/start.d
cat >30start-demo <<EOF 
#!/bin/bash

# service postgresql start

pushd %{_defaultdocdir}/%{name}-server-%{version}/demo/
    DB_NAME=dbdemo DB_RESTORESCRIPT=demodb.sql ./prep_database.sh
popd > /dev/null
# service openerp restart

EOF
popd

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_defaultdocdir}/%{name}-%{version}/README.urpmi

%if %{build_web}
%files client-web -f %{name}-%{version}/%{name}-web.lang
%doc
%defattr(-,root,root)
%{_bindir}/openerp-web
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
%{_iconsdir}/openerp-icon.png
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
%{_kde_iconsdir}/koo-icon.png
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

%files serverinit
%defattr(-,root,root)
	%dir 		%{_sysconfdir}/openerp/start.d/
	%dir 		%{_sysconfdir}/openerp/stop.d/

%files alldemo
%defattr(-,root,root)
	%dir		%{_defaultdocdir}/%{name}-server-%{version}/demo/
			%{_defaultdocdir}/%{name}-server-%{version}/demo/demodb.sql
			%{_defaultdocdir}/%{name}-server-%{version}/demo/prep_database.sh
%attr(0755,root,root)	%{_sysconfdir}/openerp/start.d/30start-demo
# todo: a few readme files, perhaps..

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
%{_mandir}/man1/openerp-server.*
%{py_puresitedir}/openerp_server-%{version}-py%{pyver}.egg-info
%{_mandir}/man5/openerp_serverrc.5*

%pre server
# todo: non-mandriva useradd
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

Recently, the OpenERP user has changed
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

%post serverinit
chkconfig postgresql on
chkconfig openerp-server on

%changelog -f %{_sourcedir}/%{name}-changelog.gitrpm.txt
