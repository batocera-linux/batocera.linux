################################################################################
#
# DosBox
#
################################################################################
# Version.: Commits on Jan 12, 2020
DOSBOX_VERSION = e6b88ad03202d1f74e329f54f213d3b070bd6202
DOSBOX_SITE = $(call github,duganchen,dosbox,$(DOSBOX_VERSION))
DOSBOX_DEPENDENCIES = sdl2 sdl2_net fluidsynth zlib libpng libogg libvorbis
DOSBOX_LICENSE = GPLv2

define DOSBOX_CONFIGURE_CMDS
    cd $(@D); ./autogen.sh; $(TARGET_CONFIGURE_OPTS) CROSS_COMPILE="$(HOST_DIR)/usr/bin/" LIBS="-lvorbisfile -lvorbis -logg" \
        ./configure --host="$(GNU_TARGET_NAME)" \
                    --enable-core-inline \
                    --enable-dynrec \
                    --enable-unaligned_memory \
                    --prefix=/usr \
                    --with-sdl-prefix="$(STAGING_DIR)/usr";
endef

$(eval $(autotools-package))
