################################################################################
#
# PCSX2
#
################################################################################

# Version.: Commits on Aug 31, 2021
LIBRETRO_PCSX2_VERSION = 22678e4e0ca2f7a33c3ad6f6edf4276479997c5e
LIBRETRO_PCSX2_SITE = https://github.com/libretro/pcsx2.git
LIBRETRO_PCSX2_LICENSE = GPLv2
LIBRETRO_PCSX2_DEPENDENCIES = libaio xz

LIBRETRO_PCSX2_SITE_METHOD = git
LIBRETRO_PCSX2_GIT_SUBMODULES = YES

LIBRETRO_PCSX2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_PCSX2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LIBRETRO_PCSX2_CONF_OPTS += -DENABLE_TESTS=OFF
LIBRETRO_PCSX2_CONF_OPTS += -DENABLE_QT=OFF
LIBRETRO_PCSX2_CONF_OPTS += -DLIBRETRO=ON
LIBRETRO_PCSX2_CONF_OPTS += -DDISABLE_ADVANCE_SIMD=ON

define LIBRETRO_PCSX2_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/pcsx2/pcsx2_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx2_libretro.so
endef

$(eval $(cmake-package))
