%global owner ojuba-org
%global commit #Write commit number here
%global sname okasha

Name: python-okasha
Summary: WSGI web framework for python
URL: http://ojuba.org
Version: 0.3.0
Release: 1%{?dist}
Source0: https://github.com/%{owner}/%{sname}/archive/%{commit}/%{sname}-%{commit}.tar.gz
License: WAQFv2
Group: System Environment/Base
BuildArch: noarch
BuildRequires: python3-devel

%description
Almost do-nothing web framewrok that features:
  * WSGI-enabled ie. can be used with mod_wsgi, mod_python, fast cgi, cgi, with paste or even without even a server
  * light weight
  * can be tuned to be suitable for desktop apps or public web servers
  * no extra dependencies
  * very simple

%package xslt
Summary:  xslt templates and support for okasha framework
Group: System Environment/Base
Requires: %{name}
Requires: python-lxml

%description xslt
Adds support for xslt-based templates using python's lxml package


%package docs
Summary:  documentation for okasha the trivial WSGI web framework for python
Group: System Environment/Base
Requires: python-okasha-xslt
Requires: python-paste

%description docs
documentation for okasha and a sample web application that uses okasha

%prep
%setup -q -n %{sname}-%{commit}

%build
pushd docs
bash ./update-from-site.sh
popd

%install
%{__python3} setup.py install \
        --root=$RPM_BUILD_ROOT \
        --optimize=2

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-docs/
cp -a test.py test.wsgi demo-themes $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-docs/
rm docs/update-from-site.sh
cp -a docs/* $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-docs/

%files
%defattr(-,root,root,-)
%doc waqf2-ar.pdf README README.ar.txt TODO
%{python3_sitelib}/%{sname}/__init__.py*
%{python3_sitelib}/%{sname}/baseWebApp.py*
%{python3_sitelib}/%{sname}/bottleTemplate.py*
%{python3_sitelib}/%{sname}/bottleTemplateSegment.py*
%{python3_sitelib}/%{sname}/utils.py*
%{python3_sitelib}/*.egg-info
%{python3_sitelib}/%{sname}/__pycache__/*.py*

%files xslt
%{python3_sitelib}/%{sname}/xsltTemplate.*

%files docs
%{_datadir}/doc/%{name}-docs/

%changelog
* Sun Sep 26 2021 Ehab El-Gedawy <ehabsas@gmail.com> - 0.3.0-1
- Port to python 3.

* Sat Feb 15 2014 Mosaab Alzoubi <moceap@hotmail.com> - 0.2.4-3
- General Fixes.

* Sat Feb 15 2014 Mosaab Alzoubi <moceap@hotmail.com> - 0.2.4-2
- Full Revision.

* Sun Jul 11 2010  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.2.0-2
- add bottle tamplates support
- add documentation

* Sat Jun 12 2010  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.0-2
- let python-okasha-xslt and python-okasha-kid depend on python-okasha

* Sat Jun 12 2010  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.0-1
- initial packing
