%global owner ojuba-org
%global commit #Write commit number here
%global sname okasha

Name: python-okasha
Summary: WSGI web framework for python
URL: http://ojuba.org
Version: 0.2.4
Release: 3%{?dist}
Source0: https://github.com/%{owner}/%{sname}/archive/%{commit}/%{sname}-%{commit}.tar.gz
License: WAQFv2
Group: System Environment/Base
BuildArch: noarch
BuildRequires: python2-devel
BuildRequires: perl

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

%package kid
Summary:  kid templates and support for okasha framework
Group: System Environment/Base
Requires: %{name}
Requires: python-kid

%description kid
Adds support for kid-based templates using python's kid package

%package docs
Summary:  documentation for okasha the trivial WSGI web framework for python
Group: System Environment/Base
Requires: python-okasha-kid
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
%{__python2} setup.py install \
        --root=$RPM_BUILD_ROOT \
        --optimize=2

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-docs/
cp -a test.py test.wsgi demo-themes $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-docs/
rm docs/update-from-site.sh
cp -a docs/* $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-docs/

%files
%defattr(-,root,root,-)
%doc waqf2-ar.pdf README README.ar.txt TODO
%{python2_sitelib}/%{sname}/__init__.py*
%{python2_sitelib}/%{sname}/baseWebApp.py*
%{python2_sitelib}/%{sname}/bottleTemplate.py*
%{python2_sitelib}/%{sname}/bottleTemplateSegment.py*
%{python2_sitelib}/%{sname}/utils.py*
%{python2_sitelib}/*.egg-info

%files xslt
%{python2_sitelib}/%{sname}/kidTemplate.py*

%files kid
%{python2_sitelib}/%{sname}/xsltTemplate.py*

%files docs
%{_datadir}/doc/%{name}-docs/

%changelog
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
