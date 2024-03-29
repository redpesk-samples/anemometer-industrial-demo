Name: anemometer-industrial-demo
Version: 0.0.0
Release: 0%{?dist}
Summary: Configuration package having all the configuration files for the industrial demo and a script

License: APL2.0
URL: http://git.ovh.iot/redpesk/redpesk-samples/anemometer-industrial-demo
Source0: %{name}-%{version}.tar.gz
BuildArch: x86_64

Requires:       modbus-binding
Requires:       redis-tsdb-binding
Requires:       afb-libpython
Requires:       modbus-binding-simulation

%description

%prep

%build

%install

%clean

%files

%changelog
