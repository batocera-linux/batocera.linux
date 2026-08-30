################################################################################
#
# libretro-vba-m
#
################################################################################
# Version: Commits on Aug 28, 2026
LIBRETRO_VBA_M_VERSION = 2acf41f88cca73174de3f4cda1e834c08a48a804
LIBRETRO_VBA_M_SITE = $(call github,visualboyadvance-m,visualboyadvance-m,$(LIBRETRO_VBA_M_VERSION))
LIBRETRO_VBA_M_DEPENDENCIES += retroarch zlib host-zip
LIBRETRO_VBA_M_EMULATOR_INFO = vba-m.libretro.core.yml

LIBRETRO_VBA_M_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_VBA_M_CONF_OPTS += -DENABLE_LIBRETRO=ON
LIBRETRO_VBA_M_CONF_OPTS += -DENABLE_WX=OFF
LIBRETRO_VBA_M_CONF_OPTS += -DENABLE_SDL=OFF
LIBRETRO_VBA_M_CONF_OPTS += -DENABLE_LINK=OFF
LIBRETRO_VBA_M_CONF_OPTS += -DCOMMITHASH=$(shell echo $(LIBRETRO_VBA_M_VERSION) | cut -c 1-7)

define LIBRETRO_VBA_M_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vbam_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vba-m_libretro.so
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
