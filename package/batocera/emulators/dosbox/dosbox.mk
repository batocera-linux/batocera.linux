################################################################################
#
# dosbox
#
################################################################################
# Version.: Commits on Jan 12, 2020
DOSBOX_VERSION = e6b88ad03202d1f74e329f54f213d3b070bd6202
DOSBOX_SITE = $(call github,duganchen,dosbox,$(DOSBOX_VERSION))
DOSBOX_DEPENDENCIES = fluidsynth libglew libogg libpng libvorbis sdl2 sdl2_net zlib
DOSBOX_LICENSE = GPLv2
DOSBOX_AUTORECONF = YES

ifeq ($(BR2_PACKAGE_LIBGLU),y)
DOSBOX_DEPENDENCIES += libglu
endif

DOSBOX_CONF_OPTS = \
    --host="$(GNU_TARGET_NAME)" \
    --includedir="$(STAGING_DIR)/usr/include" \
    --enable-core-inline \
    --enable-dynrec \
    --enable-unaligned_memory \
    --prefix=/usr \
    --with-sdl-prefix="$(STAGING_DIR)/usr"

$(eval $(autotools-package))
