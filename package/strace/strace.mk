################################################################################
#
# strace
#
################################################################################

STRACE_VERSION = 5.2
STRACE_SOURCE = strace-$(STRACE_VERSION).tar.xz
STRACE_SITE = https://strace.io/files/$(STRACE_VERSION)
STRACE_LICENSE = LGPL-2.1+
STRACE_LICENSE_FILES = COPYING LGPL-2.1-or-later
STRACE_CONF_OPTS = --enable-mpers=check

# Regenerate v4l2_pix_fmts.h since we patch v4l2_pix_fmts.in
define STRACE_GEN_V4L2_PIX_FMT
	$(@D)/xlat/gen.sh $(@D)/xlat/v4l2_pix_fmts.in $(@D)/xlat/v4l2_pix_fmts.h
endef

STRACE_POST_PATCH_HOOKS += STRACE_GEN_V4L2_PIX_FMT

# strace bundle some kernel headers to build libmpers, this mixes userspace
# headers and kernel headers which break the build with musl.
# The stddef.h from gcc is used instead of the one from musl.
ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
STRACE_CONF_OPTS += st_cv_m32_mpers=no \
	st_cv_mx32_mpers=no
endif

ifeq ($(BR2_PACKAGE_LIBUNWIND),y)
STRACE_DEPENDENCIES += libunwind
STRACE_CONF_OPTS += --with-libunwind
else
STRACE_CONF_OPTS += --without-libunwind
endif

# Demangling symbols in stack trace needs libunwind and libiberty.
ifeq ($(BR2_PACKAGE_BINUTILS)$(BR2_PACKAGE_LIBUNWIND),yy)
STRACE_DEPENDENCIES += binutils
STRACE_CONF_OPTS += --with-libiberty=check
else
STRACE_CONF_OPTS += --without-libiberty
endif

ifeq ($(BR2_PACKAGE_PERL),)
define STRACE_REMOVE_STRACE_GRAPH
	rm -f $(TARGET_DIR)/usr/bin/strace-graph
endef

STRACE_POST_INSTALL_TARGET_HOOKS += STRACE_REMOVE_STRACE_GRAPH
endif

$(eval $(autotools-package))
