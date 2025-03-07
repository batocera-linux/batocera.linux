################################################################################
#
# gamescope
#
################################################################################

GAMESCOPE_VERSION = 3.15.16
GAMESCOPE_SITE = https://github.com/Plagman/gamescope.git
GAMESCOPE_METHOD=git
GAMESCOPE_SUBMODULES=YES
GAMESCOPE_LICENSE = BSD-2-Clause
GAMESCOPE_DEPENDENCIES = sdl2 libdrm libx11 libxdamage libxext libxfixes libxrender libxres libxtst

GAMESCOPE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GAMESCOPE_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
GAMESCOPE_CONF_OPTS += -DARCHITECTURE_x86_64=ON

define GAMESCOPE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin

	$(INSTALL) -D $(@D)/gamescope $(TARGET_DIR)/usr/bin/gamescope
endef

$(eval $(meson-package))
