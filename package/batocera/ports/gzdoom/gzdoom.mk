################################################################################
#
# gzdoom
#
################################################################################

GZDOOM_VERSION = g4.8.0
GZDOOM_SITE = https://github.com/coelckers/gzdoom.git
GZDOOM_SITE_METHOD=git
GZDOOM_GIT_SUBMODULES=YES
GZDOOM_LICENSE = GPLv3
GZDOOM_DEPENDENCIES = sdl2 bzip2 fluidsynth libgtk3 openal mesa3d libglu libglew zmusic

GZDOOM_SUPPORTS_IN_SOURCE_BUILD = NO

GZDOOM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DCMAKE_CROSSCOMPILING=FALSE -DBUILD_SHARED_LIBS=OFF

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    GZDOOM_CONF_OPTS += -DHAVE_VULKAN=ON
else
    GZDOOM_CONF_OPTS += -DHAVE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    GZDOOM_CONF_OPTS += -DHAVE_GLES2=ON
else
    GZDOOM_CONF_OPTS += -DHAVE_GLES2=OFF
endif

define GZDOOM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/lib/gzdoom
	mkdir -p $(TARGET_DIR)/usr/share/gzdoom
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/gzdoom $(TARGET_DIR)/usr/bin/gzdoom
	cp -a $(@D)/buildroot-build/gzdoom.pk3 $(TARGET_DIR)/usr/lib/gzdoom/
	cp -a $(@D)/buildroot-build/game_support.pk3 $(TARGET_DIR)/usr/lib/gzdoom/
	cp -a $(@D)/buildroot-build/brightmaps.pk3 $(TARGET_DIR)/usr/share/gzdoom/
	cp -a $(@D)/buildroot-build/game_widescreen_gfx.pk3 $(TARGET_DIR)/usr/share/gzdoom/
	cp -a $(@D)/buildroot-build/lights.pk3 $(TARGET_DIR)/usr/share/gzdoom/
	cp -pr $(@D)/buildroot-build/fm_banks $(TARGET_DIR)/usr/share/gzdoom/
	cp -pr $(@D)/buildroot-build/soundfonts $(TARGET_DIR)/usr/share/gzdoom/

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/gzdoom/gzdoom.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))