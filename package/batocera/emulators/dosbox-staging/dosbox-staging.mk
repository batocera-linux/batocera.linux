################################################################################
#
# DosBox Staging
#
################################################################################
# Version.: Commits on Oct 25, 2020
DOSBOX_STAGING_VERSION = 3918ebed39dbc83b51cf76c251b799d62072279a
DOSBOX_STAGING_SITE = $(call github,dosbox-staging,dosbox-staging,$(DOSBOX_STAGING_VERSION))
DOSBOX_STAGING_DEPENDENCIES = sdl2 sdl2_net zlib libpng libogg libvorbis opus opusfile
DOSBOX_STAGING_LICENSE = GPLv2

define DOSBOX_STAGING_CONFIGURE_CMDS
    cd $(@D); ./autogen.sh; $(TARGET_CONFIGURE_OPTS) CROSS_COMPILE="$(HOST_DIR)/usr/bin/" LIBS="-lvorbisfile -lvorbis -logg" \
        ./configure --host="$(GNU_TARGET_NAME)" \
                    --enable-core-inline \
                    --enable-dynrec \
                    --enable-unaligned_memory \
                    --prefix=/usr \
                    --with-sdl-prefix="$(STAGING_DIR)/usr";
endef

$(eval $(autotools-package))
