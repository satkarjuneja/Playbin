Name:           playbin
Version:        2.1.0
Release:        1%{?dist}
Summary:        Audio player and visualizer

License:        MIT
URL:            https://github.com/satkarjuneja/playbin
Source0:        playbin
Source1:        playbin.1

Requires:       mpv
Requires:       pulseaudio-utils

BuildArch:      x86_64

%description
Playbin audio player.

%install
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{_sourcedir}/playbin %{buildroot}%{_bindir}/playbin
install -Dm644 %{_sourcedir}/playbin.1 %{buildroot}%{_mandir}/man1/playbin.1

%files
%{_bindir}/playbin
%{_mandir}/man1/playbin.1*

%changelog
* Fri Jun 12 2026 Satkar Juneja - 2.1.0
- Update to latest version of yt-dlp
- Add loop feature
