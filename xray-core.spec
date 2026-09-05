%global gomodulesmode %{nil}
%global debug_package %{nil}

%bcond prebuilt 0

Name:           xray-core
Version:        26.7.28
Release:        1%{?dist}
Summary:        Xray, Penetrates Everything. Also the best v2ray-core. Project X network proxy tool
URL:            https://github.com/XTLS/Xray-core

%if %{without prebuilt}
License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND GPL-3.0-only AND ISC AND LGPL-3.0-only AND MIT AND MPL-2.0
Source0:        https://github.com/XTLS/Xray-core/archive/v%{version}/Xray-core-%{version}.tar.gz
Source1:        Xray-core-%{version}-vendor.tar.bz2
Source2:        go-vendor-tools.toml
%else
License:        MPL-2.0
%ifarch x86_64
Source0:        https://github.com/XTLS/Xray-core/releases/download/v%{version}/Xray-linux-64.zip
%endif
%ifarch aarch64
Source0:        https://github.com/XTLS/Xray-core/releases/download/v%{version}/Xray-linux-arm64-v8a.zip
%endif
Source1:        LICENSE
%endif
Source3:        https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geoip.dat
Source4:        https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat
Source5:        xray.service
Source6:        xray@.service
Source7:        config.json
Source8:        xray.sysusers

ExclusiveArch:  x86_64 aarch64

%if %{without prebuilt}
BuildRequires:  golang >= 1.23
BuildRequires:  gcc
BuildRequires:  go-vendor-tools
BuildRequires:  go-rpm-macros
%else
BuildRequires:  unzip
%endif
BuildRequires:  systemd-rpm-macros

Provides:       xray = %{version}-%{release}

%description
Xray-core is a platform for building proxies to bypass network restrictions.
It supports multiple protocols including VLESS, VMess, Trojan, Shadowsocks,
and features XTLS for enhanced performance.
%if %{with prebuilt}
Built from upstream pre-built binaries.
%else
Built from source.
%endif

%if %{without prebuilt}
%generate_buildrequires
%go_vendor_license_buildrequires -c %{S:2}
%endif

%prep
%if %{without prebuilt}
%autosetup -n Xray-core-%{version} -a1
%else
%setup -q -c -n %{name}-%{version}
%endif

%build
%if %{without prebuilt}
# Custom ldflags must go through GO_LDFLAGS; passing a second -ldflags
# would override the distribution flags (build-id, linkmode, hardening).
export GO_LDFLAGS="-X github.com/xtls/xray-core/core.build=%{version}-%{release}"
%gobuild -o xray ./main
%endif

%install
install -Dpm 0755 xray %{buildroot}%{_bindir}/xray

install -Dpm 0644 %{SOURCE3} %{buildroot}%{_datadir}/xray/geoip.dat
install -Dpm 0644 %{SOURCE4} %{buildroot}%{_datadir}/xray/geosite.dat
install -Dpm 0644 %{SOURCE7} %{buildroot}%{_sysconfdir}/xray/config.json
install -Dpm 0644 %{SOURCE5} %{buildroot}%{_unitdir}/xray.service
install -Dpm 0644 %{SOURCE6} %{buildroot}%{_unitdir}/xray@.service
install -Dpm 0644 %{SOURCE8} %{buildroot}%{_sysusersdir}/xray.conf
install -dm 0750 %{buildroot}%{_localstatedir}/log/xray

%if %{without prebuilt}
%go_vendor_license_install -c %{S:2}
%else
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
%endif

%if %{without prebuilt}
%check
%go_vendor_license_check -c %{S:2}
%endif

%pre
%sysusers_create_compat %{SOURCE8}

%post
%systemd_post xray.service

%preun
%systemd_preun xray.service

%postun
%systemd_postun_with_restart xray.service

%if %{without prebuilt}
%files -f %{go_vendor_license_filelist}
%doc README.md
%else
%files
%license %{_datadir}/licenses/%{name}/LICENSE
%endif
%{_bindir}/xray
%dir %{_datadir}/xray
%{_datadir}/xray/geoip.dat
%{_datadir}/xray/geosite.dat
%dir %{_sysconfdir}/xray
%config(noreplace) %{_sysconfdir}/xray/config.json
%{_unitdir}/xray.service
%{_unitdir}/xray@.service
%{_sysusersdir}/xray.conf
%attr(0750,xray,xray) %dir %{_localstatedir}/log/xray

%changelog
* Sun Sep 06 2026 blennuria <blennuria@pm.me> - 26.7.28-1
- Initial package
