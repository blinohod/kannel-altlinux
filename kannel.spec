# $Id: kannel.spec 2836 2005-01-17 11:53:55Z dude $
# Authority: matthias

Summary: WAP and SMS gateway
Name: kannel
Version: 1.4.1
Release: alt1.0
License: Kannel
Group: Communications
URL: http://www.kannel.org/
Source: http://www.kannel.org/download/%version/gateway-%version.tar.bz2

BuildRequires: linux-libc-headers openjade transfig
BuildRequires: ImageMagick docbook-style-dsssl flex libMySQL-devel libpq-devel
BuildRequires: libxml2-devel openjade postgresql-devel sqlite-devel tetex-dvips
BuildRequires: transfig zlib-devel bison byacc openssl-devel pcre-devel

%description
The Kannel Open Source WAP and SMS gateway works as both an SMS gateway, for
implementing keyword based services via GSM text messages, and a WAP gateway,
via UDP. The SMS part is fairly mature, the WAP part is early in its
development. In this release, the GET request for WML pages and WMLScript
files via HTTP works, including compilation for WML and WMLScript to binary
forms. Only the data call bearer (UDP) is supported, not SMS.


%package devel
Summary: Development files for the kannel WAP and SMS gateway
Group: Development/C
Requires: %name = %version

%description devel
The Kannel Open Source WAP and SMS gateway works as both an SMS gateway, for
implementing keyword based services via GSM text messages, and a WAP gateway,
via UDP. The SMS part is fairly mature, the WAP part is early in its
development. In this release, the GET request for WML pages and WMLScript
files via HTTP works, including compilation for WML and WMLScript to binary
forms. Only the data call bearer (UDP) is supported, not SMS.

Install this package if you need to develop or recompile applications that
use the kannel WAP and SMS gateway.


%prep
%setup -n gateway-%version

%build
%configure \
    --disable-start-stop-daemon \
    --with-sqlite \
    --with-mysql \
    --with-pgsql
%make_build

%install
%makeinstall

#post
#if [ $1 -eq 1 ]; then
#   /sbin/chkconfig --add foobar
#fi
                                                                                
#preun
#if [ $1 -eq 0 ]; then
#   /sbin/service foobar stop >/dev/null 2>&1 || :
#   /sbin/chkconfig --del foobar
#fi
                                                                                
#postun
#if [ $1 -ge 1 ]; then
#   /sbin/service foobar condrestart >/dev/null 2>&1 || :
#fi


%files
%doc AUTHORS COPYING ChangeLog NEWS README STATUS
%_bindir/*
%_sbindir/*
%_mandir/man?/*

%files devel
%_includedir/kannel/
%dir %_libdir/kannel/
%_libdir/kannel/*.a

%changelog
* Fri Mar 30 2007 ALT QA Team Robot <qa-robot@altlinux.org> 1.4.1-alt1.0
- Rebuilt due to libpq.so.4 -> libpq.so.5 soname change.

* Wed Mar 14 2007 Grigory Milev <week@altlinux.ru> 1.4.1-alt1
- New version released
- fix build dependence

* Tue Mar 14 2006 Grigory Milev <week@altlinux.ru> 1.4.0-alt1
- initial build for altlinux

* Mon Jan 17 2005 Matthias Saou <http://freshrpms.net/> 1.4.0-3
- Added Stefan Radman's patch for kannel bug #173 to fix .depend problem.

* Fri Dec 10 2004 Matthias Saou <http://freshrpms.net/> 1.4.0-1
- Update to 1.4.0.
- Remove the obsolete OpenSSL workaround.

* Thu Nov  4 2004 Matthias Saou <http://freshrpms.net/> 1.3.2-4
- Added pcre support, doc building (almost) and sqlite backend...
  it still fails with a corrupt first line of .depend on FC3, though.

* Tue Aug 24 2004 Matthias Saou <http://freshrpms.net/> 1.3.2-2
- Really comment out all scriplets, they're not yet used.

* Thu Jul 29 2004 Matthias Saou <http://freshrpms.net/> 1.3.2-1
- Don't fix the openssl detection for RHL 7.x.

* Thu Jul 22 2004 Matthias Saou <http://freshrpms.net/> 1.3.2-0
- Update to 1.3.2 development version.
- Added -devel sub-package since there are now headers and a static lib.

* Wed Jul 14 2004 Matthias Saou <http://freshrpms.net/> 1.2.1-0
- Initial RPM release, still need to add an init script I think.

