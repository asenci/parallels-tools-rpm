Name:		parallels-tools
Version:	15.1.1.47117
Release:	3%{?dist}
Summary:	Parallels Tools for Linux

Group:		Applications/System
License:	Parallels
URL:		https://www.parallels.com/products/desktop

Source:		parallels-tools-%{version}.tar.gz
Source1:	kmodtool-parallels-tools
Source2:	parallels-tools-prltoolsd.service
Source3:	parallels-tools-systemd.preset

Source10:	parallels-tools-dracut.conf
Source11:	parallels-tools-modules-load.conf

Patch1:		parallels-tools-modprobe.patch

Requires:	kmod-%{name} = %{version}-%{release}
Requires:	systemd

BuildRequires:	kernel-abi-whitelists
BuildRequires:	kernel-devel
BuildRequires:	elfutils-libelf-devel
BuildRequires:	make
BuildRequires:	perl
BuildRequires:	redhat-rpm-config
BuildRequires:  gcc

ExclusiveOS:	linux
ExclusiveArch:	x86_64

# Kmod magic hidden here.
%define kmod_version %{version}
%define kmod_release %{release}
%{!?kversion: %define kversion $(uname -r)}
%{expand:%(sh %{SOURCE1} rpmtemplate %{name} %{kversion} "")}
%define debug_package %{nil}


%description
Parallels Tools are a suite of special utilities that help you use your
virtual machines in the most comfortable and efficient way. With Parallels
Tools, you can move the mouse seamlessly between the virtual machine and your
Mac, change the virtual machine's screen resolution by simply resizing its
window, synchronize your virtual machine's time and date settings with the
time settings of the host computer, share your Mac's disks and folders with
its virtual machines, copy text and drag and drop objects from Mac OS to a
virtual machine and vice versa.


%prep
%setup -q -n %{name}-%{version} -c
%patch1 -p0 -b .modprobe


%build
# kernel modules
pushd kmods
tar xzf prl_mod.tar.gz

pushd prl_eth/pvmnet
%{__make} KERNEL_DIR=%{_usrsrc}/kernels/%{kversion}
popd

pushd prl_tg/Toolgate/Guest/Linux/prl_tg
%{__make} KERNEL_DIR=%{_usrsrc}/kernels/%{kversion}
popd
cp prl_tg/Toolgate/Guest/Linux/prl_tg/*.symvers prl_fs/SharedFolders/Guest/Linux/prl_fs
cp prl_tg/Toolgate/Guest/Linux/prl_tg/*.symvers prl_vid/Video/Guest/Linux/kmod

pushd prl_fs/SharedFolders/Guest/Linux/prl_fs
%{__make} KERNEL_DIR=%{_usrsrc}/kernels/%{kversion}
popd

pushd prl_fs_freeze/Snapshot/Guest/Linux/prl_freeze
%{__make} KERNEL_DIR=%{_usrsrc}/kernels/%{kversion}
popd

pushd prl_vid/Video/Guest/Linux/kmod
%{__make} KERNEL_DIR=%{_usrsrc}/kernels/%{kversion}
popd

find . -type f -name '*.ko' -print0 | xargs -0 %{__strip} --strip-debug
popd

# Selinux
mkdir selinux
cp installer/*.te selinux/
cp installer/*.fc selinux/
rm -f selinux/prlvtg.*

pushd selinux
%{__make} -f %{_datadir}/selinux/devel/Makefile
popd


%install
# tools
%{__install} -d %{buildroot}%{_sysconfdir}/pm/sleep.d
%{__install} -m 755 tools/99prltoolsd-hibernate %{buildroot}%{_sysconfdir}/pm/sleep.d/99-prltoolsd

%{__install} -d %{buildroot}%{_unitdir}
%{__install} %{SOURCE2} %{buildroot}%{_unitdir}/prltoolsd.service

%{__install} -d %{buildroot}%{_presetdir}
%{__install} %{SOURCE3} %{buildroot}%{_presetdir}/10-parallels.preset

%{__install} -d %{buildroot}%{_bindir}
%{__install} tools/prlfsmountd.sh %{buildroot}%{_bindir}/prlfsmountd
%{__install} tools/tools64/bin/prl_showvmcfg %{buildroot}%{_bindir}/prl_showvmcfg
%{__install} tools/tools64/bin/prlhosttime %{buildroot}%{_bindir}/prlhosttime
%{__install} tools/tools64/bin/prltimesync %{buildroot}%{_bindir}/prltimesync
%{__install} tools/tools64/bin/prltoolsd %{buildroot}%{_bindir}/prltoolsd

%{__install} -d %{buildroot}%{_sbindir}
%{__install} tools/tools64/sbin/prl_nettool %{buildroot}%{_sbindir}/prl_nettool
%{__install} tools/tools64/sbin/prl_snapshot %{buildroot}%{_sbindir}/prl_snapshot

%{__install} -d %{buildroot}%{_mandir}/man8
%{__install} tools/mount.prl_fs.8 %{buildroot}%{_mandir}/man8/mount.prl_fs.8

%{__install} -d %{buildroot}/usr/lib/parallels-tools/tools/scripts/
%{__install} -m 755 tools/scripts/functions %{buildroot}/usr/lib/parallels-tools/tools/scripts/functions
%{__install} -m 755 tools/scripts/list_services.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/list_services.sh
%{__install} -m 755 tools/scripts/list_software.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/list_software.sh
%{__install} -m 755 tools/scripts/redhat-get_dhcp.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/redhat-get_dhcp.sh
%{__install} -m 755 tools/scripts/redhat-restart.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/redhat-restart.sh
%{__install} -m 755 tools/scripts/redhat-set_dhcp.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/redhat-set_dhcp.sh
%{__install} -m 755 tools/scripts/redhat-set_gateway.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/redhat-set_gateway.sh
%{__install} -m 755 tools/scripts/redhat-set_ip.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/redhat-set_ip.sh
%{__install} -m 755 tools/scripts/redhat-set_route.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/redhat-set_route.sh
%{__install} -m 755 tools/scripts/set_dns.sh %{buildroot}/usr/lib/parallels-tools/tools/scripts/set_dns.sh

# kernel modules
%{__install} -d %{buildroot}/lib/modules/%{kversion}/extra/%{name}
find kmods -type f -name '*.ko' -print0 | xargs -0 %{__install} -t %{buildroot}/lib/modules/%{kversion}/extra/%{name}

%{__install} -d %{buildroot}%{_sysconfdir}/modprobe.d
%{__install} installer/blacklist-parallels.conf %{buildroot}%{_sysconfdir}/modprobe.d/parallels.conf

%{__install} -d %{buildroot}%{_prefix}/lib/dracut/dracut.conf.d
%{__install} %{SOURCE10} %{buildroot}%{_prefix}/lib/dracut/dracut.conf.d/99-parallels.conf

%{__install} -d %{buildroot}%{_prefix}/lib/modules-load.d/
%{__install} %{SOURCE11} %{buildroot}%{_prefix}/lib/modules-load.d/parallels.conf

%{__install} -d %{buildroot}%{_udevrulesdir}
%{__install} tools/parallels-cpu-hotplug.rules %{buildroot}%{_udevrulesdir}/99-parallels-cpu-hotplug.rules
%{__install} tools/parallels-memory-hotplug.rules %{buildroot}%{_udevrulesdir}/99-parallels-memory-hotplug.rules
%{__install} tools/parallels-video.rules %{buildroot}%{_udevrulesdir}/99-parallels-video.rules

# Selinux
%{__install} -d %{buildroot}%{_datadir}/selinux/packages/%{name}
find selinux -name '*.pp' -print0 | xargs -0 %{__install} -t %{buildroot}%{_datadir}/selinux/packages/%{name}


%files
%{_bindir}/prl_showvmcfg
%{_bindir}/prlfsmountd
%{_bindir}/prlhosttime
%{_bindir}/prltimesync
%{_bindir}/prltoolsd
%{_sbindir}/prl_nettool
%{_sbindir}/prl_snapshot
%{_sysconfdir}/pm/sleep.d/99-prltoolsd
/usr/lib/parallels-tools
%defattr(644,root,root,755)
%{_mandir}/man8/mount.prl_fs.8.gz
%{_presetdir}/10-parallels.preset
%{_unitdir}/prltoolsd.service


%post
%systemd_post prltoolsd.service


%preun
%systemd_preun prltoolsd.service


%postun
%systemd_postun_with_restart prltoolsd.service


%clean
%{__rm} -rf %{buildroot}


# Selinux
%package selinux
Summary:        SELinux module for %{name}

BuildArch:	noarch
BuildRequires:	checkpolicy, selinux-policy-devel

Requires:       %{name} = %{version}-%{release}
Requires(post): selinux-policy-base >= %{_selinux_policy_version}
Requires(post): policycoreutils
%if 0%{?rhel} == 7
Requires(post): policycoreutils-python
%else
Requires(post): policycoreutils-python-utils
%endif
Requires(pre):  libselinux-utils
Requires(post): libselinux-utils


%description selinux
This package provides the SELinux policy module to ensure %{name}
runs properly under an environment with SELinux enabled.


%files selinux
%defattr(644,root,root,755)
%{_datadir}/selinux/packages/%{name}


%pre selinux
%selinux_relabel_pre


%post selinux
%selinux_modules_install %{_datadir}/selinux/packages/%{name}/prlfs.pp %{_datadir}/selinux/packages/%{name}/prltimesync.pp %{_datadir}/selinux/packages/%{name}/prltoolsd.pp
%selinux_relabel_post


%posttrans selinux
%selinux_relabel_post

%systemd_postun_with_restart prltoolsd.service


%postun selinux
%selinux_modules_uninstall prlfs prltimesync prltoolsd

if [ $1 -eq 0 ]; then
    %selinux_relabel_post
fi


# Changelog
%changelog
* Fri Nov 22 2019 Andre Sencioles <asenci@gmail.com> - 15.1.1.47117-1
- Initial release
