################################################################################
#
# mupen64plus video gles2
#
################################################################################

MUPEN64PLUS_GLES2_RICRPI_VERSION = master
MUPEN64PLUS_GLES2_RICRPI_SITE = $(call github,gizmo98,mupen64plus-video-gles2n64,$(MUPEN64PLUS_GLES2_RICRPI_VERSION))
MUPEN64PLUS_GLES2_RICRPI_LICENSE = MIT
MUPEN64PLUS_GLES2_RICRPI_DEPENDENCIES = sdl2 alsa-lib rpi-userland mupen64plus-core
MUPEN64PLUS_GLES2_RICRPI_INSTALL_STAGING = YES


define MUPEN64PLUS_GLES2_RICRPI_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(STAGING_DIR)/usr" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
        APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
	GL_CFLAGS="$(MUPEN64PLUS_GL_CFLAGS)" \
	GL_LDLIBS="$(MUPEN64PLUS_GL_LDLIBS)" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" 
endef

define MUPEN64PLUS_GLES2_RICRPI_INSTALL_TARGET_CMDS
        $(INSTALL) -D -m 0755 $(@D)/projects/unix/mupen64plus-video-n64.so $(TARGET_DIR)/usr/lib/mupen64plus/mupen64plus-video-n64-ricrpi.so
endef

define MUPEN64PLUS_GLES2_RICRPI_CROSS_FIXUP
        $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/projects/unix/Makefile
        $(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/projects/unix/Makefile
endef

MUPEN64PLUS_GLES2_RICRPI_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_GLES2_RICRPI_CROSS_FIXUP

$(eval $(generic-package))
