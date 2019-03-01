################################################################################
#
# Batocera Emulation Station
#
################################################################################

ifeq ($(BR2_PACKAGE_KODI),y)
	BATOCERA_EMULATIONSTATION_CONF_OPTS += -DDISABLE_KODI=0
else
	BATOCERA_EMULATIONSTATION_CONF_OPTS += -DDISABLE_KODI=1
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
	BATOCERA_EMULATIONSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=1
else
	BATOCERA_EMULATIONSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=0
endif

# Version.: Commits on Feb 02, 2019
BATOCERA_EMULATIONSTATION_VERSION = 93d33a2727918e493de22ad10d6b56a733d04f3d
BATOCERA_EMULATIONSTATION_SITE = $(call github,batocera-linux,batocera-emulationstation,$(BATOCERA_EMULATIONSTATION_VERSION))

BATOCERA_EMULATIONSTATION_LICENSE = MIT
BATOCERA_EMULATIONSTATION_DEPENDENCIES = sdl2 sdl2_mixer boost libfreeimage freetype eigen alsa-lib \
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
