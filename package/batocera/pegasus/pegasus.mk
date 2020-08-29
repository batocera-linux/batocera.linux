################################################################################
#
# Pegasus Frontend
#
################################################################################

PEGASUS_VERSION = 0156545edbe109ce3179f1145f8c1bf33f6935a8
PEGASUS_SITE = https://github.com/mmatyas/pegasus-frontend
PEGASUS_SITE_METHOD = git
PEGASUS_LICENSE = MIT
PEGASUS_GIT_SUBMODULES = YES
PEGASUS_LICENSE = GPLv3
PEGASUS_DEPENDENCIES = qt5base qt5multimedia qt5svg sdl2
# install in staging for debugging (gdb)
#PEGASUS_INSTALL_STAGING = YES

PEGASUS_CONF_OPTS = "USE_SDL_GAMEPAD=1" "INSTALLDIR=$(TARGET_DIR)/usr/bin"

# PEGASUS_OVERRIDE_SRCDIR = /sources/batocera-emulationstation

#ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
#PEGASUS_DEPENDENCIES += libgl
#PEGASUS_CONF_OPTS += -DGL=1
#else
#PEGASUS_CONF_OPTS += -DGL=0
#endif

#ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
#PEGASUS_DEPENDENCIES += libgles
#PEGASUS_CONF_OPTS += -DGLES=1
#else
#PEGASUS_CONF_OPTS += -DGLES=0
#endif

#PEGASUS_CONF_OPTS += -DCMAKE_CXX_FLAGS=-D$(call UPPERCASE,$(BATOCERA_SYSTEM_ARCH))

#ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
#	PEGASUS_CONF_OPTS += -DGLES=ON
#endif

#ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
#	PEGASUS_CONF_OPTS += -DBCM=ON
#endif

#ifneq ($(BR2_PACKAGE_KODI)$(BR2_PACKAGE_KODI18),)
#	PEGASUS_CONF_OPTS += -DDISABLE_KODI=0
#else
#	PEGASUS_CONF_OPTS += -DDISABLE_KODI=1
#endif


#ifeq ($(BR2_PACKAGE_XORG7),y)
#	PEGASUS_CONF_OPTS += -DENABLE_FILEMANAGER=1
#else
#	PEGASUS_CONF_OPTS += -DENABLE_FILEMANAGER=0
#endif

#define PEGASUS_RPI_FIXUP
#	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/opt/vc|$(STAGING_DIR)/usr|g' $(@D)/CMakeLists.txt
#	$(SED) 's|.{CMAKE_FIND_ROOT_PATH}/usr|$(STAGING_DIR)/usr|g'    $(@D)/CMakeLists.txt
#endef

#define PEGASUS_RESOURCES
#	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/help
#	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/flags
#	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/battery
#	$(INSTALL) -m 0644 -D $(@D)/resources/*.* $(TARGET_DIR)/usr/share/emulationstation/resources
#	$(INSTALL) -m 0644 -D $(@D)/resources/help/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/help
#	$(INSTALL) -m 0644 -D $(@D)/resources/flags/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/flags
#	$(INSTALL) -m 0644 -D $(@D)/resources/battery/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/battery

	# es_input.cfg
#	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/emulationstation
#	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/controllers/es_input.cfg \
#		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/emulationstation
#endef


### S31emulationstation

# default for most of architectures (framebuffer and no splash while it doest work nicely with the splash video)
#PEGASUS_BOOT_SCRIPT=S31emulationstation_fb_nosplash

# on rpi, it is not a problem to mix video and es splash
#ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
#	PEGASUS_BOOT_SCRIPT=S31emulationstation_fb_splash
#endif

# on rpi1, 1 cpu
#ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
#	PEGASUS_BOOT_SCRIPT=S31emulationstation_fb_1cpu
#endif

#ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
#	PEGASUS_BOOT_SCRIPT=S31emulationstation_fbegl_nosplash
#endif

#ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
#	PEGASUS_BOOT_SCRIPT=S31emulationstation_xorg
#endif

### ### ###

#define PEGASUS_BOOT
#	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-emulationstation/S31emulationstation/$(PEGASUS_BOOT_SCRIPT) \
#		$(TARGET_DIR)/etc/init.d/S31emulationstation
#endef

#PEGASUS_PRE_CONFIGURE_HOOKS += PEGASUS_RPI_FIXUP
#PEGASUS_POST_INSTALL_TARGET_HOOKS += PEGASUS_RESOURCES
#PEGASUS_POST_INSTALL_TARGET_HOOKS += PEGASUS_BOOT

$(eval $(qmake-package))
