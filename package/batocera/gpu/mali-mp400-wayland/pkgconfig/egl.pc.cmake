prefix=/usr
exec_prefix=${prefix}
libdir=${prefix}/@CMAKE_INSTALL_LIBDIR@
includedir=${prefix}/@CMAKE_INSTALL_INCLUDEDIR@

Name: egl
Description: Mali EGL library
Version: 1.4
Libs: -L${libdir} -lEGL
Libs.private: -lm -lpthread
Cflags: -I${includedir}
