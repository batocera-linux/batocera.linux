################################################################################
#
# Batocera Emulation Station
#
################################################################################

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
        BATOCERA_EMULATIONSTATION_CONF_OPTS = -DRPI_VERSION=3
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
        BATOCERA_EMULATIONSTATION_CONF_OPTS = -DRPI_VERSION=2
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI1),y)
        BATOCERA_EMULATIONSTATION_CONF_OPTS = -DRPI_VERSION=1
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI0),y)
        BATOCERA_EMULATIONSTATION_CONF_OPTS = -DRPI_VERSION=1
endif

BATOCERA_EMULATIONSTATION_SITE = $(call github,batocera-linux,batocera-emulationstation,$(BATOCERA_EMULATIONSTATION_VERSION))
BATOCERA_EMULATIONSTATION_VERSION = master

BATOCERA_EMULATIONSTATION_LICENSE = MIT
BATOCERA_EMULATIONSTATION_DEPENDENCIES = sdl2 sdl2_mixer boost freeimage freetype eigen alsa-lib \
	libcurl openssl

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
BATOCERA_EMULATIONSTATION_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
BATOCERA_EMULATIONSTATION_DEPENDENCIES += libgles
endif


define BATOCERA_EMULATIONSTATION_RPI_FIXUP
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/CMakeLists.txt
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/CMakeLists.txt
	$(SED) 's|/usr/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/CMakeLists.txt
endef

BATOCERA_EMULATIONSTATION_PRE_CONFIGURE_HOOKS += BATOCERA_EMULATIONSTATION_RPI_FIXUP

$(eval $(cmake-package))
