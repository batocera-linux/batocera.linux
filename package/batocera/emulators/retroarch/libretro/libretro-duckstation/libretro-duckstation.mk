################################################################################
#
# LIBRETRO_DUCKSTATION
#
################################################################################
# libretro cores can be downloaded in binary form,
# but not built from the Github Duckstation sources
LIBRETRO_DUCKSTATION_VERSION = c26eca7d0d9e6559f3a6a7af94dfa2a850223a19
LIBRETRO_DUCKSTATION_SITE = $(call github,batocera-linux,lr-duckstation,$(LIBRETRO_DUCKSTATION_VERSION))
LIBRETRO_DUCKSTATION_LICENSE = non-commercial

LIBRETRO_DUCKSTATION_PK = unknown
ifeq ($(BR2_x86_64),y)
LIBRETRO_DUCKSTATION_PK = duckstation_libretro_linux_x64.zip
else ifeq ($(BR2_aarch64),y)
LIBRETRO_DUCKSTATION_PK = duckstation_libretro_linux_aarch64.zip
else ifeq ($(BR2_arm),y)
LIBRETRO_DUCKSTATION_PK = duckstation_libretro_linux_armv7.zip
endif

define LIBRETRO_DUCKSTATION_INSTALL_TARGET_CMDS
        cd $(@D) && unzip $(LIBRETRO_DUCKSTATION_PK)
        mkdir -p $(TARGET_DIR)/usr/lib/libretro/
        cp -prn $(@D)/duckstation_libretro.so $(TARGET_DIR)/usr/lib/libretro
endef

$(eval $(generic-package))
