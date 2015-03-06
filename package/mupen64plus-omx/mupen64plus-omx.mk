################################################################################
#
# mupen64plus audio omx
#
################################################################################

MUPEN64PLUS_OMX_VERSION = 63939f7cc2acac457bdecf536075109a9d261f03
MUPEN64PLUS_OMX_SITE = $(call github,ricrpi,mupen64plus-audio-omx,$(MUPEN64PLUS_OMX_VERSION))
MUPEN64PLUS_OMX_LICENSE = MIT
MUPEN64PLUS_OMX_DEPENDENCIES = sdl2 alsa-lib rpi-userland mupen64plus-core
MUPEN64PLUS_OMX_INSTALL_STAGING = YES


define MUPEN64PLUS_OMX_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(STAGING_DIR)/usr" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
        APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
	GL_CFLAGS="$(MUPEN64PLUS_GL_CFLAGS)" \
	GL_LDLIBS="$(MUPEN64PLUS_GL_LDLIBS)" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) MACHINE=armv6l OPTFLAGS="$(TARGET_CXXFLAGS)" 
endef

define MUPEN64PLUS_OMX_INSTALL_TARGET_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
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
