################################################################################
#
# snes9x
#
################################################################################
# Version: Commits on Jan 24, 2025
SNES9X_VERSION = 663738341a43e15f5e00fd8fd36672da6089a694
SNES9X_SITE = https://github.com/snes9xgit/snes9x.git
SNES9X_SITE_METHOD = git
SNES9X_GIT_SUBMODULES = YES
SNES9X_LICENSE = GPL-2.0+
SNES9X_LICENSE_FILES = Copyright.txt License.txt

SNES9X_DEPENDENCIES = qt6base
SNES9X_SUBDIR = qt

SNES9X_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
SNES9X_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SNES9X_CONF_OPTS += -DBUILD_STATIC_LIBS=ON

ifeq ($(BR2_PACKAGE_XORG7),y)
    SNES9X_CONF_OPTS += -DUSE_X11=ON
    SNES9X_DEPENDENCIES += xlib_libX11
else
    SNES9X_CONF_OPTS += -DUSE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    SNES9X_CONF_OPTS += -DUSE_WAYLAND=ON
    SNES9X_DEPENDENCIES += wayland
else
    SNES9X_CONF_OPTS += -DUSE_WAYLAND=OFF
endif

define SNES9X_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        $(INSTALL) -m 0755 $(@D)/qt/snes9x-qt $(TARGET_DIR)/usr/bin
endef

$(eval $(cmake-package))
