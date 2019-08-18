################################################################################
#
# Batocera Emulation Station
#
################################################################################

# Version.: Commits on Aug 16, 2019
BATOCERA_EMULATIONSTATION_VERSION = 2c4d74c0a49aacb2e4697b496e78b437e1ea814b
BATOCERA_EMULATIONSTATION_SITE = https://github.com/batocera-linux/batocera-emulationstation
BATOCERA_EMULATIONSTATION_SITE_METHOD = git
BATOCERA_EMULATIONSTATION_LICENSE = MIT
BATOCERA_EMULATIONSTATION_GIT_SUBMODULES = YES
BATOCERA_EMULATIONSTATION_LICENSE = MIT, Apache-2.0
BATOCERA_EMULATIONSTATION_DEPENDENCIES = sdl2 sdl2_mixer boost libfreeimage freetype alsa-lib libcurl vlc rapidjson

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
BATOCERA_EMULATIONSTATION_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
BATOCERA_EMULATIONSTATION_DEPENDENCIES += libgles
endif

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

define BATOCERA_EMULATIONSTATION_RPI_FIXUP
	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/opt/vc|$(STAGING_DIR)/usr|g' $(@D)/CMakeLists.txt
	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/usr|$(STAGING_DIR)/usr|g'    $(@D)/CMakeLists.txt
endef

define BATOCERA_EMULATIONSTATION_RESOURCES
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0644 -D $(@D)/resources/*.* $(TARGET_DIR)/usr/share/emulationstation/resources
	$(INSTALL) -m 0644 -D $(@D)/resources/help/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/help
endef

BATOCERA_EMULATIONSTATION_PRE_CONFIGURE_HOOKS += BATOCERA_EMULATIONSTATION_RPI_FIXUP
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_RESOURCES

$(eval $(cmake-package))
