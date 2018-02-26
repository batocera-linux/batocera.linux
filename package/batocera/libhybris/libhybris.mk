################################################################################
#
# libhybris
#
# Allows to run bionic-based HW adaptations in glibc systems - libs
#
################################################################################
LIBHYBRIS_VERSION = 070c3ab
LIBHYBRIS_SITE    = $(call github,libhybris,libhybris,$(LIBHYBRIS_VERSION))
LIBHYBRIS_SUBDIR  = hybris
LIBHYBRIS_DEPENDENCIES = android-headers
LIBHYBRIS_AUTORECONF = YES
LIBHYBRIS_CONF_ENV += CFLAGS=-I$(BUILD_DIR)/android-headers-25
LIBHYBRIS_INSTALL_STAGING = YES
LIBHYBRIS_PROVIDES = libgles

LIBHYBRIS_ARCH = ${ARCH}
ifeq ($(BR2_aarch64),y)
	LIBHYBRIS_ARCH = arm64
endif

ifeq ($(BR2_arm),y)
	LIBHYBRIS_ARCH = arm
endif

LIBHYBRIS_CONF_OPTS += \
	--enable-arch=${LIBHYBRIS_ARCH} \
	--with-default-egl-platform=fbdev \
	--with-android-headers=${BUILD_DIR}/android-headers-25 \
	--with-default-hybris-ld-library-path=/system/lib \
	--enable-mali-quirks

ifeq ($(BR2_PACKAGE_LIBHYBRIS_DEBUG), y)
LIBHYBRIS_CONF_OPTS += \
	--enable-debug \
	--enable-trace
endif

$(eval $(autotools-package))
