################################################################################
#
# RetroLX Emulation Station
#
################################################################################

RETROLX_EMULATIONSTATION_VERSION = 2675f178b6590f1a60738fda74ed6b5de04467f2
RETROLX_EMULATIONSTATION_SITE = https://github.com/RetroLX/retrolx-emulationstation
RETROLX_EMULATIONSTATION_SITE_METHOD = git
RETROLX_EMULATIONSTATION_LICENSE = MIT
RETROLX_EMULATIONSTATION_GIT_SUBMODULES = YES
RETROLX_EMULATIONSTATION_LICENSE = MIT, Apache-2.0
RETROLX_EMULATIONSTATION_DEPENDENCIES = sdl2 sdl2_mixer libfreeimage freetype alsa-lib libcurl vlc rapidjson
# install in staging for debugging (gdb)
RETROLX_EMULATIONSTATION_INSTALL_STAGING = YES
# RETROLX_EMULATIONSTATION_OVERRIDE_SRCDIR = /sources/batocera-emulationstation

RETROLX_EMULATIONSTATION_CONF_OPTS += -DCMAKE_CXX_FLAGS=-D$(call UPPERCASE,$(BATOCERA_SYSTEM_ARCH))

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
RETROLX_EMULATIONSTATION_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-lmali -DCMAKE_SHARED_LINKER_FLAGS=-lmali
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
RETROLX_EMULATIONSTATION_CONF_OPTS += -DGLES2=ON
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
RETROLX_EMULATIONSTATION_CONF_OPTS += -DEGL=ON
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
RETROLX_EMULATIONSTATION_CONF_OPTS += -DBCM=ON
endif

ifeq ($(BR2_PACKAGE_KODI),y)
RETROLX_EMULATIONSTATION_CONF_OPTS += -DDISABLE_KODI=0
else
RETROLX_EMULATIONSTATION_CONF_OPTS += -DDISABLE_KODI=1
endif


ifeq ($(BR2_PACKAGE_XORG7),y)
RETROLX_EMULATIONSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=1
else
RETROLX_EMULATIONSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=0
endif

RETROLX_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN=$(shell grep -E '^SCREENSCRAPER_DEV_LOGIN=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/frontends/emulationstation/retrolx-emulationstation/keys.txt | cut -d = -f 2-)
RETROLX_EMULATIONSTATION_KEY_GAMESDB_APIKEY=$(shell grep -E '^GAMESDB_APIKEY=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/frontends/emulationstation/retrolx-emulationstation/keys.txt | cut -d = -f 2-)
RETROLX_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN=$(shell grep -E '^CHEEVOS_DEV_LOGIN=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/frontends/emulationstation/retrolx-emulationstation/keys.txt | cut -d = -f 2-)

ifneq ($(RETROLX_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN),)
RETROLX_EMULATIONSTATION_CONF_OPTS += "-DSCREENSCRAPER_DEV_LOGIN=$(RETROLX_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN)"
endif
ifneq ($(RETROLX_EMULATIONSTATION_KEY_GAMESDB_APIKEY),)
RETROLX_EMULATIONSTATION_CONF_OPTS += "-DGAMESDB_APIKEY=$(RETROLX_EMULATIONSTATION_KEY_GAMESDB_APIKEY)"
endif
ifneq ($(RETROLX_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN),)
RETROLX_EMULATIONSTATION_CONF_OPTS += "-DCHEEVOS_DEV_LOGIN=$(RETROLX_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN)"
endif

define RETROLX_EMULATIONSTATION_RPI_FIXUP
	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/opt/vc|$(STAGING_DIR)/usr|g' $(@D)/CMakeLists.txt
	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/usr|$(STAGING_DIR)/usr|g'    $(@D)/CMakeLists.txt
endef

define RETROLX_EMULATIONSTATION_RESOURCES
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/flags
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/battery
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/services
	$(INSTALL) -m 0644 -D $(@D)/resources/*.* $(TARGET_DIR)/usr/share/emulationstation/resources
	$(INSTALL) -m 0644 -D $(@D)/resources/help/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0644 -D $(@D)/resources/flags/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/flags
	$(INSTALL) -m 0644 -D $(@D)/resources/battery/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/battery
	$(INSTALL) -m 0644 -D $(@D)/resources/services/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/services

	# es_input.cfg
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/emulationstation
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/frontends/emulationstation/retrolx-emulationstation/controllers/es_input.cfg \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/emulationstation
endef

### S31emulationstation
# default for most of architectures
RETROLX_EMULATIONSTATION_PREFIX = SDL_NOMOUSE=1
RETROLX_EMULATIONSTATION_CMD = /usr/bin/emulationstation
RETROLX_EMULATIONSTATION_ARGS = --no-splash $${EXTRA_OPTS}
RETROLX_EMULATIONSTATION_POSTFIX = \&
RETROLX_EMULATIONSTATION_CONF_OPTS += -DCEC=OFF

# on rpi1: dont load ES in background
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
RETROLX_EMULATIONSTATION_POSTFIX = \& sleep 5
endif

# on SPLASH_MPV, the splash with video + es splash is ok
ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_MPV),y)
RETROLX_EMULATIONSTATION_ARGS = $${EXTRA_OPTS}
endif

# es splash is ok when there is no video
ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_IMAGE)$(BR2_PACKAGE_BATOCERA_SPLASH_ROTATE_IMAGE),y)
RETROLX_EMULATIONSTATION_ARGS = $${EXTRA_OPTS}
endif

# # on x86/x86_64: startx runs ES
ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
RETROLX_EMULATIONSTATION_PREFIX =
RETROLX_EMULATIONSTATION_CMD = startx
RETROLX_EMULATIONSTATION_ARGS =
endif

# # Run through Weston compositor on Wayland
ifeq ($(BR2_PACKAGE_WAYLAND)$(BR2_PACKAGE_WESTON),yy)
RETROLX_EMULATIONSTATION_PREFIX = SDL_NOMOUSE=1 SDL_VIDEODRIVER=wayland XDG_RUNTIME_DIR=/userdata/system
endif

define RETROLX_EMULATIONSTATION_BOOT
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/frontends/emulationstation/retrolx-emulationstation/S31emulationstation $(TARGET_DIR)/etc/init.d/S31emulationstation
	sed -i -e 's;%RETROLX_EMULATIONSTATION_PREFIX%;${RETROLX_EMULATIONSTATION_PREFIX};g' \
		-e 's;%RETROLX_EMULATIONSTATION_CMD%;${RETROLX_EMULATIONSTATION_CMD};g' \
		-e 's;%RETROLX_EMULATIONSTATION_ARGS%;${RETROLX_EMULATIONSTATION_ARGS};g' \
		-e 's;%RETROLX_EMULATIONSTATION_POSTFIX%;${RETROLX_EMULATIONSTATION_POSTFIX};g' \
		$(TARGET_DIR)/etc/init.d/S31emulationstation
endef

RETROLX_EMULATIONSTATION_PRE_CONFIGURE_HOOKS += RETROLX_EMULATIONSTATION_RPI_FIXUP
RETROLX_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += RETROLX_EMULATIONSTATION_RESOURCES
RETROLX_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += RETROLX_EMULATIONSTATION_BOOT

$(eval $(cmake-package))
