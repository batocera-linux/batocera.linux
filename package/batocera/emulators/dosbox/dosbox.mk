################################################################################
#
# DosBox
#
################################################################################
# Version.: Commits on May 02, 2020
DOSBOX_VERSION = dosbox-x-v0.83.1
DOSBOX_SITE = $(call github,joncampbell123,dosbox-x,$(DOSBOX_VERSION))
DOSBOX_DEPENDENCIES = sdl2 sdl2_net sdl_sound zlib libpng libogg libvorbis
DOSBOX_LICENSE = GPLv2

define DOSBOX_CONFIGURE_CMDS
    cd $(@D); ./autogen.sh; $(TARGET_CONFIGURE_OPTS) CROSS_COMPILE="$(HOST_DIR)/usr/bin/" LIBS="-lvorbisfile -lvorbis -logg" \
        ./configure --host="$(GNU_TARGET_NAME)" \
                    --enable-core-inline \
                    --enable-dynrec \
                    --enable-unaligned_memory \
                    --prefix=/usr \
                    --disable-sdl \
                    --enable-sdl2 \
                    --with-sdl2-prefix="$(STAGING_DIR)/usr";
endef

$(eval $(autotools-package))