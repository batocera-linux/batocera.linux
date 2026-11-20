################################################################################
#
# cubeb
#
################################################################################
# Version: Commits on Oct 22, 2026
CUBEB_VERSION = dcd7cddafa4b95776cf5d117549ad58e17f23764
CUBEB_SITE = $(call github,mozilla,cubeb,$(CUBEB_VERSION))
CUBEB_LICENSE = ISC
CUBEB_LICENSE_FILES = LICENSE
CUBEB_INSTALL_STAGING = YES

CUBEB_CONF_OPTS = \
	-DBUILD_SHARED_LIBS=ON \
	-DBUILD_TESTS=OFF \
	-DBUILD_TOOLS=OFF \
	-DBUILD_RUST_LIBS=OFF \
	-DUSE_SANITIZERS=OFF \
	-DLAZY_LOAD_LIBS=OFF

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
CUBEB_DEPENDENCIES += alsa-lib
endif

ifeq ($(BR2_PACKAGE_JACK2),y)
CUBEB_DEPENDENCIES += jack2
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
CUBEB_DEPENDENCIES += pulseaudio
endif

ifeq ($(BR2_PACKAGE_SPEEXDSP),y)
CUBEB_DEPENDENCIES += speexdsp
endif

$(eval $(cmake-package))
