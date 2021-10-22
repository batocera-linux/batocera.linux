################################################################################
#
# BENNUGD_BGDC
#
################################################################################
# Version.: Commits on Oct 06, 2021
BENNUGD_BGDC_VERSION = 60ee3389efcf9b402d66035e87f33d17d70cbd83
BENNUGD_BGDC_SITE = $(call github,christianhaitian,bennugd-monolithic,$(BENNUGD_BGDC_VERSION))

BENNUGD_BGDC_DEPENDENCIES = sdl2 sdl2_mixer libtre
BENNUGD_BGDC_LICENSE = GPL-2.0

BENNUGD_BGDC_SUPPORTS_IN_SOURCE_BUILD = NO
BENNUGD_BGDC_SUBDIR = projects/cmake/bgdc

define BENNUGD_BGDC_INSTALL_TARGET_CMDS
	cp -pvr $(@D)/projects/cmake/bgdc/buildroot-build/bgdc $(TARGET_DIR)/usr/bin
	
	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	#cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/bennugd/bennugd.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
