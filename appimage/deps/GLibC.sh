#!/usr/bin/bash

echo 'Copying GLibC'

# Files
copy /usr/bin/ld.so
copy ${LIBDIR}/Mcrt1.o
copy ${LIBDIR}/Scrt1.o
copy ${LIBDIR}/audit
copy ${LIBDIR}/crt?.o
copy ${LIBDIR}/gconv
copy ${LIBDIR}/gcrt1.o
copy ${LIBDIR}/libBrokenLocale.*
copy ${LIBDIR}/libanl.*
copy ${LIBDIR}/ld-linux-x86-64.so.2
copy ${LIBDIR}/libc.*
copy ${LIBDIR}/libc_*
copy ${LIBDIR}/libdl.*
copy ${LIBDIR}/libg.*
copy ${LIBDIR}/libm.*
copy ${LIBDIR}/libm-*
copy ${LIBDIR}/libmcheck.a
copy ${LIBDIR}/libmemusage.so
copy ${LIBDIR}/libmvec.*
copy ${LIBDIR}/libnsl.so.1
copy ${LIBDIR}/libnss_compat.so*
copy ${LIBDIR}/libnss_db.so*
copy ${LIBDIR}/libnss_dns.so*
copy ${LIBDIR}/libnss_files.so*
copy ${LIBDIR}/libnss_hesiod.so*
copy ${LIBDIR}/libpcprofile.so
copy ${LIBDIR}/libpthread.*
copy ${LIBDIR}/libresolv.*
copy ${LIBDIR}/librt.*
copy ${LIBDIR}/libthread_db.so*
copy ${LIBDIR}/libutil.*
copy /usr/lib/locale/C.utf8
copy ${LIBDIR}/rcrt1.o
try_copy_optional \
  "/usr/share/locale/*/LC_MESSAGES/libc.mo" \
  "/usr/share/locale-langpack/*/LC_MESSAGES/libc.mo"

ln -sfr "${AppDir}"/usr/lib "${AppDir}"/usr/lib64
