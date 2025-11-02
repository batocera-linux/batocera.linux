################################################################################
#
# batocera-emulationstation
#
################################################################################
# Last update: Commits on Oct 28, 2025
BATOCERA_EMULATIONSTATION_VERSION = 9247e381e66ea10fd5af9acfdc935df4d3aaece2
BATOCERA_EMULATIONSTATION_SITE = https://github.com/batocera-linux/batocera-emulationstation
BATOCERA_EMULATIONSTATION_SITE_METHOD = git
BATOCERA_EMULATIONSTATION_LICENSE = MIT
BATOCERA_EMULATIONSTATION_GIT_SUBMODULES = YES
BATOCERA_EMULATIONSTATION_LICENSE = MIT, Apache-2.0
BATOCERA_EMULATIONSTATION_DEPENDENCIES = sdl2 sdl2_mixer vlc libfreeimage freetype alsa-lib
BATOCERA_EMULATIONSTATION_DEPENDENCIES += libcurl rapidjson batocera-es-system host-gettext
# install in staging for debugging (gdb)
BATOCERA_EMULATIONSTATION_INSTALL_STAGING = YES
# BATOCERA_EMULATIONSTATION_OVERRIDE_SRCDIR = /sources/batocera-emulationstation

BATOCERA_EMULATIONSTATION_CONF_OPTS += \
    -DCMAKE_CXX_FLAGS=-D$(call UPPERCASE,$(BATOCERA_SYSTEM_ARCH))

ifeq ($(BR2_PACKAGE_XAPP_XINIT),y)
BATOCERA_EMULATIONSTATION_DEPENDENCIES += xapp_xinit
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
BATOCERA_EMULATIONSTATION_DEPENDENCIES += libmali
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-lmali
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCMAKE_SHARED_LINKER_FLAGS=-lmali
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL)$(BR2_PACKAGE_XSERVER_XORG_SERVER),yy)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DGL=ON
else
ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DGLES2=ON
endif
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DBCM=ON -DRPI=ON
endif

ifeq ($(BR2_PACKAGE_ESPEAK),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DENABLE_TTS=ON
BATOCERA_EMULATIONSTATION_DEPENDENCIES += espeak
endif

ifeq ($(BR2_PACKAGE_KODI)$(BR2_PACKAGE_KODI21),y)
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

BATOCERA_EMULATIONSTATION_SOURCE_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation

BATOCERA_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN=\
    $(shell grep -E '^SCREENSCRAPER_DEV_LOGIN=' \
	$(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/keys.txt | cut -d = -f 2-)
BATOCERA_EMULATIONSTATION_KEY_GAMESDB_APIKEY=\
    $(shell grep -E '^GAMESDB_APIKEY=' \
	$(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/keys.txt | cut -d = -f 2-)
BATOCERA_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN=\
    $(shell grep -E '^CHEEVOS_DEV_LOGIN=' \
	$(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/keys.txt | cut -d = -f 2-)
BATOCERA_EMULATIONSTATION_KEY_HFS_DEV_LOGIN=\
    $(shell grep -E '^HFS_DEV_LOGIN=' \
	$(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/keys.txt | cut -d = -f 2-)

ifneq ($(BATOCERA_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN),)
BATOCERA_EMULATIONSTATION_CONF_OPTS += \
    "-DSCREENSCRAPER_DEV_LOGIN=$(BATOCERA_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN)"
endif
ifneq ($(BATOCERA_EMULATIONSTATION_KEY_GAMESDB_APIKEY),)
BATOCERA_EMULATIONSTATION_CONF_OPTS += \
    "-DGAMESDB_APIKEY=$(BATOCERA_EMULATIONSTATION_KEY_GAMESDB_APIKEY)"
endif
ifneq ($(BATOCERA_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN),)
BATOCERA_EMULATIONSTATION_CONF_OPTS += \
    "-DCHEEVOS_DEV_LOGIN=$(BATOCERA_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN)"
endif
ifneq ($(BATOCERA_EMULATIONSTATION_KEY_HFS_DEV_LOGIN),)
BATOCERA_EMULATIONSTATION_CONF_OPTS += \
    "-DHFS_DEV_LOGIN=$(BATOCERA_EMULATIONSTATION_KEY_HFS_DEV_LOGIN)"
endif

define BATOCERA_EMULATIONSTATION_RPI_FIXUP
	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/opt/vc|$(STAGING_DIR)/usr|g' $(@D)/CMakeLists.txt
	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/usr|$(STAGING_DIR)/usr|g'    $(@D)/CMakeLists.txt
endef

define BATOCERA_EMULATIONSTATION_EXTERNAL_POS
	cp $(STAGING_DIR)/usr/share/batocera-es-system/es_external_translations.h \
	    $(STAGING_DIR)/usr/share/batocera-es-system/es_keys_translations.h $(@D)/es-app/src
	for P in $(STAGING_DIR)/usr/share/batocera-es-system/locales/*; \
	    do if test -e $$P/batocera-es-system.po; then \
	    cp $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po \
	    $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po.tmp && \
	    $(HOST_DIR)/bin/msgcat \
		$(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po.tmp \
	    $$P/batocera-es-system.po > \
	    $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po; fi; done
endef

define BATOCERA_EMULATIONSTATION_RESOURCES
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/flags
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/battery
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/services
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/shaders
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/shaders/kawase
	$(INSTALL) -m 0644 -D $(@D)/resources/*.* \
	    $(TARGET_DIR)/usr/share/emulationstation/resources
	$(INSTALL) -m 0644 -D $(@D)/resources/help/*.* \
	    $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0644 -D $(@D)/resources/flags/*.* \
	    $(TARGET_DIR)/usr/share/emulationstation/resources/flags
	$(INSTALL) -m 0644 -D $(@D)/resources/battery/*.* \
	    $(TARGET_DIR)/usr/share/emulationstation/resources/battery
	$(INSTALL) -m 0644 -D $(@D)/resources/shaders/*.* \
	    $(TARGET_DIR)/usr/share/emulationstation/resources/shaders
	$(INSTALL) -m 0644 -D $(@D)/resources/shaders/*.* \
	    $(TARGET_DIR)/usr/share/emulationstation/resources/shaders/kawase

	# es_input.cfg
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/emulationstation
	cp $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/controllers/es_input.cfg $(TARGET_DIR)/usr/share/emulationstation

	# savestates config
	$(INSTALL) -m 0644 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/es_savestates.cfg $(TARGET_DIR)/usr/share/emulationstation

	# hooks
	cp $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/batocera-preupdate-gamelists-hook \
	    $(TARGET_DIR)/usr/bin/
endef

### S31emulationstation
# default for most of architectures
BATOCERA_EMULATIONSTATION_PREFIX = SDL_NOMOUSE=1
BATOCERA_EMULATIONSTATION_CMD = emulationstation-standalone
BATOCERA_EMULATIONSTATION_ARGS = --no-splash $${EXTRA_OPTS}
BATOCERA_EMULATIONSTATION_POSTFIX = \&

# disabling cec. causing perf issue on init/deinit
#ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCEC=OFF
#else
#BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCEC=ON
#endif

# on SPLASH_MPV, the splash with video + es splash is ok
ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_MPV),y)
BATOCERA_EMULATIONSTATION_ARGS = $${EXTRA_OPTS}
endif

# es splash is ok when there is no video
ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_IMAGE),y)
BATOCERA_EMULATIONSTATION_ARGS = $${EXTRA_OPTS}
endif

## on x86/x86_64: startx runs ES
ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
BATOCERA_EMULATIONSTATION_PREFIX =
BATOCERA_EMULATIONSTATION_CMD = startx
BATOCERA_EMULATIONSTATION_ARGS = --windowed
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_XORG
endif

## on Wayland sway runs ES
ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND_SWAY),y)
BATOCERA_EMULATIONSTATION_CMD = sway-launch
BATOCERA_EMULATIONSTATION_DEPENDENCIES += sway
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_WAYLAND_SWAY
endif

ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND_LABWC),y)
BATOCERA_EMULATIONSTATION_CMD = labwc-launch
BATOCERA_EMULATIONSTATION_DEPENDENCIES += labwc
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_WAYLAND_LABWC
endif

define BATOCERA_EMULATIONSTATION_XORG
	$(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/xorg/xinitrc \
	    $(BINARIES_DIR)/batocera-target/etc/X11/xinit/xinitrc
endef

define BATOCERA_EMULATIONSTATION_WAYLAND_SWAY
	$(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/sway/04-sway.sh \
	    $(TARGET_DIR)/etc/profile.d/04-sway.sh
    $(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/sway/config \
	    $(TARGET_DIR)/etc/sway/config
    $(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/sway/sway-launch \
	    $(TARGET_DIR)/usr/bin/sway-launch
endef

define BATOCERA_EMULATIONSTATION_WAYLAND_LABWC
    mkdir -p $(TARGET_DIR)/usr/share/labwc
	$(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/labwc/04-labwc.sh \
	    $(TARGET_DIR)/etc/profile.d/04-labwc.sh
	$(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/labwc/rc.xml \
	    $(TARGET_DIR)/usr/share/labwc/rc.xml
	$(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/labwc/S14labwc \
	    $(TARGET_DIR)/etc/init.d/S14labwc
    $(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/labwc/autostart \
	    $(TARGET_DIR)/usr/share/labwc/autostart
    $(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/labwc/autostart_* \
	    $(TARGET_DIR)/usr/share/labwc/
    $(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/wayland/labwc/labwc-launch \
	    $(TARGET_DIR)/usr/bin/labwc-launch
endef

define BATOCERA_EMULATIONSTATION_BOOT
	$(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/S31emulationstation \
	    $(TARGET_DIR)/etc/init.d/S31emulationstation
	$(INSTALL) -D -m 0755 $(BATOCERA_EMULATIONSTATION_SOURCE_PATH)/emulationstation-standalone \
	    $(TARGET_DIR)/usr/bin/emulationstation-standalone
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
