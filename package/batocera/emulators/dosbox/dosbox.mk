################################################################################
#
# DosBox
#
################################################################################
# Version.: Commits on Jan 08, 2020
DOSBOX_VERSION = 411481d3c760a7f25bc530c97da7ae008e63e0ad
DOSBOX_SITE = $(call github,duganchen,dosbox,$(DOSBOX_VERSION))
DOSBOX_DEPENDENCIES = sdl2 sdl2_net sdl_sound zlib libpng libogg libvorbis
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