################################################################################
#
# raze
#
################################################################################
# Version: Commits on Nov 6, 2022
RAZE_VERSION = b4a49ea228e0fff196092ccf6e03b8550fa4592c
RAZE_SITE = $(call github,coelckers,Raze,$(RAZE_VERSION))
RAZE_LICENSE = GPLv2
RAZE_DEPENDENCIES = sdl2 bzip2 fluidsynth libgtk3 openal mesa3d libglu libglew zmusic
RAZE_SUPPORTS_IN_SOURCE_BUILD = NO

RAZE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RAZE_CONF_OPTS += -DCMAKE_CROSSCOMPILING=FALSE
RAZE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    RAZE_CONF_OPTS += -DHAVE_VULKAN=ON
else
    RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    RAZE_CONF_OPTS += -DHAVE_GLES2=ON
else
    RAZE_CONF_OPTS += -DHAVE_GLES2=OFF
endif

define RAZE_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/raze $(TARGET_DIR)/usr/bin/raze
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/raze.pk3 $(TARGET_DIR)/usr/share/raze/raze.pk3
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/soundfonts/raze.sf2 $(TARGET_DIR)/usr/share/raze/soundfonts/raze.sf2
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/raze/raze.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
