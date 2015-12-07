################################################################################
#
# Emulation Station 2 - recalbox version https://github.com/digitalLumberjack/recalbox-emulationstation
#
################################################################################

ifeq ($(BR2_PACKAGE_RECALBOX_EMULATIONSTATION2_ARCADE),y)
        RECALBOX_EMULATIONSTATION2_VERSION = recalbox-buildroot-arcade
else 
	ifeq ($(BR2_cortex_a7),y)
		RECALBOX_EMULATIONSTATION2_VERSION = v3.3.0-rpi2 
	else
        	RECALBOX_EMULATIONSTATION2_VERSION = v3.3.0-rpi1
	endif
endif

RECALBOX_EMULATIONSTATION2_SITE = $(call github,digitallumberjack,recalbox-emulationstation,$(RECALBOX_EMULATIONSTATION2_VERSION))

RECALBOX_EMULATIONSTATION2_LICENSE = MIT
RECALBOX_EMULATIONSTATION2_DEPENDENCIES = sdl2 sdl2_mixer boost freeimage freetype eigen alsa-lib \
	libgles libcurl openssl

define RECALBOX_EMULATIONSTATION2_RPI_FIXUP
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/CMakeLists.txt
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/CMakeLists.txt
endef

RECALBOX_EMULATIONSTATION2_PRE_CONFIGURE_HOOKS += RECALBOX_EMULATIONSTATION2_RPI_FIXUP

$(eval $(cmake-package))
