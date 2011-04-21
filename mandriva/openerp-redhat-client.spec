# Redhat, crippled, static version of the spec file


%if 1
# Where is that officially defined?
    %define _iconsdir %{_datadir}/icons
%endif

%define tarball_extra -4-g0e50801

Name:		openerp-client
Version:	6.0.2
Release:	4%{?dist}
License:	AGPLv3
Group:		Applications/Databases
Summary:	OpenERP Client
URL:		http://www.openerp.com
Source0:	http://www.openerp.com/download/stable/source/%{name}-%{version}%{tarball_extra}.tar.gz
#                   All non-official patches are contained in:
#                   http://git.hellug.gr/?p=xrg/openerp  and referred submodules
#                   look for the ./mandriva folder there, where this .spec file is held, also.
# BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	desktop-file-utils, python-setuptools
BuildRequires:	pygtk2-devel, libxslt-python
BuildRequires:	python2-devel

Requires:	pygtk2
Requires:       pygobject2, pygtk2-libglade, pydot, python-lxml
# Requires:	python-matplotlib
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
Requires:	hippo-canvas-python
Requires:	python-dateutil
Requires:       mx

%description
Gtk client component for Open ERP.


%prep
%setup -q

%build

python ./setup.py build --quiet

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

python ./setup.py install --root=%{buildroot} --quiet
install -D bin/pixmaps/openerp-icon.png %{buildroot}%{_iconsdir}/openerp-icon.png

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
    chmod a+x openerp-client.py
popd


pushd %{buildroot}/%{_datadir}/locale
# Adjusting localization names for Albania, Ukraine
	mv al sq
	rm -rf ua # there is already an "uk" file for Ukraine, ua seems old.
popd

%find_lang %{name}

mv %{buildroot}/%{_datadir}/openerp-client/* %{buildroot}/%{python_sitelib}/%{name}
rm -rf %{buildroot}/%{_datadir}/openerp-client

mkdir %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << EOF
[Desktop Entry]
Version=1.0
Name=Open ERP
GenericName=GTK ERP Client
Comment=A gtk client for the open source ERP
Exec=%{_bindir}/%{name}
Icon=openerp-icon
Terminal=false
Type=Application
StartupNotify=true
Categories=Office;GNOME;GTK;
EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%if 0
#Left here for future backporting
%clean
rm -rf %{buildroot}
%endif

%files -f %{name}.lang
%defattr(-,root,root)
%doc doc/*
%{_bindir}/%{name}
%{_iconsdir}/openerp-icon.png
%{python_sitelib}/%{name}/
%{_mandir}/man1/openerp-client.*
%{_datadir}/pixmaps/openerp-client/
%{_datadir}/applications/%{name}.desktop
%{python_sitelib}/openerp_client-%{version}-py%{python_version}.egg-info

%post
%{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null

%postun
if [ -x %{_bindir}/update-desktop-database ]; then %{_bindir}/update-desktop-database %{_datadir}/applications > /dev/null ; fi

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

