# This spec file generates an RPM that installs the cray_node_discovery role
# into the ansible_framework
# Copyright 2019 Cray Inc. All Rights Reserved.
%define install_dir /opt/cray/crayctl/ansible_framework

Requires: cray-crayctl
Requires: kubernetes-crayctldeploy

Name: node-discovery-crayctldeploy
License: Cray Software License Agreement
Summary: node-discovery deployment ansible role
Version: 0.3.1
Release: %(echo ${BUILD_METADATA})
Source: %{name}-%{version}.tar.bz2
Vendor: Cray Inc.

%description
This RPM when installed will place an ansible role, for the purposes of
deploying Cray's node-discovery tool, into the ansible framework so it can then
later be installed.

%prep
%setup -q

%build

%install
install -m 755 -d %{buildroot}%{install_dir}/roles/
cp -r ansible_framework/cray_node_discovery %{buildroot}%{install_dir}/roles/

%files
%{install_dir}/roles/*

%changelog
