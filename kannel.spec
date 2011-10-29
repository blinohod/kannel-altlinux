%define kannel_user kannel
%define kannel_group kannel
%define kannel_build svn4937

Summary: WAP and SMS gateway
Name: kannel
Version: 1.5.0
Release: alt7.%kannel_build
License: Kannel
Group: Communications
URL: http://www.kannel.org/
Source: gateway-%version.tar.bz2
Source1: config-%version.tar.bz2
Source2: bearerbox.init
Source3: smsbox.init
Source5: kannel.logrotate
Source6: kannel.monit

PreReq: monit-base
BuildPreReq: linux-libc-headers openssl-engines 

Packager: Michael Bochkaryov <misha@altlinux.ru>

# Automatically added by buildreq on Wed Sep 07 2011 (-bi)
# optimized out: elfutils libcom_err-devel libkrb5-devel libpq-devel
BuildRequires: ImageMagick-tools flex gcc-c++ libmysqlclient-devel libpam-devel libpcre-devel libsqlite3-devel libssl-devel libxml2-devel openssl postgresql-devel sqlite3 zlib-devel

%description
Kannel is an open source software implementing the following functionality:

* WAP gateway for connecting WAP (Wireless Application Protocol) capable
phones to the Internet. WML and WMLScript files compilation to binary
form is supported.

* SMS gateway for implementing services based on GSM/CDMA short messages.
GSM modems, SMPP, UCP/EMI, CIMD and other SMSC connections are supported.

* WAP Push Proxy Gateway (PPG).

* OTA Settings delivery platform.

Compiled with PAM, SSL, MySQL, PostgreSQL, SQLite3 and native malloc.

%package devel
Summary: Development files for the kannel WAP and SMS gateway
Group: Development/C
Requires: %name = %version

%description devel
This package contains libraries and header files for Kannel WAP and SMS
gateway. Install this package if you need to develop or recompile
applications that use Kannel.

%prep
%setup -c -n %name-%version
%setup -T -D -a 1

%build 
cd gateway-%version
%configure \
		--with-cflags='-fPIC' \
		--enable-cookies \
		--enable-largefile \
		--disable-docs \
		--disable-drafts \
		--enable-keepalive \
		--disable-mutex-stats \
		--enable-localtime \
		--enable-pam \
		--enable-pcre \
		--enable-sms \
		--enable-ssl \
		--disable-start-stop-daemon \
		--with-defaults=speed \
		--enable-wap \
		--with-mysql \
		--with-pgsql \
		--without-sqlite \
		--with-sqlite3 \
		--with-ssl=%_libdir/openssl \
		--disable-ssl-thread-test
%make

%install
cd gateway-%version
%makeinstall

%make_install install-docs DESTDIR=%buildroot

mkdir -p %buildroot%_sysconfdir/logrotate.d
mkdir -p %buildroot%_sysconfdir/monitrc.d
mkdir -p %buildroot%_initdir
mkdir -p %buildroot%_logdir/kannel
mkdir -p %buildroot%_localstatedir/kannel/cdr
mkdir -p %buildroot%_var/run/kannel
mkdir -p %buildroot%_var/spool/kannel
install -m 755 test/fakesmsc %buildroot%_bindir
install -m 755 test/fakewap %buildroot%_bindir
install -m 755 test/wapproxy %buildroot%_bindir
install -m 755 test/store_tools %buildroot%_bindir/kannel-store-tools
install -m 755 %SOURCE2 %buildroot%_initdir/kannel.bearerbox
install -m 755 %SOURCE3 %buildroot%_initdir/kannel.smsbox
install -m 755 %SOURCE5 %buildroot%_sysconfdir/logrotate.d/kannel
install -m 755 %SOURCE6 %buildroot%_sysconfdir/monitrc.d/kannel
cp -rf ../config %buildroot%_sysconfdir/kannel

%pre
%_sbindir/groupadd %kannel_group ||:
%_sbindir/useradd -r -d /dev/null -s /dev/null -g %kannel_group -n %kannel_user \
	2> /dev/null > /dev/null ||:

%post
%post_service kannel.bearerbox
%post_service kannel.smsbox

%preun
%preun_service kannel.smsbox
%preun_service kannel.bearerbox

%files
%doc gateway-%version/{AUTHORS,ChangeLog,COPYING,NEWS,README,STATUS,contrib,doc}
%_bindir/*
%_sbindir/*
#%%exclude %%_sbindir/start-stop-daemon
%_mandir/man?/*
%dir %_sysconfdir/kannel/*
%config(noreplace) %_sysconfdir/kannel/*
%config(noreplace) %_sysconfdir/monitrc.d/*
%config(noreplace) %_sysconfdir/logrotate.d/*
%_initdir/*
%attr(0770,%kannel_user,%kannel_group) %dir %_logdir/kannel
%attr(0770,%kannel_user,%kannel_group) %dir %_var/run/kannel
%attr(0770,%kannel_user,%kannel_group) %dir %_var/spool/kannel
%attr(0770,%kannel_user,%kannel_group) %dir %_localstatedir/kannel
%attr(0770,%kannel_user,%kannel_group) %dir %_localstatedir/kannel/cdr

%files devel
%_includedir/kannel/
%dir %_libdir/kannel/
%_libdir/kannel/*.a

%changelog
* Sat Oct 29 2011 Michael Bochkaryov <misha@altlinux.ru> 1.5.0-alt7.svn4937
- Small fix in init-scripts

* Fri Oct 28 2011 Michael Bochkaryov <misha@altlinux.ru> 1.5.0-alt6.svn4937
- Source updated from fresh SVN (2011-10-26)
- The following patches applied:
  + PAM authentication support;
  + DLR delivery retry
  + kannel-store-tools utility for managing SMS store
- Configuration rewritten

* Mon Sep 12 2011 Dmitriy Kruglikov <dkr@altlinux.org> 1.5.0-alt5cvs20110819
- Tuned

* Mon Sep 12 2011 Dmitriy Kruglikov <dkr@altlinux.org> 1.5.0-alt4cvs20110819
- Internal DLR storage

* Fri Sep 09 2011 Dmitriy Kruglikov <dkr@altlinux.org> 1.5.0-alt3cvs20110819
- Added configs with included other

* Wed Sep 07 2011 Dmitriy Kruglikov <dkr@altlinux.org> 1.5.0-alt2cvs20110819
- Prepared for buiding

* Wed Sep 07 2011 Michael Bochkaryov <misha@altlinux.ru> 1.5.0-alt2cvs20110819
- Update sources from upstream SVN 2011-08-19

* Sun Nov 08 2009 Michael Bochkaryov <misha@altlinux.ru> 1.5.0-alt1.cvs20091101
- Fixed build requirements
- Added loopback smsc module
- Fixed possible crash in HTTP black/white list processing
- Fixed processing of SQL reserved words as table/column names
- Implemented smsc-id option for smpp-tlv
- Some minor fixes (see ChangeLog)
- Disable docs building (to be updated and moved to subpackage)

* Sat Jul 25 2009 Michael Bochkaryov <misha@altlinux.ru> 1.5.0-alt1.cvs20090721
- Version changed to 1.5.0
- Added PAM support patch for sendsms API
- Added DLR retry patch
- Added store_tools utility for SMS storage management
- Added -fPIC build flag for building kannel based software
- wapproxy is packaged

* Fri May 29 2009 Michael Bochkaryov <misha@altlinux.ru> 1.4.3-alt1.cvs20090525
- merge CVS updates up to May 25 2009
  + intermediate DLR support
  + DLR support for mtbatch
  + multi-IP support implemented
  + return SMPP DLR error in dlr_err metadata parameter

* Tue Apr 21 2009 Michael Bochkaryov <misha@altlinux.ru> 1.4.3-alt1.cvs20090417
- build from CVS tree
- optional SMPP TLV support restored

* Tue Mar 03 2009 Grigory Milev <week@altlinux.ru> 1.4.3-alt1
- Please upgrade from 1.4.2 stable to 1.4.3 stable immediately.
  Due to a bug in the 1.4.2 stable release, any DLRs via SMPP v3.4 will cause a
  PANIC condition in bearerbox. - The Kannel Group 

* Wed Jan 14 2009 Grigory Milev <week@altlinux.ru> 1.4.2-alt1
- New version released
- fixed SMP build (docs don't builded on SMP when use make_build, changed to simple make)

* Thu Jan 08 2009 Michael Bochkaryov <misha@altlinux.ru> 1.4.1-alt2.cvs20081203
- new build from fresh CVS meta-data branch (Dec 3 2008)
- logrotate configuration added
- monit configuration added
- enquire_link dump removed from SMPP debug
- disable mutexes status logging

* Sun Jun 22 2008 Michael Bochkaryov <misha@altlinux.ru> 1.4.1-alt1.3.cvs20080124
- init scripts fixed

* Wed Jun 04 2008 Michael Bochkaryov <misha@altlinux.ru> 1.4.1-alt1.2.cvs20080124
- start-stop-daemon removed (unused)

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

