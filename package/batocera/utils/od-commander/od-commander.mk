################################################################################
#
# od-commander
#
################################################################################

OD_COMMANDER_VERSION = 60e30e2e8f0819bc118cf546ee7fd52fc8b91e87
OD_COMMANDER_SITE = $(call github,od-contrib,commander,$(OD_COMMANDER_VERSION))
OD_COMMANDER_DEPENDENCIES = sdl2 sdl2_gfx sdl2_image sdl2_ttf dejavu nanum-font
OD_COMMANDER_RESOURCES_DIR = /usr/share/od-commander/

OD_COMMANDER_CONF_OPTS += \
	-DWITH_SYSTEM_SDL_GFX=ON -DWITH_SYSTEM_SDL_TTF=ON \
	-DFONTS=$(BR2_PACKAGE_OD_COMMANDER_FONTS) \
	-DLOW_DPI_FONTS=$(BR2_PACKAGE_OD_COMMANDER_FONTS_LOW_DPI) \
	-DRES_DIR="\"$(OD_COMMANDER_RESOURCES_DIR)\""

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
	OD_COMMANDER_CONF_OPTS += -DBATOCERA_HANDHELD=1 -DFILE_SYSTEM="\"/dev/mmcblk0p2\""
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
	OD_COMMANDER_CONF_OPTS += -DBATOCERA_HANDHELD=1 -DFILE_SYSTEM="\"/dev/mmcblk0p2\""
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	OD_COMMANDER_CONF_OPTS += -DFILE_SYSTEM="\"/dev/sda2\"" # FIXME this should be dynamic...
else
	OD_COMMANDER_CONF_OPTS += -DFILE_SYSTEM="\"/dev/mmcblk0p2\""
endif

ifeq ($(BR2_PACKAGE_OD_COMMANDER_AUTOSCALE),y)
OD_COMMANDER_CONF_OPTS += -DAUTOSCALE=1
endif

ifneq ($(BR2_PACKAGE_OD_COMMANDER_PPU_X),"")
OD_COMMANDER_CONF_OPTS += -DPPU_X=$(BR2_PACKAGE_OD_COMMANDER_PPU_X)
endif

ifneq ($(BR2_PACKAGE_OD_COMMANDER_PPU_Y),"")
OD_COMMANDER_CONF_OPTS += -DPPU_Y=$(BR2_PACKAGE_OD_COMMANDER_PPU_Y)
endif

ifneq ($(BR2_PACKAGE_OD_COMMANDER_WIDTH),"")
OD_COMMANDER_CONF_OPTS += -DSCREEN_WIDTH=$(BR2_PACKAGE_OD_COMMANDER_WIDTH)
endif

ifneq ($(BR2_PACKAGE_OD_COMMANDER_HEIGHT),"")
OD_COMMANDER_CONF_OPTS += -DSCREEN_HEIGHT=$(BR2_PACKAGE_OD_COMMANDER_HEIGHT)
endif

define OD_COMMANDER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)$(OD_COMMANDER_RESOURCES_DIR)
	$(INSTALL) -m 0644 $(@D)/res/Fiery_Turk.ttf \
	  $(TARGET_DIR)$(OD_COMMANDER_RESOURCES_DIR)
	$(INSTALL) -m 0644 $(@D)/res/*.png \
	  $(TARGET_DIR)$(OD_COMMANDER_RESOURCES_DIR)
	$(INSTALL) -m 0755 -D $(OD_COMMANDER_BUILDDIR)commander \
	  $(TARGET_DIR)/usr/bin/od-commander
	 cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/od-commander/odcommander.keys \
	  $(TARGET_DIR)/usr/share/evmapy/
endef

$(eval $(cmake-package))
