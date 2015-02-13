################################################################################
#
# mupen64plus video gles2
#
################################################################################

MUPEN64PLUS_GLES2_VERSION = master
MUPEN64PLUS_GLES2_SITE = $(call github,gizmo98,mupen64plus-video-gles2n64,$(MUPEN64PLUS_GLES2_VERSION))
MUPEN64PLUS_GLES2_LICENSE = MIT
MUPEN64PLUS_GLES2_DEPENDENCIES = sdl2 alsa-lib rpi-userland
MUPEN64PLUS_GLES2_INSTALL_STAGING = YES

MUPEN64PLUS_GLES2_GL_CFLAGS = -I$(STAGING_DIR)/usr/include -L$(STAGING_DIR)/usr/lib
MUPEN64PLUS_GLES2_GL_LDLIBS = -lbcm_host -lGLESv2 -lEGL

MUPEN64PLUS_GLES2_PARAMS = VC=1 USE_GLES=1 

ifeq ($(BR2_ARM_CPU_ARMV6),y)
        MUPEN64PLUS_GLES2_PARAMS += VFP_HARD=1
	MUPEN64PLUS_GLES2_HOST_CPU = armv6
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
        MUPEN64PLUS_GLES2_PARAMS += NEON=1
	MUPEN64PLUS_GLES2_HOST_CPU = armv7
endif

define MUPEN64PLUS_GLES2_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(STAGING_DIR)/usr" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
        APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
	GL_CFLAG="$(MUPEN64PLUS_GLES2_GL_CFLAGS)" \
	GL_LDLIBS="$(MUPEN64PLUS_GLES2_GL_LDLIBS)" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_GLES2_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" 
endef

define MUPEN64PLUS_GLES2_INSTALL_TARGET_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(TARGET_DIR)/usr/" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
        APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
	GL_CFLAG="$(MUPEN64PLUS_GLES2_GL_CFLAGS)" \
	GL_LDLIBS="$(MUPEN64PLUS_GLES2_GL_LDLIBS)" \
	INSTALL="/usr/bin/install" \
	INSTALL_STRIP_FLAG="" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_GLES2_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" install
endef

define MUPEN64PLUS_GLES2_CROSS_FIXUP
        $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/projects/unix/Makefile
        $(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/projects/unix/Makefile
endef

MUPEN64PLUS_GLES2_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_GLES2_CROSS_FIXUP

$(eval $(generic-package))
