Name:           parallels-tools-release
Version:        7
Release:        1
Summary:        Parallels Desktop Tools for CentOS 7 repository configuration

Group:          System Environment/Base
License:        GPLv2
URL:            https://github.com/asenci/parallels-tools-rpm

Source1:        parallels-tools.repo

BuildArch:     noarch

Requires:      redhat-release >=  %{version}


%description
This package contains the Parallels Desktop Tools for CentOS 7 configuration
for yum.


%install
%{__install} -d %{buildroot}%{_sysconfdir}/yum.repos.d
%{__install} %{SOURCE1} %{buildroot}%{_sysconfdir}/yum.repos.d/parallels.repo


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(644,root,root,755)
%config(noreplace) /etc/yum.repos.d/*


%changelog
* Fri Nov 22 2019 Andre Sencioles <asenci@gmail.com> - 15.1.1.47117-1
- Initial release
