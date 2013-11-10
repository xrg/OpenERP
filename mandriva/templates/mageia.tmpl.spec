{% if autonomous %}
%define git_repo {{ name }}
%define git_head HEAD
%define cd_if_modular
{% else %}
%define cd_if_modular cd %{name}-%{version}
{% endif %}

%{?!pyver: %define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define release_class {{ release_class }}

%define __find_provides   %{u2p:%{_builddir}}/openerp-{{rel.version }}/mandriva/find-provides.sh
%define __find_requires   %{u2p:%{_builddir}}/openerp-{{rel.version }}/mandriva/find-requires.sh

Name:   {{name}}
License:        AGPLv3
Group:          Databases
Summary:        Addons for OpenERP/F3
{% if autonomous %}
Version:        %git_get_ver
Release:        %mkrel %git_get_rel2
Source0:        %git_bs_source %{name}-%{version}.tar.gz
Source1:        %{name}-gitrpm.version
Source2:        %{name}-changelog.gitrpm.txt
{% else %}
Version:        {{rel.mainver+rel.subver }}
Release:        %mkrel {{ rel.extrarel }}
#Source0:       %{name}-%{version}.tar.gz
{% endif %}
URL:            {{ project_url or 'http://openerp.hellug.gr' }}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}
BuildArch:      noarch

%description
Addon modules for OpenERP

%prep
{% if autonomous %}
%git_get_source
%setup -q
{% else %}
cd %{name}-%{version}
{% endif %}

%build
%{cd_if_modular}

%install
%{cd_if_modular}
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/%{python_sitelib}/openerp-server/addons
cp -ar ./* $RPM_BUILD_ROOT/%{python_sitelib}/openerp-server/addons/

{% if modules.no_dirs %}
pushd $RPM_BUILD_ROOT/%{python_sitelib}/openerp-server/addons/
{% for tdir in modules.no_dirs %}
        rm -rf {{ tdir }}
{% endfor %}
popd
{% endif %}

{% for module in modules %}
{% if not module.installable %}
    {%- continue %}
{% endif %}
%package {{ module.name }}
{% if module.info.version %}
Version: {{ module.info.version }}
{% endif %}
Group: Databases
Summary: {{ module.info.name }}
Requires: openerp-server {% if rel.mainver %}>= {{ rel.mainver }}{% endif %}

{% if module.info.depends %}
{{ module.get_depends() }}
{% endif -%}
{%- if module.ext_deps %}
{{ module.ext_deps }}
{% endif -%}
{% if module.info.author %}
Vendor: {{module.info.author }}
{% endif %}
{% if module.info.website %}
URL: {{ module.get_website() }}
{% endif %}

%description {{ module.name }}
{{ module.info.description or module.info.name }}


%files {{ module.name }}
%defattr(-,root,root)
%{python_sitelib}/openerp-server/addons/{{ module.name }}

{% endfor %}

{% if autonomous %}
%changelog -f %{_sourcedir}/%{name}-changelog.gitrpm.txt
{% endif %}

#eof
