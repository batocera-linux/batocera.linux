################################################################################
#
# mupen64plus video GLIDEN64
#
################################################################################


MUPEN64PLUS_GLIDEN64_VERSION = e8892846428e20bfceb4fb83867f39d49de697c5
MUPEN64PLUS_GLIDEN64_SITE = $(call github,gizmo98,GLideN64,$(MUPEN64PLUS_GLIDEN64_VERSION))
MUPEN64PLUS_GLIDEN64_LICENSE = MIT
MUPEN64PLUS_GLIDEN64_DEPENDENCIES = sdl2 alsa-lib rpi-userland mupen64plus-core
MUPEN64PLUS_GLIDEN64_INSTALL_STAGING = YES
MUPEN64PLUS_GLIDEN64_CONF_OPTS = -DMUPENPLUSAPI=On -DBCMHOST=On
MUPEN64PLUS_GLIDEN64_SUBDIR = /src/


define MUPEN64PLUS_GLIDEN64_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/*.* \
		$(TARGET_DIR)/usr/lib/mupen64plus
endef

define MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_FIXUP
        $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/src/CMakeLists.txt
        $(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/src/CMakeLists.txt
endef

MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_FIXUP


$(eval $(cmake-package))


