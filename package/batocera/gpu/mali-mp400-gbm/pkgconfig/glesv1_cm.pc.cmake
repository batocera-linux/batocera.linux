prefix=/usr
exec_prefix=${prefix}
libdir=${prefix}/@CMAKE_INSTALL_LIBDIR@
includedir=${prefix}/@CMAKE_INSTALL_INCLUDEDIR@

Name: glesv1_cm
Description: Mali OpenGL ES 1.1 CM library
Version: 1.1
Libs: -L${libdir} -lGLESv1_CM
Libs.private: -lm -lpthread
Cflags: -I${includedir}
