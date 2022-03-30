prefix=/usr
exec_prefix=${prefix}
libdir=${prefix}/@CMAKE_INSTALL_LIBDIR@
includedir=${prefix}/@CMAKE_INSTALL_INCLUDEDIR@

Name: gbm
Description: Mali gbm library
Version: 10.4.0
Libs: -L${libdir} -lgbm
Libs.private: -lm -lpthread
Cflags: -I${includedir}
