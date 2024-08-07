################################################################################
#
# melonds
#
################################################################################
# Version: Commits on May 16, 2024
MELONDS_VERSION = a72b79a55ad2d61811af11b1b911f6af863f66c2
MELONDS_SITE = https://github.com/Arisotura/melonDS.git
MELONDS_SITE_METHOD=git
MELONDS_GIT_SUBMODULES=YES
MELONDS_LICENSE = GPLv2
MELONDS_DEPENDENCIES = sdl2 qt6base qt6multimedia slirp libepoxy libarchive

MELONDS_SUPPORTS_IN_SOURCE_BUILD = NO

MELONDS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
MELONDS_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr"
MELONDS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
MELONDS_CONF_OPTS += -DUSE_QT6=ON

define MELONDS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/melonDS \
		$(TARGET_DIR)/usr/bin/
endef

define MELONDS_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/melonds/nds.melonds.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

MELONDS_POST_INSTALL_TARGET_HOOKS += MELONDS_POST_PROCESS

$(eval $(cmake-package))
