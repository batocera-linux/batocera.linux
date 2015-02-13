################################################################################
#
# mupen64plus audio omx
#
################################################################################

MUPEN64PLUS_OMX_VERSION = master
MUPEN64PLUS_OMX_SITE = $(call github,gizmo98,mupen64plus-audio-omx,$(MUPEN64PLUS_OMX_VERSION))
MUPEN64PLUS_OMX_LICENSE = MIT
MUPEN64PLUS_OMX_DEPENDENCIES = sdl2 alsa-lib rpi-userland
MUPEN64PLUS_OMX_INSTALL_STAGING = YES

MUPEN64PLUS_OMX_GL_CFLAGS = -L$(STAGING_DIR)/usr/lib
MUPEN64PLUS_OMX_GL_LDLIBS = -lbcm_host -lGLESv2 -lEGL

MUPEN64PLUS_OMX_PARAMS = VC=1 USE_GLES=1 MACHINE=armv6l

ifeq ($(BR2_ARM_CPU_ARMV6),y)
        MUPEN64PLUS_OMX_PARAMS += VFP_HARD=1
	MUPEN64PLUS_OMX_HOST_CPU = armv6
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
        MUPEN64PLUS_OMX_PARAMS += NEON=1
	MUPEN64PLUS_OMX_HOST_CPU = armv7
endif

define MUPEN64PLUS_OMX_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(STAGING_DIR)/usr" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
        APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
	GL_CFLAG="$(MUPEN64PLUS_OMX_GL_CFLAGS)" \
	GL_LDLIBS="$(MUPEN64PLUS_OMX_GL_LDLIBS)" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_OMX_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" 
endef

define MUPEN64PLUS_OMX_INSTALL_TARGET_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(TARGET_DIR)/usr/" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
        APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
	GL_CFLAG="$(MUPEN64PLUS_OMX_GL_CFLAGS)" \
	GL_LDLIBS="$(MUPEN64PLUS_OMX_GL_LDLIBS)" \
	INSTALL="/usr/bin/install" \
	INSTALL_STRIP_FLAG="" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_OMX_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" install
endef

define MUPEN64PLUS_OMX_CROSS_FIXUP
        $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/projects/unix/Makefile
        $(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/projects/unix/Makefile
endef

MUPEN64PLUS_OMX_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_OMX_CROSS_FIXUP

$(eval $(generic-package))
