################################################################################
#
# mupen64plus video gles2
#
################################################################################
# Version.: Commits on Aug 8, 2019 
MUPEN64PLUS_GLES2_VERSION = 1f53773f9045f5f18b895fe41f166d272175d72f
MUPEN64PLUS_GLES2_SITE = $(call github,ricrpi,mupen64plus-video-gles2n64,$(MUPEN64PLUS_GLES2_VERSION))
MUPEN64PLUS_GLES2_LICENSE = GPL
MUPEN64PLUS_GLES2_DEPENDENCIES = sdl2 alsa-lib mupen64plus-core
MUPEN64PLUS_GLES2_INSTALL_STAGING = YES

define MUPEN64PLUS_GLES2_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
		PREFIX="$(STAGING_DIR)/usr" \
		PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
		HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
		APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
		GL_CFLAGS="$(MUPEN64PLUS_GL_CFLAGS)" \
		GL_LDLIBS="$(MUPEN64PLUS_GL_LDLIBS)" \
		-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)"
endef

define MUPEN64PLUS_GLES2_INSTALL_TARGET_CMDS
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
		-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" install
		
		cp $(@D)/data/gles2n64.conf    "$(TARGET_DIR)/usr/share/mupen64plus/"
		cp $(@D)/data/gles2n64rom.conf "$(TARGET_DIR)/usr/share/mupen64plus/"
endef

define MUPEN64PLUS_GLES2_CROSS_FIXUP
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/projects/unix/Makefile
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/projects/unix/Makefile
endef

MUPEN64PLUS_GLES2_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_GLES2_CROSS_FIXUP

$(eval $(generic-package))
