################################################################################
#
# CITRA
#
################################################################################
# commit 55ec7031ccb2943c2c507620cf4613a86d160670 is reverted by patch, something wrong in it for perfs (patch 004-perf1-revert-core.patch)
# patch 002-perf1.patch while NO_CAST_FROM_ASCII is causing perfs issues too
CITRA_VERSION = 90192124cc644248c5b192e08e96a6bbbe7e0eae
CITRA_SITE = https://github.com/citra-emu/citra.git
CITRA_SITE_METHOD=git
CITRA_GIT_SUBMODULES=YES
CITRA_LICENSE = GPLv2
CITRA_DEPENDENCIES = qt5base qt5tools qt5multimedia fmt boost ffmpeg sdl2

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
CITRA_SUPPORTS_IN_SOURCE_BUILD = NO

CITRA_CONF_OPTS += -DENABLE_QT=ON
CITRA_CONF_OPTS += -DENABLE_QT_TRANSLATION=ON
CITRA_CONF_OPTS += -DARCHITECTURE=x86_64
CITRA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRA_CONF_OPTS += -DENABLE_FFMPEG=ON
CITRA_CONF_OPTS += -DENABLE_FFMPEG_AUDIO_DECODER=ON
CITRA_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

CITRA_CONF_ENV += LDFLAGS=-lpthread

define CITRA_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/bin/Release/citra-qt \
		$(TARGET_DIR)/usr/bin/
endef

define CITRA_EVMAP
    $(INSTALL) -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/citra/3ds.citra.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

CITRA_POST_INSTALL_TARGET_HOOKS = CITRA_EVMAP

$(eval $(cmake-package))
