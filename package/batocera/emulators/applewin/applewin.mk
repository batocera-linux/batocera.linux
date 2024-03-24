################################################################################
#
# applewin
#
################################################################################
# Version: Commits on Mar 4, 2024
APPLEWIN_VERSION = 9dd627599628c22f34e1a7d02f1bb2d7f7e536a6
APPLEWIN_SITE = https://github.com/audetto/AppleWin
APPLEWIN_SITE_METHOD=git
APPLEWIN_GIT_SUBMODULES=YES
APPLEWIN_LICENSE = GPLv2
APPLEWIN_DEPENDENCIES = sdl2 sdl2_image minizip-zlib slirp libpcap boost

APPLEWIN_SUPPORTS_IN_SOURCE_BUILD = NO

APPLEWIN_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
APPLEWIN_CONF_OPTS += -DBUILD_SA2=ON
APPLEWIN_CONF_OPTS += -DBUILD_LIBRETRO=ON

ifeq ($(BR2_PACKAGE_HAS_OPENGL),y)
APPLEWIN_CONF_OPTS += -DSA2_OPENGL=ON
else
APPLEWIN_CONF_OPTS += -DSA2_OPENGL=OFF
endif

define APPLEWIN_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/lib/libretro
        $(INSTALL) -D $(@D)/buildroot-build/source/frontends/libretro/applewin_libretro.so $(TARGET_DIR)/usr/lib/libretro/
        cp -avf $(@D)/buildroot-build/sa2 $(TARGET_DIR)/usr/bin/applewin
        mkdir -p $(TARGET_DIR)/usr/share/applewin
	cp -R $(@D)/resource/* $(TARGET_DIR)/usr/share/applewin/
	rm $(TARGET_DIR)/usr/share/applewin/resource.h
        #cp -avf $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/applewin/applewin.keys $(TARGET_DIR)/usr/share/evmapy/
endef

$(eval $(cmake-package))
