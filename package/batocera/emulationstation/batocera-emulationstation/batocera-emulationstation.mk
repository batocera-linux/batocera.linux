################################################################################
#
# Batocera Emulation Station
#
################################################################################

# Version: Commits on Nov 22, 2019
BATOCERA_EMULATIONSTATION_VERSION = c74a63b4127abca6ebce48b84d3b40f66d26247e
BATOCERA_EMULATIONSTATION_SITE = https://github.com/batocera-linux/batocera-emulationstation
BATOCERA_EMULATIONSTATION_SITE_METHOD = git
BATOCERA_EMULATIONSTATION_LICENSE = MIT
BATOCERA_EMULATIONSTATION_GIT_SUBMODULES = YES
BATOCERA_EMULATIONSTATION_LICENSE = MIT, Apache-2.0
BATOCERA_EMULATIONSTATION_DEPENDENCIES = sdl2 sdl2_mixer boost libfreeimage freetype alsa-lib libcurl vlc rapidjson
# install in staging for debugging (gdb)
BATOCERA_EMULATIONSTATION_INSTALL_STAGING = YES

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

# cec is causing issues with es on xu4
ifeq ($(BR2_PACKAGE_LIBCEC_EXYNOS_API),y)
	BATOCERA_EMULATIONSTATION_CONF_OPTS += -DCEC=OFF
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


### S31emulationstation

# default for most of architectures (framebuffer and no splash while it doest work nicely with the splash video)
BATOCERA_EMULATIONSTATION_BOOT_SCRIPT=S31emulationstation_fb_nosplash

# on rpi, it is not a problem to mix video and es splash
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	BATOCERA_EMULATIONSTATION_BOOT_SCRIPT=S31emulationstation_fb_splash
endif

# on rpi1, 1 cpu
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
	BATOCERA_EMULATIONSTATION_BOOT_SCRIPT=S31emulationstation_fb_1cpu
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
	BATOCERA_EMULATIONSTATION_BOOT_SCRIPT=S31emulationstation_fbegl_nosplash
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
	BATOCERA_EMULATIONSTATION_BOOT_SCRIPT=S31emulationstation_xorg
endif

### ### ###

define BATOCERA_EMULATIONSTATION_BOOT
	cp package/batocera/emulationstation/batocera-emulationstation/$(BATOCERA_EMULATIONSTATION_BOOT_SCRIPT) $(TARGET_DIR)/etc/init.d/S31emulationstation
endef

BATOCERA_EMULATIONSTATION_PRE_CONFIGURE_HOOKS += BATOCERA_EMULATIONSTATION_RPI_FIXUP
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_RESOURCES
BATOCERA_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += BATOCERA_EMULATIONSTATION_BOOT

$(eval $(cmake-package))
