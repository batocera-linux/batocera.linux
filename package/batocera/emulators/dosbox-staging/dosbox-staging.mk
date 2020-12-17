################################################################################
#
# DosBox Staging
#
################################################################################
# Version.: Release on Dec 02, 2020
DOSBOX_STAGING_VERSION = v0.76.0
DOSBOX_STAGING_SITE = $(call github,dosbox-staging,dosbox-staging,$(DOSBOX_STAGING_VERSION))
DOSBOX_STAGING_DEPENDENCIES = sdl2 sdl2_net zlib libpng libogg libvorbis opus opusfile fluidsynth
DOSBOX_STAGING_LICENSE = GPLv2

DOSBOX_STAGING_CPPFLAGS = -DNDEBUG
DOSBOX_STAGING_CFLAGS   = -O3 -fstrict-aliasing -fno-signed-zeros -fno-trapping-math -fassociative-math -frename-registers -ffunction-sections -fdata-sections
DOSBOX_STAGING_CXXFLAGS = -O3 -fstrict-aliasing -fno-signed-zeros -fno-trapping-math -fassociative-math -frename-registers -ffunction-sections -fdata-sections

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
DOSBOX_STAGING_CFLAGS   += -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
DOSBOX_STAGING_CFLAGS   += -mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mtune=cortex-a53 -mfpu=neon-fp-armv8 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mtune=cortex-a53 -mfpu=neon-fp-armv8 -mfloat-abi=hard
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a72 -mtune=cortex-a72
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a72 -mtune=cortex-a72
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC2)$(BR2_PACKAGE_BATOCERA_TARGET_LIBRETECH_H5)$(BR2_PACKAGE_BATOCERA_TARGET_S905)$(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mtune=cortex-a53
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mtune=cortex-a53
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC4),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mtune=cortex-a55
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mtune=cortex-a55
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a73 -mtune=cortex-a73.cortex-a53
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a73 -mtune=cortex-a73.cortex-a53
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
DOSBOX_STAGING_CFLAGS   += -mcpu=cortex-a15 -mfpu=neon-vfpv4 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -mcpu=cortex-a15 -mfpu=neon-vfpv4 -mfpu=neon-vfpv4 -mfloat-abi=hard
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TINKERBOARD)$(BR2_PACKAGE_BATOCERA_TARGET_MIQI),y)
DSOBOX_STAGING_CFLAGS   += -marm -march=armv7-a -mtune=cortex-a17 -mfpu=neon-vfpv4 -mfloat-abi=hard
DSOBOX_STAGING_CXXFLAGS += -marm -march=armv7-a -mtune=cortex-a17 -mfpu=neon-vfpv4 -mfloat-abi=hard
endif

define DOSBOX_STAGING_CONFIGURE_CMDS
    cd $(@D); ./autogen.sh; $(TARGET_CONFIGURE_OPTS) CROSS_COMPILE="$(HOST_DIR)/usr/bin/" LIBS="-lvorbisfile -lvorbis -logg" \
        ./configure CPPFLAGS="$(DOSBOX_STAGING_CPPFLAGS)" CFLAGS="$(DOSBOX_STAGING_CFLAGS)" CXXFLAGS="$(DOSBOX_STAGING_CXXFLAGS)" --host="$(GNU_TARGET_NAME)" \
                    --enable-core-inline \
                    --enable-dynrec \
                    --enable-unaligned_memory \
                    --prefix=/usr \
                    --with-sdl-prefix="$(STAGING_DIR)/usr";
endef

define DOSBOX_STAGING_INSTALL_TARGET_CMDS
        $(INSTALL) -D $(@D)/src/dosbox $(TARGET_DIR)/usr/bin/dosbox-staging
endef

$(eval $(autotools-package))
