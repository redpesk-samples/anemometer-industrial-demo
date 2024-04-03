%global binary          anemometer_industrial_demo.py
%global service         %{binary}.service
%global modbusconfsimu  anemometer_simu.json
%global modbusconf      anemometer.json
%global confdir         %{_sysconfdir}/gateway
%global afmdatadir      /var/local/lib/afm/applications
%global modbusbinding   modbus-binding
%global redisconf       redis.conf


Name: anemometer-industrial-demo
Version: 1.0.0
Release: 0%{?dist}
Summary: A small binding that connects a Modbus device to a Redis timeseries

License: APL2.0
URL: http://git.ovh.iot/redpesk/redpesk-samples/anemometer-industrial-demo
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch

Requires:       modbus-binding
Requires:       redis-tsdb-binding
Requires:       afb-libpython


%description
%summary

%package simulation
Summary:        A small binding that connects a Modbus device to a Redis timeseries - package for the Modbus simulation
Requires:       modbus-binding
Requires:       redis-tsdb-binding
Requires:       afb-libpython
Requires:       modbus-binding-simulation

%description simulation
Package which uses modbus binding simulation
%summary
%prep
%autosetup -p 1


%install
install -Dm755 %{binary} %{buildroot}%{_bindir}/%{binary}
#install -Dm644 systemd/%{service} %{buildroot}%{_unitdir}/%{service}
install -Dm644 configs/%{modbusconf} %{buildroot}%{confdir}/%{modbusconf}
install -Dm644 configs/%{modbusconfsimu} %{buildroot}%{confdir}/%{modbusconfsimu}
install -Dm644 configs/%{redisconf} %{buildroot}%{confdir}/%{redisconf}

%files
%{_bindir}/%{binary}
#%{_unitdir}/%{service}
%config(noreplace) %{confdir}/%{modbusconf}
%config(noreplace) %{confdir}/%{redisconf}

%post
if [[ -d %{afmdatadir}/%{modbusbinding} ]]; then
    cp %{confdir}/%{modbusconf} %{afmdatadir}/%{modbusbinding}/etc/%{modbusconf}
    chsmack -a App:modbus-binding:Conf %{afmdatadir}/%{modbusbinding}/etc/%{modbusconf}
fi


%files simulation
%{_bindir}/%{binary}
%config(noreplace) %{confdir}/%{modbusconfsimu}
%config(noreplace) %{confdir}/%{redisconf}
%post simulation
if [[ -d %{afmdatadir}/%{modbusbinding} ]]; then
    cp %{confdir}/%{modbusconfsimu} %{afmdatadir}/%{modbusbinding}/etc/%{modbusconfsimu}
    chsmack -a App:modbus-binding:Conf %{afmdatadir}/%{modbusbinding}/etc/%{modbusconfsimu}
fi


%changelog
