################################################################################
#
# MAME
#
################################################################################
# Version.: Commits on Nov 1, 2020
MAME_VERSION = mame0226
MAME_SITE = $(call github,mamedev,mame,$(MAME_VERSION))
MAME_DEPENDENCIES = sdl2 zlib libpng fontconfig
MAME_LICENSE = MAME

define MAME_BUILD_CMDS
    cd $(@D); \
	CFLAGS="--sysroot=$(STAGING_DIR)"   \
	CXXFLAGS="--sysroot=$(STAGING_DIR)" \
	LDFLAGS="--sysroot=$(STAGING_DIR) -lasound -lfontconfig"  \
	PKG_CONFIG="$(STAGING_DIR)/usr/bin/pkg-config --define-prefix" \
	$(MAKE) TARGETOS=linux OSD=sdl \
	TARGET=mame \
	SUBTARGET=tiny \
	PTR64=1 \
	VERBOSE=1 \
	OVERRIDE_CC="$(TARGET_CC)" OVERRIDE_CXX="$(TARGET_CXX)" OVERRIDE_LD="$(TARGET_LD)" CROSS_BUILD=1 \
	NO_USE_PORTAUDIO=1 \
	USE_SYSTEM_LIB_ZLIB=1 \
	USE_SYSTEM_LIB_JPEG=1 \
	USE_SYSTEM_LIB_FLAC=1 \
	USE_SYSTEM_LIB_SQLITE3=1 \
	SDL_INSTALL_ROOT=$(STAGING_DIR)/usr USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig \
	TOOLS=1
endef

#	USE_SYSTEM_LIB_RAPIDJSON=1 \
#	USE_SYSTEM_LIB_LUA=1 \
#	USE_SYSTEM_LIB_PUGIXML=1 \

$(eval $(generic-package))
