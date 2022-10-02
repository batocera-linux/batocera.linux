################################################################################
#
# vita3k
#
################################################################################
# Version: Commits on Aug 31, 2022
# Don't bump due to requiring a browser with commit - 3b74ceb
VITA3K_VERSION = 486c41b6baa2754fa5c0d63a208d9e43a8d2a187
VITA3K_SITE = https://github.com/vita3k/vita3k
VITA3K_SITE_METHOD=git
VITA3K_GIT_SUBMODULES=YES
VITA3K_LICENSE = GPLv3
VITA3K_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf zlib libogg libvorbis python-ruamel-yaml

VITA3K_SUPPORTS_IN_SOURCE_BUILD = NO

VITA3K_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF \
                   -DUSE_DISCORD_RICH_PRESENCE=OFF -DUSE_VITA3K_UPDATE=OFF

define VITA3K_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/vita3k/
	cp -R $(@D)/buildroot-build/bin/* $(TARGET_DIR)/usr/bin/vita3k/
	rm $(TARGET_DIR)/usr/bin/vita3k/update-vita3k.sh
endef

define VITA3K_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/vita3k/psvita.vita3k.keys $(TARGET_DIR)/usr/share/evmapy
endef

VITA3K_POST_INSTALL_TARGET_HOOKS = VITA3K_INSTALL_EVMAPY

$(eval $(cmake-package))
