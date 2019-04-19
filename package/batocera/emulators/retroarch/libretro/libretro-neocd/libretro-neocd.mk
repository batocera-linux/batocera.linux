################################################################################
#
# NEOCD
#
################################################################################
# Version.: Commits on Apr 5, 2019
LIBRETRO_NEOCD_VERSION = fd77de0d3f557f9d92a78c7bdda44c207f992ab5
LIBRETRO_NEOCD_SITE = $(call github,libretro,neocd_libretro,$(LIBRETRO_NEOCD_VERSION))
LIBRETRO_NEOCD_LICENSE="GPLv3"

define LIBRETRO_NEOCD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/cmake-build-Release/output/libneocd_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/neocd_libretro.so
endef

$(eval $(cmake-package))
