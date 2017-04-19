################################################################################
#
# Emulation Station
#
################################################################################
EMULATION_STATION_VERSION = 1.0.2
EMULATION_STATION_SOURCE = v$(EMULATION_STATION_VERSION).tar.gz
EMULATION_STATION_SITE = https://github.com/Aloshi/EmulationStation/archive
EMULATION_STATION_LICENSE = MIT
EMULATION_STATION_DEPENDENCIES = sdl boost freeimage freetype eigen alsa-lib \
	libgles

define EMULATION_STATION_RPI_FIXUP
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/CMakeLists.txt
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/CMakeLists.txt
endef

EMULATION_STATION_PRE_CONFIGURE_HOOKS += EMULATION_STATION_RPI_FIXUP

$(eval $(cmake-package))
