################################################################################
#
# citra
#
################################################################################

CITRA_VERSION = nightly-1903
CITRA_SITE = https://github.com/citra-emu/citra-nightly.git
CITRA_SITE_METHOD=git
CITRA_GIT_SUBMODULES=YES
CITRA_LICENSE = GPLv2
CITRA_DEPENDENCIES += fmt boost ffmpeg sdl2 fdk-aac qt6base qt6tools qt6multimedia
CITRA_SUPPORTS_IN_SOURCE_BUILD = NO

CITRA_GIT_SUBMODULES = YES

CITRA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRA_CONF_OPTS += -DENABLE_QT_TRANSLATION=ON

CITRA_CONF_OPTS += -DENABLE_QT=ON
CITRA_INSTALL_TARGET_CMDS_BIN = citra-qt

CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRA_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CITRA_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
CITRA_CONF_OPTS += -DENABLE_COMPATIBILITY_LIST_DOWNLOAD=ON
CITRA_CONF_OPTS += -DENABLE_FFMPEG_VIDEO_DUMPER=ON
CITRA_CONF_OPTS += -DENABLE_FFMPEG_AUDIO_DECODER=ON
CITRA_CONF_OPTS += -DUSE_SYSTEM_BOOST=ON
CITRA_CONF_OPTS += -DUSE_SYSTEM_SDL2=ON
CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRA_CONF_OPTS += -DENABLE_OPENAL=OFF

CITRA_CONF_ENV += LDFLAGS=-lpthread

define CITRA_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib
	$(INSTALL) -D $(@D)/buildroot-build/bin/Release/$(CITRA_INSTALL_TARGET_CMDS_BIN) \
		$(TARGET_DIR)/usr/bin/
endef

define CITRA_EVMAP
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/citra/3ds.citra.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

CITRA_POST_INSTALL_TARGET_HOOKS = CITRA_EVMAP

$(eval $(cmake-package))
