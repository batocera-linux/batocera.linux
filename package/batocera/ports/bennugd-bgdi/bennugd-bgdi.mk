################################################################################
#
# BENNUGD_BGDI
#
################################################################################
# Version.: Commits on Oct 06, 2021
BENNUGD_BGDI_VERSION = 60ee3389efcf9b402d66035e87f33d17d70cbd83
BENNUGD_BGDI_SITE = $(call github,christianhaitian,bennugd-monolithic,$(BENNUGD_BGDI_VERSION))

BENNUGD_BGDI_DEPENDENCIES = sdl2 sdl2_mixer libtre
BENNUGD_BGDI_LICENSE = GPL-2.0

BENNUGD_BGDI_SUPPORTS_IN_SOURCE_BUILD = NO
BENNUGD_BGDI_SUBDIR = projects/cmake/bgdi

define BENNUGD_BGDI_INSTALL_TARGET_CMDS
	cp -pvr $(@D)/projects/cmake/bgdi/buildroot-build/bgdi $(TARGET_DIR)/usr/bin
endef

$(eval $(cmake-package))
