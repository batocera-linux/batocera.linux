################################################################################
#
# CITRA-ANDROID
#
################################################################################
# Version.: Commits on Sep 11, 2021
CITRA_ANDROID_VERSION = 6f6f9a091085305154375028f3342aad16697f3c
CITRA_ANDROID_SITE = https://github.com/citra-emu/citra-android.git
CITRA_ANDROID_SITE_METHOD=git
CITRA_ANDROID_GIT_SUBMODULES=YES
CITRA_ANDROID_LICENSE = GPLv2
CITRA_ANDROID_DEPENDENCIES = fmt boost ffmpeg sdl2

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
CITRA_ANDROID_SUPPORTS_IN_SOURCE_BUILD = NO

CITRA_ANDROID_CONF_OPTS += -DENABLE_QT=OFF
CITRA_ANDROID_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRA_ANDROID_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRA_ANDROID_CONF_OPTS += -DENABLE_FFMPEG=ON
CITRA_ANDROID_CONF_OPTS += -DENABLE_FFMPEG_AUDIO_DECODER=ON
CITRA_ANDROID_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

CITRA_ANDROID_CONF_ENV += LDFLAGS=-lpthread

define CITRA_ANDROID_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/bin/Release/citra \
		$(TARGET_DIR)/usr/bin/
endef

define CITRA_ANDROID_EVMAP
	$(INSTALL) -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/citra-android/3ds.citra.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

CITRA_ANDROID_POST_INSTALL_TARGET_HOOKS = CITRA_ANDROID_EVMAP

$(eval $(cmake-package))
