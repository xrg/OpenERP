%define git_repo openerp
%define git_head HEAD

%global name openerp
%global release_class pub

%{?!pyver: %global pyver %(python -c 'import sys;print(sys.version[0:3])')}
%{?!python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{?!py_puresitedir: %global py_puresitedir %(python -c 'import distutils.sysconfig; print distutils.sysconfig.get_python_lib()' 2>/dev/null || echo PYTHON-LIBDIR-NOT-FOUND)}

%{?!auto_specdir: %global auto_specdir %{_specdir} }

%if %{_target_vendor} == mandriva
%global NoDisplay       DISPLAY=

%if %mdkver > 200900
%define build_kde       1
%define build_web       1
%else
%define build_kde       0
%define build_web       0
%endif
%global build_mdvmga    1
%else

%if %{_target_vendor} == mageia
%define NoDisplay       DISPLAY=

%define build_kde       1
%define build_web       1
%define build_mdvmga    1

%else
# Other distributions

%define NoDisplay       NODISPLAY=n
%define build_kde       0
%define build_web       0

%define build_mdvmga    0

%{?!_iconsdir %global _iconsdir %{_datadir}/icons }
%{?!_kde_iconsdir %global _kde_iconsdir %_kde_prefix/share/icons}
%endif
%endif

%define use_git_clone   1

%{?_without_kde:        %global build_kde 0}
%{?_with_kde:           %global build_kde 1}

%{?_without_web:        %global build_web 0}
%{?_with_web:           %global build_web 1}

%define _use_internal_dependency_generator 0
%define __find_provides   %{u2p:%{_builddir}}/%{name}-%{git_get_ver}/mandriva/find-provides.sh
%define __find_requires   %{u2p:%{_builddir}}/%{name}-%{git_get_ver}/mandriva/find-requires.sh

%{?_use_clone:  %global use_git_clone 1}
%{?_use_tarball: %global use_git_clone 0}

%if %{use_git_clone}
%global clone_prefixdir %{name}-%{version}/
%else
%global clone_prefixdir ./
%endif

%define scriptsdir      %{_sysconfdir}/%{name}
# Was %{_libexecdir}/%{name}-server/ , but mandriva uses _libdir :(

Name:           %name
Version:        %{git_get_ver}
Release:        %mkrel %{git_get_rel2}
License:        AGPLv3+
Group:          Databases
Summary:        Client and Server meta-package for the open source ERP
URL:            http://www.openerp.com
Obsoletes:      tinyerp <= 5.0
%if ! %{use_git_clone}
Source:         %git_bs_source %{name}-%{version}.tar.gz
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}
BuildArch:      noarch
BuildRequires:  python, python-setuptools
BuildRequires:  desktop-file-utils
%if %{build_mdvmga}
BuildRequires:   pygtk2.0-devel, pygtk2.0-libglade, python-libxslt
BuildRequires:  python-psycopg2, python-dot, python-pychart
%else 
%if %{_target_vendor} == redhat
BuildRequires:  pygtk2-devel, libxslt-python
BuildRequires:  python2-devel
%endif
%endif
Requires:       openerp-client, openerp-server

%description
Open ERP is a free enterprise management software package. It
covers all domains for small to medium businesses; accounting,
stock management, sales, customer relationship, purchases,
project management...

%package client
Group:          Databases
Summary:        GTK Client for the ERP
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
%if %{build_mdvmga}
Requires:       python-matplotlib
Requires:       python-dot, python-lxml
Requires:       pygtk2.0, pygtk2.0-libglade, python-egenix-mx-base
Requires:       python-dateutil
%if %mdkver > 200900
Requires:       python-hippo-canvas
%endif
%else 
%if %{_target_vendor} == redhat || %{_target_vendor} == pc
Requires:       pygtk2
Requires:       pygobject2, pygtk2-libglade, pydot, python-lxml
BuildRequires:  pygobject2
BuildRequires:  jpackage-utils
Requires:       hippo-canvas-python
Requires:       python-dateutil
%endif
%endif

%description client
Client components for Open ERP.

%if %{build_kde}
%package client-kde
Group:          Databases
Summary:        KDE Client for the ERP
Requires:       python-dot, python-pytz, python-kde4
Obsoletes:      ktiny <= 4.0
BuildRequires:  python-qt4
BuildRequires:  qt4-devel, kde4-macros
BuildRequires:  python-lxml, python-qt4-devel
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
Requires:       locales-kde

%description client-kde
KDE client (aka. koo) components for Open ERP.

%package client-kde-apidoc
Group:          Documentation
Summary:        API documentation for ERP Client (KDE)

%description client-kde-apidoc
Technical documentation for the API of OpenERP KDE client (koo).
%endif

%if %{build_web}
%package client-web
Group:          Databases
Summary:        Web Client, a web-interface server
#BuildRequires: ....
Requires:       python-cherrypy, python-formencode
Requires:       python-simplejson, python-mako
# BuildRequires:  python-cherrypy, python-formencode
# BuildRequires:  python-simplejson
%if %{build_mdvmga}
Requires:       python-pkg-resources
Requires:       python-pytz
Requires:       python-Babel
%else
Requires:       pytz
Requires:       python-babel
%endif

%description client-web
OpenERP Web is the web client of the OpenERP, a free enterprise management 
software: accounting, stock, manufacturing, project mgt...

%endif

%package server
Group:          System/Servers
Summary:        Server for the ERP (framework core)
Requires:       python-lxml
Requires:       postgresql >= 8.2
Requires:       python-imaging
Requires:       python-psycopg2, python-reportlab
Requires:       ghostscript
# perhaps the matplotlib could yield for pytz, in Mdv >=2009.0
%if %{build_mdvmga}
Requires:       python-matplotlib
Requires:       python-parsing, python-libxslt
Requires:       pygtk2.0, pygtk2.0-libglade
Requires:       python-pychart, python-yaml, python-mako
Requires(pre):  rpm-helper
Requires(postun): rpm-helper
%else
Requires:       python-dateutil
Requires:       ghostscript
Requires:       PyXML, PyYAML, python-mako
Requires:       pychart
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

%description server
Server components for Open ERP.

IMPORTANT: Please read the INSTALL file in /usr/share/doc/openerp-server for
the first time run.

Note: at Mandriva 2008.1, python-pychart is needed from backports,
instead of the "pychart" package.

%package serverinit
Group:          Applications/Databases

Summary:        Full server Metapackage, install and run
Requires:       %{name}-server
Requires:       postgresql-server >= 8.2
Requires:       postgresql-plpgsql
Requires:       run-parts


%description serverinit
With this, all necessary packages and modules for a complete OpenERP server
are installed. This also triggers the installation of a PostgreSQL server.

%package alldemo
Group:          Applications/Databases
Summary:        Demo Metapackage, preloads an example database
Requires:       %{name}-serverinit, %{name}-client
Requires: openerp-addons-account
Requires: openerp-addons-account_chart
Requires: openerp-addons-account_greek_fiscal
Requires: openerp-addons-base_contact
Requires: openerp-addons-base_iban
Requires: openerp-addons-base_setup
Requires: openerp-addons-base_vat
Requires: openerp-addons-crm
Requires: openerp-addons-document
Requires: openerp-addons-event
Requires: openerp-addons-event_project
Requires: openerp-addons-hr
Requires: openerp-addons-hr_attendance
Requires: openerp-addons-hr_expense
Requires: openerp-addons-hr_timesheet
Requires: openerp-addons-hr_timesheet_invoice
Requires: openerp-addons-hr_timesheet_sheet
Requires: openerp-addons-l10n_gr
Requires: openerp-addons-mrp
Requires: openerp-addons-process
Requires: openerp-addons-product
Requires: openerp-addons-project
Requires: openerp-addons-project_event
Requires: openerp-addons-project_retro_planning
Requires: openerp-addons-purchase
Requires: openerp-addons-sale
Requires: openerp-addons-stock
Requires: openerp-addons-stock_location

# Hint: issue 
# SELECT 'Requires: openerp-addons-' || name FROM ir_module_module  WHERE state = 'installed' ORDER BY name;
# to get the modules


%description alldemo
With this demo, all necessary packages and modules for a complete OpenERP
server and client are installed. The server also has a default database
with some data.

%global modulize_g    -g %{_sourcedir}/%{name}-gitrpm.version

%prep
%if %{use_git_clone}
%git_clone_source
%git_prep_submodules -f
%else
%git_get_source_sm
%setup -q
%endif

echo "Preparing for addons build.."
./mandriva/modulize.py -C %{release_class} %modulize_g -x addons/server_modules.list addons/* > %{auto_specdir}/openerp-addons.spec
rm -f %{_builddir}/openerp-addons-$(./mandriva/modulize.py %modulize_g --onlyver)
ln -sf $(pwd)/addons %{_builddir}/openerp-addons-$(./mandriva/modulize.py %modulize_g --onlyver)
echo "Prepared addons"

echo "Preparing for extra addons build.."
./mandriva/modulize.py -C %{release_class} -n openerp-extra-addons %modulize_g -x addons/server_modules.list extra-addons/* > %{auto_specdir}/openerp-extra-addons.spec
rm -f %{_builddir}/openerp-extra-addons-$(./mandriva/modulize.py %modulize_g --onlyver)
ln -sf $(pwd)/extra-addons %{_builddir}/openerp-extra-addons-$(./mandriva/modulize.py %modulize_g --onlyver)
echo "Prepared extra addons"

echo "Preparing koo addons.."
./mandriva/modulize.py -n openerp-addons-koo %modulize_g -C %{release_class} -x addons/server_modules.list client-kde/server-modules/* > %{auto_specdir}/openerp-addons-koo.spec
rm -f %{_builddir}/openerp-addons-koo-$(./mandriva/modulize.py %modulize_g --onlyver)
ln -sf $(pwd)/client-kde/server-modules %{_builddir}/openerp-addons-koo-$(./mandriva/modulize.py %modulize_g --onlyver)

echo "Prepared koo addons."

%build
%if %{use_git_clone}
cd %{name}-%{version}
%endif

pushd client
        %{NoDisplay} python ./setup.py build --quiet
popd

%if %{build_kde}
pushd client-kde
        make
        %{NoDisplay} python ./setup.py build --quiet
popd
%endif

%if %{build_web}
pushd client-web
        %{NoDisplay} python ./setup.py build --quiet
popd
%endif

pushd server
        NO_INSTALL_REQS=1 %{NoDisplay} python ./setup.py build --quiet
popd

%install
%if %{use_git_clone}
cd %{name}-%{version}
%endif

pushd client
        %{NoDisplay} python ./setup.py install --root=%{buildroot} --quiet
        install -D bin/pixmaps/openerp-icon.png %{buildroot}%{_iconsdir}/openerp-icon.png
popd

%if %{build_kde}
pushd client-kde
        %{NoDisplay} python ./setup.py install --root=%{buildroot} --quiet
        install -D Koo/ui/images/koo-icon.png %{buildroot}%{_kde_iconsdir}/koo-icon.png
popd
%endif

mkdir -p %{buildroot}%{_sysconfdir}

%if %{build_web}
pushd client-web
        %{NoDisplay} python ./setup.py install --root=%{buildroot} --quiet
popd

#remove the default init script

pushd %{buildroot}%{python_sitelib}
    mv addons openobject/addons
popd

if [ -d %{buildroot}/usr/doc/openerp-web ] ; then
    rm -rf %{buildroot}/usr/doc/openerp-web
fi

%endif

pushd server
        NO_INSTALL_REQS=1 %{NoDisplay} python ./setup.py install --root=%{buildroot} --quiet
popd

# the Python installer plants the RPM_BUILD_ROOT inside the launch scripts, fix that:
pushd %{buildroot}%{_bindir}/
        for BIN in %{name}-server %{name}-client ; do
                sed -i "s|%{buildroot}||" $BIN
        done
popd

%find_lang %{name}-client

%if %{build_kde}
%find_lang koo
%endif

mv %{buildroot}%{_datadir}/openerp-client/* %{buildroot}%{python_sitelib}/openerp-client
rm -rf %{buildroot}%{_datadir}/openerp-client

mkdir %{buildroot}%{_datadir}/applications || :
cat > %{buildroot}%{_datadir}/applications/openerp-client.desktop << EOF
[Desktop Entry]
Version=1.0
Name=Open ERP
Encoding=UTF-8
GenericName=GTK ERP Client
Comment=A gtk client for the open source ERP
Exec=%{_bindir}/openerp-client
Icon=openerp-icon
Terminal=false
Type=Application
StartupNotify=true
Categories=Office;GNOME;GTK;X-MandrivaLinux-CrossDesktop;
EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/openerp-client.desktop

%if %{build_kde}
cat > %{buildroot}%{_datadir}/applications/openerp-koo.desktop << EOF
[Desktop Entry]
Version=1.0
Name=Open ERP
Encoding=UTF-8
GenericName=OpenERP KDE Client
Comment=The KDE client for the open source ERP
Exec=%{_bindir}/koo
Icon=koo-icon
Terminal=false
Type=Application
StartupNotify=true
Categories=Office;KDE;X-MandrivaLinux-CrossDesktop;
EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/openerp-koo.desktop
%endif

# We remove the installed documentation dirs, because %doc will copy them again
pushd %{buildroot}%{_defaultdocdir}
        [ -d %{name}-server-* ] && rm -rf %{name}-server-*
        [ -d %{name}-client-web-* ] && rm -rf %{name}-client-web-*
        [ -d %{name}-client-* ] && rm -rf %{name}-client-*
        [ -d koo ] && rm -rf koo
popd

install -m 644 -D server/doc/openerp-server.conf %{buildroot}%{_sysconfdir}/openerp-server.conf
install -m 755 -D server/doc/openerp-server.init %{buildroot}%{_initrddir}/openerp-server
install -m 644 -D server/doc/openerp-server.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/openerp-server

install -d %{buildroot}%{_sysconfdir}/openerp/start.d
install -d %{buildroot}%{_sysconfdir}/openerp/stop.d

install -m 640 -D server/ssl-cert.cfg %{buildroot}%{_sysconfdir}/openerp/cert.cfg

install -m 644 server/bin/import_xml.rng %{buildroot}%{python_sitelib}/openerp-server/

install -d %{buildroot}%{scriptsdir}/
install -m 755 server/tools/server-check.sh %{buildroot}%{scriptsdir}/
install -d %{buildroot}%{python_sitelib}/openerp-server/addons/base/security/
install -m 644 server/bin/addons/base/security/* %{buildroot}%{python_sitelib}/openerp-server/addons/base/security/

install -d %{buildroot}%{_datadir}/pixmaps/openerp-server
install -m 644 -D server/pixmaps/* %{buildroot}%{_datadir}/pixmaps/openerp-server/

#temp fixes for alpha builds
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
# some files for the web-client
install -D client-web/scripts/init.d/openerp-web.mdv %{buildroot}%{_initrddir}/%{name}-web
install -D client-web/doc/openerp-web.mdv.cfg %{buildroot}%{_sysconfdir}/openerp-web.cfg
%endif

mkdir -p %{buildroot}/var/log/openerp
mkdir -p %{buildroot}/var/spool/openerp
mkdir -p %{buildroot}/var/run/openerp

install -d %{buildroot}%{_defaultdocdir}/%{name}-server-%{version}-demo/
install -m 744 mandriva/prep_database.sh %{buildroot}%{_defaultdocdir}/%{name}-server-%{version}-demo/
# install -m 644 mandriva/demodb.sql %{buildroot}%{_defaultdocdir}/%{name}-server-%{version}-demo/

pushd %{buildroot}%{_sysconfdir}/openerp/start.d
cat >30start-demo <<EOF
#!/bin/bash

# service postgresql start

pushd %{_defaultdocdir}/%{name}-server-%{version}-demo/
#    DB_NAME=dbdemo DB_RESTORESCRIPT=demodb.sql ./prep_database.sh
popd > /dev/null
# service openerp restart

EOF

ln -sf %{scriptsdir}/server-check.sh ./10server-check
popd

%files
%defattr(-,root,root)
%doc %{clone_prefixdir}server/doc/README.urpmi %{clone_prefixdir}server/README

%if %{build_web}
%files client-web
%doc %{clone_prefixdir}client-web/doc/*
%defattr(-,root,root)
%attr(0755,root, root) %{_bindir}/openerp-web
%attr(0755,root,root) %{_initrddir}/openerp-web
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp-web.cfg
%{python_sitelib}/openobject/
%{py_puresitedir}/openerp_web-*-py%{pyver}.egg-info
%endif

%files client -f %{clone_prefixdir}%{name}-client.lang
%doc %{clone_prefixdir}client/doc/*
%defattr(-,root,root)
%{_bindir}/openerp-client
%{_iconsdir}/openerp-icon.png
%{python_sitelib}/openerp-client/
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
%{_mandir}/man1/koo.*
%{_datadir}/Koo/
%{_datadir}/applications/openerp-koo.desktop
%{py_puresitedir}/koo-*-py%{pyver}.egg-info

%if 0
%files client-kde-apidoc
%defattr(-,root,root)
%endif

%endif

%files serverinit
%defattr(-,root,root)

%files alldemo
%defattr(-,root,root)
        %dir            %{_defaultdocdir}/%{name}-server-%{version}-demo/
#                       %{_defaultdocdir}/%{name}-server-%{version}-demo/demodb.sql
                        %{_defaultdocdir}/%{name}-server-%{version}-demo/prep_database.sh
%attr(0755,root,root)   %{_sysconfdir}/openerp/start.d/30start-demo
# todo: a few readme files, perhaps..

%post client
%{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null

%postun client
if [ -x %{_bindir}/update-desktop-database ]; then %{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null ; fi

%files server
%defattr(-,root,root)
%doc %{clone_prefixdir}server/LICENSE %{clone_prefixdir}server/README 
%doc %{clone_prefixdir}server/doc/INSTALL %{clone_prefixdir}server/doc/Changelog
%attr(0755,openerp,openerp) %dir /var/log/openerp
%attr(0755,openerp,openerp) %dir /var/spool/openerp
%attr(0755,openerp,openerp) %dir /var/run/openerp
%attr(0750,openerp,openerp) %dir %{_sysconfdir}/openerp
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp/cert.cfg
%{_initrddir}/openerp-server
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/openerp-server.conf
%attr(0644,openerp,openerp) %config(noreplace) %{_sysconfdir}/logrotate.d/openerp-server
        %dir            %{_sysconfdir}/openerp/start.d/
        %dir            %{_sysconfdir}/openerp/stop.d/
%attr(0755,root,root)   %{_sysconfdir}/openerp/start.d/10server-check
%attr(0755,root,root)   %{scriptsdir}/server-check.sh
%{_bindir}/openerp-server
%{python_sitelib}/openerp-server/
%{_datadir}/pixmaps/openerp-server/
%exclude %{_defaultdocdir}/%{name}-server-%{version}-demo
%{_mandir}/man1/openerp-server.*
%{py_puresitedir}/openerp_server-%{version}-py%{pyver}.egg-info
%{_mandir}/man5/openerp_serverrc.*

%pre server
# todo: non-mandriva useradd
%if %{build_mdvmga}
%_pre_useradd openerp /var/spool/openerp /sbin/nologin
%else
    /usr/sbin/useradd -c "OpenERP Server" \
        -s /sbin/nologin -r -d /var/spool/openerp openerp 2>/dev/null || :
%endif

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

%if %{build_mdvmga}
%_post_service openerp-server
%else
/sbin/chkconfig --add openerp-server
%endif

%preun server
%if %{build_mdvmga}
%_preun_service openerp-server
%else
if [ $1 = 0 ] ; then
    /sbin/service openerp-server stop >/dev/null 2>&1
    /sbin/chkconfig --del openerp-server
fi
%endif


%postun server
%if %{build_mdvmga}
%_postun_service openerp-server
%_postun_userdel openerp
%else
if [ "$1" -ge "1" ] ; then
    /sbin/service openerp-server condrestart >/dev/null 2>&1 || :
fi
%endif

%post serverinit
chkconfig postgresql on
chkconfig openerp-server on

%changelog -f %{_sourcedir}/%{name}-changelog.gitrpm.txt
