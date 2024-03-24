################################################################################
#
# snes9x
#
################################################################################

SNES9X_VERSION = 1e1c45be07bf5760e73414d9ed0253d6dedb8605
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

ifeq ($(BR2_x86_64),y)
    SNES9X_CONF_OPTS += -DUSE_X11=ON
else
    SNES9X_CONF_OPTS += -DUSE_X11=OFF
endif

define SNES9X_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        $(INSTALL) -m 0755 $(@D)/qt/snes9x-qt $(TARGET_DIR)/usr/bin
endef

$(eval $(cmake-package))
