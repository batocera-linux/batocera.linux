################################################################################
#
# dosbox-x
#
################################################################################

DOSBOX_X_VERSION = dosbox-x-v2025.02.01
DOSBOX_X_SITE = $(call github,joncampbell123,dosbox-x,$(DOSBOX_X_VERSION))
DOSBOX_X_DEPENDENCIES = sdl2 sdl2_net fluidsynth zlib libpng libogg libvorbis linux-headers
DOSBOX_X_LICENSE = GPLv2
DOSBOX_X_AUTORECONF = YES

DOSBOX_X_CONF_OPTS = --host="$(GNU_TARGET_NAME)" \
                     --enable-core-inline \
                     --enable-dynrec \
                     --enable-unaligned_memory \
                     --prefix=/usr \
                     --disable-sdl \
                     --enable-sdl2 \
                     --with-sdl2-prefix="$(STAGING_DIR)/usr"

define DOSBOX_X_CONFIGURE_CONFIG
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/dosbox
    cp -rf $(@D)/dosbox-x.reference.conf \
        $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/dosbox/dosboxx.conf
endef

DOSBOX_X_POST_INSTALL_TARGET_HOOKS += DOSBOX_X_CONFIGURE_CONFIG

$(eval $(autotools-package))
