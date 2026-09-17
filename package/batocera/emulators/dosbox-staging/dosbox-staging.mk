################################################################################
#
# dosbox-staging
#
################################################################################

DOSBOX_STAGING_VERSION = v0.83.0
DOSBOX_STAGING_SITE = $(call github,dosbox-staging,dosbox-staging,$(DOSBOX_STAGING_VERSION))
DOSBOX_STAGING_DEPENDENCIES = asio iir libpng libogg libvorbis opus opusfile
DOSBOX_STAGING_DEPENDENCIES += sdl2 sdl2_image speexdsp zlib
DOSBOX_STAGING_DEPENDENCIES += fluidsynth munt slirp alsa-lib
DOSBOX_STAGING_LICENSE = GPLv2
DOSBOX_STAGING_EMULATOR_INFO = dosbox_staging.emulator.yml

DOSBOX_STAGING_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
DOSBOX_STAGING_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DOSBOX_STAGING_CONF_OPTS += -DUSE_SYSTEM_LIBS=ON
DOSBOX_STAGING_CONF_OPTS += -DIS_PRESET_USED=ON
DOSBOX_STAGING_CONF_OPTS += -DOPT_TESTS=OFF

define DOSBOX_STAGING_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/dosbox-staging \
		$(TARGET_DIR)/usr/bin/dosbox-staging
	mkdir -p $(TARGET_DIR)/usr/share/dosbox-staging
	rsync -a --exclude='meson.build' --exclude='.git*' \
		$(@D)/resources/ $(TARGET_DIR)/usr/share/dosbox-staging/
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
