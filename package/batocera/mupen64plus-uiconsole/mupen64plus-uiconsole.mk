################################################################################
#
# mupen64plus ui-console
#
################################################################################

MUPEN64PLUS_UICONSOLE_VERSION = 1e9a53456c150de61ed722984e7a337f9a9d7c64
MUPEN64PLUS_UICONSOLE_SITE = $(call github,mupen64plus,mupen64plus-ui-console,$(MUPEN64PLUS_UICONSOLE_VERSION))
MUPEN64PLUS_UICONSOLE_LICENSE = MIT
MUPEN64PLUS_UICONSOLE_DEPENDENCIES = sdl2 alsa-lib mupen64plus-core


define MUPEN64PLUS_UICONSOLE_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(STAGING_DIR)/usr" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" 
endef

define MUPEN64PLUS_UICONSOLE_INSTALL_TARGET_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(TARGET_DIR)/usr" \
	APIDIR="$(STAGING_DIR)/usr/include/mupen64plus" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
	INSTALL="/usr/bin/install" \
	INSTALL_STRIP_FLAG="" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" install
#	$(INSTALL) -m 0644 $(@D)/projects/unix/libmupen64plus.so.2.0.0 $(TARGET_DIR)/usr/lib
endef

define MUPEN64PLUS_UICONSOLE_CROSS_FIXUP
        $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/projects/unix/Makefile
        $(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/projects/unix/Makefile
endef

MUPEN64PLUS_UICONSOLE_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_UICONSOLE_CROSS_FIXUP


$(eval $(generic-package))
