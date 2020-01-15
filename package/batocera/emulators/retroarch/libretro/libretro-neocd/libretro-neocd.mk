
################################################################################
#
# NEOCD
#
################################################################################
# Version.: Commits on Dec 18, 2019
LIBRETRO_NEOCD_VERSION = 7346ab58a0c0e96f35b39086b03439c10343b81c
LIBRETRO_NEOCD_SITE = https://github.com/libretro/neocd_libretro.git
LIBRETRO_NEOCD_SITE_METHOD=git
LIBRETRO_NEOCD_GIT_SUBMODULES=YES
LIBRETRO_NEOCD_LICENSE = GPLv3

define LIBRETRO_NEOCD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libneocd_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/neocd_libretro.so
endef

define LIBRETRO_NEOCD_DISABLE_ARM_FLAGS
	$(SED) 's|^set(CMAKE_CXX_FLAGS_RELEASE|#set(CMAKE_CXX_FLAGS_RELEASE|g' $(@D)/CMakeLists.txt
endef

ifeq ($(BR2_arm),y)
else
  LIBRETRO_NEOCD_PRE_CONFIGURE_HOOKS += LIBRETRO_NEOCD_DISABLE_ARM_FLAGS
endif

$(eval $(cmake-package))
