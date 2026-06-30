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
# Nothing to prep — frozen build is already provided

%build
# No build step — binary is prebuilt

%install
rm -rf %{buildroot}

# Create target directory
mkdir -p %{buildroot}/opt/RunUpdates

# Copy full runtime tree from SOURCES
cp -a %{_sourcedir}/RunUpdates/opt/RunUpdates/* %{buildroot}/opt/RunUpdates/

%files
%dir /opt/RunUpdates
%dir /opt/RunUpdates/bin
%dir /opt/RunUpdates/etc
%dir /opt/RunUpdates/etc/schemata
%dir /opt/RunUpdates/var

%post
echo "RunUpdates installed."

%preun
echo "Uninstalling RunUpdates..."

%postun
echo "RunUpdates removed."
