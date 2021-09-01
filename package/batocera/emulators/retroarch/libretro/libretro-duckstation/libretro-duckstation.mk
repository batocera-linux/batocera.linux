################################################################################
#
# LIBRETRO_DUCKSTATION
#
################################################################################
# libretro cores can be downloaded in binary form,
# but not built from the Github Duckstation sources
LIBRETRO_DUCKSTATION_VERSION = ffbaff6aefad340760a146d194f686d0e9317883
LIBRETRO_DUCKSTATION_SITE = $(call github,batocera-linux,lr-duckstation,$(LIBRETRO_DUCKSTATION_VERSION))
LIBRETRO_DUCKSTATION_LICENSE = non-commercial

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
LIBRETRO_DUCKSTATION_PK = duckstation_libretro_linux_x64.zip
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326_ANY),y)
LIBRETRO_DUCKSTATION_PK = duckstation_libretro_linux_aarch64.zip
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_DUCKSTATION_PK = duckstation_libretro_linux_aarch64.zip
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_DUCKSTATION_PK = duckstation_libretro_linux_aarch64.zip
endif

define LIBRETRO_DUCKSTATION_INSTALL_TARGET_CMDS
        cd $(@D) && unzip $(LIBRETRO_DUCKSTATION_PK)
        mkdir -p $(TARGET_DIR)/usr/lib/libretro/
        cp -prn $(@D)/duckstation_libretro.so $(TARGET_DIR)/usr/lib/libretro
endef

$(eval $(generic-package))
