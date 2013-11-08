%{?!pyver: %define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define release_class {{ release_class }}

Name:   {{name}}
Version:        {{rel.mainver+rel.subver }}
Release:        %mkrel {{ rel.extrarel }}
License:        AGPLv3
Group:          Databases
Summary:        Addons for OpenERP/F3
#Source0:       %{name}-%{version}.tar.gz
URL:            http://openerp.hellug.gr
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}
BuildArch:      noarch

%description
Addon modules for OpenERP

%prep
cd %{name}-%{version}
# setup -q

%build
cd %{name}-%{version}

%install
cd %{name}-%{version}
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
Requires: openerp-server >= {{ rel.mainver }}
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

#eof
