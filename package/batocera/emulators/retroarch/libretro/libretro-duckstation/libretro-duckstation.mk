################################################################################
#
# LIBRETRO_DUCKSTATION
#
################################################################################
# libretro cores can be downloaded in binary form,
# but not built from the Github Duckstation sources
# Version.: 0.1-4866-gf799f62a
LIBRETRO_DUCKSTATION_VERSION = 5c0d746e4ccb725fc03e53dc530b90bc570253d7
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

    $(INSTALL) -D $(@D)/duckstation_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/duckstation_libretro.so
endef

$(eval $(generic-package))
