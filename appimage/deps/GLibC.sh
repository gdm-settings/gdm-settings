#!/usr/bin/bash

echo 'Copying GLibC'

# Files
copy /usr/bin/ld.so
copy /usr/lib/Mcrt1.o
copy /usr/lib/Scrt1.o
copy /usr/lib/audit
copy /usr/lib/crt?.o
copy /usr/lib/gconv
copy /usr/lib/gcrt1.o
copy /usr/lib/libBrokenLocale.*
copy /usr/lib/libanl.*
copy /usr/lib/ld-linux-x86-64.so.2
copy /usr/lib/libc.*
copy /usr/lib/libc_*
copy /usr/lib/libdl.*
copy /usr/lib/libg.*
copy /usr/lib/libm.*
copy /usr/lib/libm-*
copy /usr/lib/libmcheck.a
copy /usr/lib/libmemusage.so
copy /usr/lib/libmvec.*
copy /usr/lib/libnsl.so.1
copy /usr/lib/libnss_compat.so*
copy /usr/lib/libnss_db.so*
copy /usr/lib/libnss_dns.so*
copy /usr/lib/libnss_files.so*
copy /usr/lib/libnss_hesiod.so*
copy /usr/lib/libpcprofile.so
copy /usr/lib/libpthread.*
copy /usr/lib/libresolv.*
copy /usr/lib/librt.*
copy /usr/lib/libthread_db.so*
copy /usr/lib/libutil.*
copy /usr/lib/locale/C.UTF-8
copy /usr/lib/rcrt1.o
copy /usr/share/locale/*/LC_MESSAGES/libc.mo

ln -sfr "${AppDir}"/usr/lib "${AppDir}"/usr/lib64
