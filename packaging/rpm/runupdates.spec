Name: RunUpdates
Version: %{version}
Release: 1%{?dist}
Summary: RunUpdates system updater and automation tool
License: Proprietary
URL: https://linktechengineering.net/runupdates
Vendor: Linktech Engineering
Packager: Linktech Engineering Support <support@linktechengineering.net>
BuildArch: x86_64
Requires: /bin/bash

%description
RunUpdates is a system update orchestration tool. This RPM installs the
frozen RunUpdates binary and the required runtime directories under
/opt/RunUpdates, including configuration, schemata, logs, and run
directories.

%prep
# Nothing to prep — files were copied into SOURCES by build_rpm.sh

%build
# No build step — binary is prebuilt

%install
rm -rf %{buildroot}

echo "SOURCE DIR: %{_sourcedir}"
find %{_sourcedir}/RunUpdates -maxdepth 3

mkdir -p %{buildroot}/opt/RunUpdates
%install

echo "=== DEBUG ==="
pwd

echo "builddir:"
ls -ld %{_builddir}

echo "staging:"
ls -ld %{_builddir}/../../staging || true

echo "opt:"
ls -ld %{_builddir}/../../staging/opt || true

echo "RunUpdates:"
ls -la %{_builddir}/../../staging/opt/RunUpdates || true

rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/RunUpdates

cp -a %{_builddir}/../../staging/opt/RunUpdates/* \
      %{buildroot}/opt/RunUpdates/

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