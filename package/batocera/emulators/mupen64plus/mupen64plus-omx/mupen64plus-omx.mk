################################################################################
#
# mupen64plus audio omx
#
################################################################################
# Version.: Commits on Feb 13, 2016 (discontinued)
MUPEN64PLUS_OMX_VERSION = 3225ca52206c0a484a22212a76c9cf94e219c8c7
MUPEN64PLUS_OMX_SITE = $(call github,ricrpi,mupen64plus-audio-omx,$(MUPEN64PLUS_OMX_VERSION))
MUPEN64PLUS_OMX_LICENSE = GPLv2
MUPEN64PLUS_OMX_DEPENDENCIES = sdl2 alsa-lib rpi-userland mupen64plus-core
MUPEN64PLUS_OMX_INSTALL_STAGING = YES

define MUPEN64PLUS_OMX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
		PREFIX="$(STAGING_DIR)/usr" \
		PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
		HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
		APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
		GL_CFLAGS="$(MUPEN64PLUS_GL_CFLAGS)" \
		GL_LDLIBS="$(MUPEN64PLUS_GL_LDLIBS)" \
		-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) MACHINE=armv6l OPTFLAGS="$(TARGET_CXXFLAGS)"
endef

define MUPEN64PLUS_OMX_INSTALL_TARGET_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
		PREFIX="$(TARGET_DIR)/usr/" \
		PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
		HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
		APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
		GL_CFLAGS="$(MUPEN64PLUS_GL_CFLAGS)" \
		GL_LDLIBS="$(MUPEN64PLUS_GL_LDLIBS)" \
		INSTALL="/usr/bin/install" \
		INSTALL_STRIP_FLAG="" \
		-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) MACHINE=armv6l OPTFLAGS="$(TARGET_CXXFLAGS)" install
endef

define MUPEN64PLUS_OMX_CROSS_FIXUP
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/projects/unix/Makefile
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/projects/unix/Makefile
endef

MUPEN64PLUS_OMX_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_OMX_CROSS_FIXUP

$(eval $(generic-package))
