################################################################################
#
# TheXTech
#
################################################################################
# v1.3.7 beta from Aug 27, 2023
THEXTECH_VERSION = 45b37e92827789f8e2ccf7e107ef3e9179fc8213
THEXTECH_SITE = https://github.com/Wohlstand/TheXTech
THEXTECH_SITE_METHOD = git
THEXTECH_GIT_SUBMODULES = YES
THEXTECH_LICENSE = GPLv3
THEXTECH_DEPENDENCIES = sdl2 sdl2_mixer sdl2_ttf

THEXTECH_CONF_ENV = GIT_DISCOVERY_ACROSS_FILESYSTEM=1
THEXTECH_CONF_OPTS = -DTHEXTECH_ENABLE_TTF_SUPPORT=ON -DUSE_SYSTEM_LIBS_DEFAULT=ON

ifeq ($(BR2_PACKAGE_HAS_LIBGL),)
THEXTECH_CONF_OPTS += -DTHEXTECH_BUILD_GL_DESKTOP_MODERN=OFF -DTHEXTECH_BUILD_GL_DESKTOP_LEGACY=OFF
endif

define THEXTECH_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/output/bin/thextech $(TARGET_DIR)/usr/bin/
	cp -avf $(@D)/output/lib/libSDL2_mixer_ext.so* $(TARGET_DIR)/usr/lib/
	cp -avf $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/thextech/thextech.keys $(TARGET_DIR)/usr/share/evmapy/
endef

$(eval $(cmake-package))
