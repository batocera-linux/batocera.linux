################################################################################
#
# Batocera Emulation Station
#
################################################################################

# Last update: May 13, 2022
BATOCERA_EMULATIONSTATION_VERSION = 5f1cd6d5efc8d4cbebcafaac18854e1916161859
BATOCERA_EMULATIONSTATION_SITE = https://github.com/batocera-linux/batocera-emulationstation
BATOCERA_EMULATIONSTATION_SITE_METHOD = git
BATOCERA_EMULATIONSTATION_LICENSE = MIT
BATOCERA_EMULATIONSTATION_GIT_SUBMODULES = YES
BATOCERA_EMULATIONSTATION_LICENSE = MIT, Apache-2.0
BATOCERA_EMULATIONSTATION_DEPENDENCIES = sdl2 sdl2_mixer libfreeimage freetype alsa-lib libcurl vlc rapidjson pulseaudio-utils batocera-es-system host-gettext
# install in staging for debugging (gdb)
BATOCERA_EMULATIONSTATION_INSTALL_STAGING = YES
# BATOCERA_EMULATIONSTATION_OVERRIDE_SRCDIR = /sources/batocera-emulationstation

BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCMAKE_CXX_FLAGS=-D$(call UPPERCASE,$(BATOCERA_SYSTEM_ARCH))

ifeq ($(BR2_PACKAGE_MALI_T760)$(BR2_PACKAGE_MALI_T860),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-lmali -DCMAKE_SHARED_LINKER_FLAGS=-lmali
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DGLES2=ON
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DEGL=ON
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DBCM=ON -DRPI=ON
endif

ifeq ($(BR2_PACKAGE_ESPEAK),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DENABLE_TTS=ON
BATOCERA_EMULATIONSTATION_DEPENDENCIES += espeak
endif

ifeq ($(BR2_PACKAGE_KODI),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DDISABLE_KODI=OFF
else
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DDISABLE_KODI=ON
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO_ENABLE_ATOMIC),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DENABLE_PULSE=ON
else
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DENABLE_PULSE=OFF
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=ON
else
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=OFF
endif

BATOCERA_EMULATIONSTATION_CONF_OPTS += -DBATOCERA=ON

BATOCERA_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN=$(shell grep -E '^SCREENSCRAPER_DEV_LOGIN=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/keys.txt | cut -d = -f 2-)
BATOCERA_EMULATIONSTATION_KEY_GAMESDB_APIKEY=$(shell grep -E '^GAMESDB_APIKEY=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/keys.txt | cut -d = -f 2-)
BATOCERA_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN=$(shell grep -E '^CHEEVOS_DEV_LOGIN=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/keys.txt | cut -d = -f 2-)
BATOCERA_EMULATIONSTATION_KEY_HFS_DEV_LOGIN=$(shell grep -E '^HFS_DEV_LOGIN=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/keys.txt | cut -d = -f 2-)

ifneq ($(BATOCERA_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN),)
BATOCERA_EMULATIONSTATION_CONF_OPTS += "-DSCREENSCRAPER_DEV_LOGIN=$(BATOCERA_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN)"
endif
ifneq ($(BATOCERA_EMULATIONSTATION_KEY_GAMESDB_APIKEY),)
BATOCERA_EMULATIONSTATION_CONF_OPTS += "-DGAMESDB_APIKEY=$(BATOCERA_EMULATIONSTATION_KEY_GAMESDB_APIKEY)"
endif
ifneq ($(BATOCERA_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN),)
BATOCERA_EMULATIONSTATION_CONF_OPTS += "-DCHEEVOS_DEV_LOGIN=$(BATOCERA_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN)"
endif
ifneq ($(BATOCERA_EMULATIONSTATION_KEY_HFS_DEV_LOGIN),)
BATOCERA_EMULATIONSTATION_CONF_OPTS += "-DHFS_DEV_LOGIN=$(BATOCERA_EMULATIONSTATION_KEY_HFS_DEV_LOGIN)"
endif

define BATOCERA_EMULATIONSTATION_RPI_FIXUP
	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/opt/vc|$(STAGING_DIR)/usr|g' $(@D)/CMakeLists.txt
	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/usr|$(STAGING_DIR)/usr|g'    $(@D)/CMakeLists.txt
endef

define BATOCERA_EMULATIONSTATION_EXTERNAL_POS
	cp $(STAGING_DIR)/usr/share/batocera-es-system/es_external_translations.h $(@D)/es-app/src
	for P in $(STAGING_DIR)/usr/share/batocera-es-system/locales/*; do if test -e $$P/batocera-es-system.po; then cp $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po.tmp && $(HOST_DIR)/bin/msgcat $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po.tmp $$P/batocera-es-system.po > $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po; fi; done
endef

define BATOCERA_EMULATIONSTATION_RESOURCES
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
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/controllers/es_input.cfg \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/emulationstation

	# hooks
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/batocera-preupdate-gamelists-hook $(TARGET_DIR)/usr/bin/
endef

### S31emulationstation
# default for most of architectures
BATOCERA_EMULATIONSTATION_PREFIX = SDL_NOMOUSE=1
BATOCERA_EMULATIONSTATION_CMD = emulationstation-standalone
BATOCERA_EMULATIONSTATION_ARGS = --no-splash $${EXTRA_OPTS}
BATOCERA_EMULATIONSTATION_POSTFIX = \&
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCEC=OFF
else
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCEC=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_OMXPLAYER),y)
BATOCERA_EMULATIONSTATION_ARGS = $${EXTRA_OPTS}
endif

# on SPLASH_MPV, the splash with video + es splash is ok
ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_MPV),y)
BATOCERA_EMULATIONSTATION_ARGS = $${EXTRA_OPTS}
endif

# es splash is ok when there is no video
ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_IMAGE),y)
BATOCERA_EMULATIONSTATION_ARGS = $${EXTRA_OPTS}
endif

# # on x86/x86_64: startx runs ES
ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
BATOCERA_EMULATIONSTATION_PREFIX =
BATOCERA_EMULATIONSTATION_CMD = startx
BATOCERA_EMULATIONSTATION_ARGS = --windowed
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_XINITRC
endif

define BATOCERA_EMULATIONSTATION_XINITRC
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/xinitrc $(TARGET_DIR)/etc/X11/xinit/xinitrc
endef

define BATOCERA_EMULATIONSTATION_BOOT
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/S31emulationstation $(TARGET_DIR)/etc/init.d/S31emulationstation
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/emulationstation-standalone $(TARGET_DIR)/usr/bin/emulationstation-standalone
	sed -i -e 's;%BATOCERA_EMULATIONSTATION_PREFIX%;${BATOCERA_EMULATIONSTATION_PREFIX};g' \
		-e 's;%BATOCERA_EMULATIONSTATION_CMD%;${BATOCERA_EMULATIONSTATION_CMD};g' \
		-e 's;%BATOCERA_EMULATIONSTATION_ARGS%;${BATOCERA_EMULATIONSTATION_ARGS};g' \
		-e 's;%BATOCERA_EMULATIONSTATION_POSTFIX%;${BATOCERA_EMULATIONSTATION_POSTFIX};g' \
		$(TARGET_DIR)/usr/bin/emulationstation-standalone
	sed -i -e 's;%BATOCERA_EMULATIONSTATION_PREFIX%;${BATOCERA_EMULATIONSTATION_PREFIX};g' \
		-e 's;%BATOCERA_EMULATIONSTATION_CMD%;${BATOCERA_EMULATIONSTATION_CMD};g' \
		-e 's;%BATOCERA_EMULATIONSTATION_ARGS%;${BATOCERA_EMULATIONSTATION_ARGS};g' \
		-e 's;%BATOCERA_EMULATIONSTATION_POSTFIX%;${BATOCERA_EMULATIONSTATION_POSTFIX};g' \
		$(TARGET_DIR)/etc/init.d/S31emulationstation
endef

BATOCERA_EMULATIONSTATION_PRE_CONFIGURE_HOOKS += BATOCERA_EMULATIONSTATION_RPI_FIXUP
BATOCERA_EMULATIONSTATION_PRE_CONFIGURE_HOOKS += BATOCERA_EMULATIONSTATION_EXTERNAL_POS
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_RESOURCES
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_BOOT

$(eval $(cmake-package))
