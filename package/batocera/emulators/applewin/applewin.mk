################################################################################
#
# applewin
#
################################################################################
# Version: Commits on Jul 23, 2023
APPLEWIN_VERSION = ed3f07122e1fb16d036ceb5c670f7f049b278176
APPLEWIN_SITE = https://github.com/audetto/AppleWin
APPLEWIN_SITE_METHOD=git
APPLEWIN_GIT_SUBMODULES=YES
APPLEWIN_LICENSE = GPLv2
APPLEWIN_DEPENDENCIES = sdl2 minizip-zlib slirp libpcap boost

APPLEWIN_SUPPORTS_IN_SOURCE_BUILD = NO

APPLEWIN_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
APPLEWIN_CONF_OPTS += -DBUILD_SA2=OFF # Depends on OpenGL
APPLEWIN_CONF_OPTS += -DBUILD_LIBRETRO=ON

#APPLEWIN_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
