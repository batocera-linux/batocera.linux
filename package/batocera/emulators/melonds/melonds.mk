################################################################################
#
# melonds
#
################################################################################

MELONDS_VERSION = 1.1
MELONDS_SITE = https://github.com/Arisotura/melonDS.git
MELONDS_SITE_METHOD=git
MELONDS_GIT_SUBMODULES=YES
MELONDS_LICENSE = GPLv2
MELONDS_DEPENDENCIES += ecm sdl2 slirp libepoxy libarchive libenet
MELONDS_DEPENDENCIES += qt6base qt6svg qt6multimedia 

MELONDS_SUPPORTS_IN_SOURCE_BUILD = NO

MELONDS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
MELONDS_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr"
MELONDS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
MELONDS_CONF_OPTS += -DUSE_QT6=ON

# wayland is currently broken, don't set this...
#ifeq ($(BR2_PACKAGE_WAYLAND),y)
#MELONDS_CONF_OPTS += -DENABLE_WAYLAND=ON
#else
MELONDS_CONF_OPTS += -DENABLE_WAYLAND=OFF
#endif

define MELONDS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/melonDS \
		$(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
