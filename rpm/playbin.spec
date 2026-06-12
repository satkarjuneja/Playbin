Name:           playbin
Version:        2.0.0
Release:        1%{?dist}
Summary:        Audio player and visualizer

License:        MIT
URL:            https://github.com/satkarjuneja/playbin
Source0:        playbin

Requires:       mpv
Requires:       pulseaudio-utils

BuildArch:      x86_64

%description
Playbin audio player.

%install
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{_sourcedir}/playbin %{buildroot}%{_bindir}/playbin

%files
%{_bindir}/playbin

%changelog
* Fri Jun 12 2026 Satkar Juneja - 2.0.0-1
- Initial release