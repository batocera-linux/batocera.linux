################################################################################
#
# dosbox-staging
#
################################################################################

DOSBOX_STAGING_VERSION = v0.80.1
DOSBOX_STAGING_SITE = $(call github,dosbox-staging,dosbox-staging,$(DOSBOX_STAGING_VERSION))
DOSBOX_STAGING_DEPENDENCIES = alsa-lib sdl2 sdl2_net sdl2_image fluidsynth zlib libpng libogg libvorbis opus opusfile slirp iir speexdsp
DOSBOX_STAGING_LICENSE = GPLv2

DOSBOX_STAGING_CPPFLAGS = -DNDEBUG
DOSBOX_STAGING_CFLAGS   = -O3 -fstrict-aliasing -fno-signed-zeros -fno-trapping-math -fassociative-math -frename-registers -ffunction-sections -fdata-sections
DOSBOX_STAGING_CXXFLAGS = -O3 -fstrict-aliasing -fno-signed-zeros -fno-trapping-math -fassociative-math -frename-registers -ffunction-sections -fdata-sections
DOSBOX_STAGING_CONF_OPTS = -Duse_mt32emu=false

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
DOSBOX_STAGING_CFLAGS   += -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836)$(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC)$(BR2_PACKAGE_BATOCERA_TARGET_CHA)$(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
DOSBOX_STAGING_CFLAGS   += -mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_CORTEX_A53),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a53 -mtune=cortex-a53
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a53 -mtune=cortex-a53
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a72 -mtune=cortex-a72
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a72 -mtune=cortex-a72
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN3),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mtune=cortex-a55
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mtune=cortex-a55
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a73 -mtune=cortex-a73.cortex-a53
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a73 -mtune=cortex-a73.cortex-a53
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
DOSBOX_STAGING_CFLAGS   += -mcpu=cortex-a15 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -mcpu=cortex-a15 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
DOSBOX_STAGING_CFLAGS   += -marm -march=armv7-a -mtune=cortex-a17 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -marm -march=armv7-a -mtune=cortex-a17 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mtune=cortex-a55
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mtune=cortex-a55
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8.2-a+dotprod+rcpc+ssbs+sb -mtune=cortex-a76.cortex-a55
DOSBOX_STAGING_CXXFLAGS += -march=armv8.2-a+dotprod+rcpc+ssbs+sb -mtune=cortex-a76.cortex-a55
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
DOSBOX_STAGING_CFLAGS   += -marm -march=armv7-a -mtune=cortex-a9 -mfpu=neon-vfpv3 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -marm -march=armv7-a -mtune=cortex-a9 -mfpu=neon-vfpv3 -mfloat-abi=hard
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a75 -mtune=cortex-a75.cortex-a55
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a75 -mtune=cortex-a75.cortex-a55
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif

define DOSBOX_STAGING_INSTALL_TARGET_CMDS
        $(INSTALL) -D $(@D)/build/dosbox $(TARGET_DIR)/usr/bin/dosbox-staging
endef

$(eval $(meson-package))
