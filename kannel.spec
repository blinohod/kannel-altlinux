# $Id: kannel.spec 2836 2005-01-17 11:53:55Z dude $
# Authority: matthias

%define branch meta-data
%define kannel_user kannel
%define kannel_group kannel

Summary: WAP and SMS gateway
Name: kannel
Version: 1.4.1
Release: alt1.1.cvs20080124
License: Kannel
Group: Communications
URL: http://www.kannel.org/
Source: %name-%version-%branch.tar.bz2
Source1: bearerbox.init
Source2: smsbox.init

#Packager: Michael Bochkaryov <misha@altlinux.ru>

PreReq: monit-base
BuildPreReq: linux-libc-headers openssl-engines

# Automatically added by buildreq on Tue May 20 2008
BuildRequires: ImageMagick checkstyle docbook-style-dsssl flex fonts-type1-cm-super-pfb jadetex libMySQL-devel libpam-devel libpcre-devel libsqlite-devel libsqlite3-devel libxml2-devel openssl postgresql-devel sqlite sqlite3 transfig

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
%setup -n kannel_meta

%build
%configure \
		--enable-cookies \
		--enable-docs \
		--enable-keepalive \
		--enable-mutex-stats \
		--enable-localtime \
		--enable-pam \
		--enable-pcre \
		--enable-sms \
		--enable-ssl \
		--enable-start-stop-daemon \
		--enable-wap \
		--with-mysql \
		--with-pgsql \
		--with-sqlite \
		--with-sqlite3 \
		--with-ssl=%_libdir/openssl
%make_build

%install
%makeinstall

%make_install install-docs DESTDIR=%buildroot
mv %buildroot%_datadir/doc/kannel _docs

mkdir -p %buildroot%_sysconfdir/kannel
mkdir -p %buildroot%_initdir
mkdir -p %buildroot%_logdir/kannel
mkdir -p %buildroot%_localstatedir/kannel
mkdir -p %buildroot%_var/run/kannel
install -m 644 gw/wapkannel.conf %buildroot%_sysconfdir/kannel
install -m 644 gw/smskannel.conf %buildroot%_sysconfdir/kannel
install -m 755 test/fakesmsc %buildroot%_bindir
install -m 755 test/fakewap %buildroot%_bindir
install -m 755 %SOURCE1 %buildroot%_initdir/kannel.bearerbox
install -m 755 %SOURCE2 %buildroot%_initdir/kannel.smsbox


%pre
%_sbindir/groupadd %kannel_group ||:
%_sbindir/useradd -r -d /dev/null -s /dev/null -g %kannel_group -n %kannel_user \
	2> /dev/null > /dev/null ||:

%post
%post_service kannel.bearerbox
%post_service kannel.smsbox
                                                                                
%preun
%preun_service kannel.bearerbox
%preun_service kannel.smsbox
                                                                                
#postun
#if [ $1 -ge 1 ]; then
#   /sbin/service foobar condrestart >/dev/null 2>&1 || :
#fi


%files
%doc AUTHORS COPYING ChangeLog NEWS README STATUS _docs/* contrib
%_bindir/*
%_sbindir/*
%_mandir/man?/*
%dir %_sysconfdir/kannel
%config(noreplace) %_sysconfdir/kannel/*
%_initdir/*
%attr(0770,%kannel_user,%kannel_group) %dir %_var/run/kannel
%attr(0770,%kannel_user,%kannel_group) %dir %_localstatedir/kannel

%files devel
%_includedir/kannel/
%dir %_libdir/kannel/
%_libdir/kannel/*.a

%changelog
* Wed May 21 2008 Michael Bochkaryov <misha@altlinux.ru> 1.4.1-alt1.1.cvs20080124
- build from CVS meta-data branch:
  + optional SMPP TLV parameters support
	+ MO SM concatenation support
- documentation and contribs packaged
- init scripts and default configuration added
- PostgreSQL support added
- libpcre support added

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

