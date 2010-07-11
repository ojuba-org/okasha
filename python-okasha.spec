Name: python-okasha

%global srcname okasha
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Summary: trivial WSGI web framework for python
URL: http://okasha.ojuba.org
Version: 0.2.0
Release: 1%{?dist}
Source0: http://git.ojuba.org/cgit/%{srcname}/snapshot/%{srcname}-%{version}.tar.bz2
License: Waqf
Group: System Environment/Base
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python
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
Requires: %{name}, python-lxml
%description xslt
Adds support for xslt-based templates using python's lxml package

%package kid
Summary:  kid templates and support for okasha framework
Group: System Environment/Base
Requires: %{name}, python-kid
%description kid
Adds support for kid-based templates using python's kid package

%package docs
Summary:  documentation for okasha the trivial WSGI web framework for python
Group: System Environment/Base
Requires: python-okasha-kid python-okasha-xslt python-paste
%description docs
documentation for okasha and a sample web application that uses okasha

Documentation is installed on /%{_datadir}/doc/%{name}-docs/

%prep
%setup -q -n %{srcname}-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install \
        --root=$RPM_BUILD_ROOT \
        --optimize=2

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-docs/
cp -a test.py test.wsgi files templates $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-docs/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc LICENSE-en LICENSE-ar.txt README README.ar.txt TODO
%{python_sitelib}/%{srcname}/__init__.py*
%{python_sitelib}/%{srcname}/baseWebApp.py*
%{python_sitelib}/%{srcname}/bottleTemplate.py*
%{python_sitelib}/%{srcname}/bottleTemplateSegment.py*
%{python_sitelib}/%{srcname}/utils.py*
%{python_sitelib}/*.egg-info

%files xslt
%{python_sitelib}/%{srcname}/kidTemplate.py*

%files kid
%{python_sitelib}/%{srcname}/xsltTemplate.py*

%files docs
%{_datadir}/doc/%{name}-docs/

%changelog
* Sat Jun 12 2010  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.0-2
- let python-okasha-xslt and python-okasha-kid depend on python-okasha

* Sat Jun 12 2010  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.0-1
- initial packing

