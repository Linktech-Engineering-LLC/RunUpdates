Name:           RunUpdates
Version:        %{version}
Release:        1%{?dist}
Summary:        RunUpdates system updater and automation tool

License:        Proprietary
URL:            https://linktechengineering.net/runupdates
Source0:        RunUpdates-%{version}.tar.gz

%global debug_package %{nil}
%global _build_id_links none

BuildArch:      x86_64
Requires:       /bin/bash

%description
RunUpdates is a system update orchestration tool.

This RPM installs the frozen RunUpdates binary and required runtime
directories under /opt/RunUpdates, including configuration,
schemata, log storage, and runtime directories.

%prep
%setup -q

%build
# Nothing to build.
# Binary has already been frozen by PyInstaller.

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/opt

cp -a opt/RunUpdates %{buildroot}/opt/

%files
%dir /opt/RunUpdates

/opt/RunUpdates/LICENSE

%dir /opt/RunUpdates/bin
/opt/RunUpdates/bin/RunUpdates

%dir /opt/RunUpdates/etc
/opt/RunUpdates/etc/bash.env
/opt/RunUpdates/etc/cron.env
/opt/RunUpdates/etc/systemd.env

%dir /opt/RunUpdates/etc/schemata
/opt/RunUpdates/etc/schemata/hosts.schema.yml

%dir /opt/RunUpdates/var
%dir /opt/RunUpdates/var/log
%dir /opt/RunUpdates/var/log/summaries
%dir /opt/RunUpdates/var/run

%post
echo "RunUpdates installed."

%preun
echo "Uninstalling RunUpdates..."

%postun
echo "RunUpdates removed."