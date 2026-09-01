################################################################################
#
# applewin
#
################################################################################
# Version: Commits on Aug 29, 2026
APPLEWIN_VERSION = d495cfe427358d6b1f185a60bc2b3a8c7c5e8107
APPLEWIN_SITE = https://github.com/audetto/AppleWin
APPLEWIN_SITE_METHOD=git
APPLEWIN_GIT_SUBMODULES=YES
APPLEWIN_LICENSE = GPLv2
APPLEWIN_DEPENDENCIES = sdl2 sdl2_image minizip-zlib slirp libpcap boost host-xxd
APPLEWIN_EMULATOR_INFO = applewin.emulator.yml applewin.libretro.core.yml

APPLEWIN_SUPPORTS_IN_SOURCE_BUILD = NO

APPLEWIN_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
APPLEWIN_CONF_OPTS += -DBUILD_SA2=ON
APPLEWIN_CONF_OPTS += -DBUILD_LIBRETRO=ON

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
APPLEWIN_CONF_OPTS += -DSA2_OPENGL=ON
else
APPLEWIN_CONF_OPTS += -DSA2_OPENGL=OFF
endif

define APPLEWIN_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/lib/libretro
    $(INSTALL) -D $(@D)/buildroot-build/source/frontends/libretro/applewin_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/
    cp -avf $(@D)/buildroot-build/sa2 $(TARGET_DIR)/usr/bin/applewin
    mkdir -p $(TARGET_DIR)/usr/share/applewin
    cp -R $(@D)/resource/* $(TARGET_DIR)/usr/share/applewin/
    rm $(TARGET_DIR)/usr/share/applewin/resource.h
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
