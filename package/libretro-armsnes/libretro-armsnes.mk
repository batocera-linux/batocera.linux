################################################################################
#
# ARMSNES
#
################################################################################
ARMSNES_VERSION = 0.2
ARMSNES_SITE = https://github.com/rmaz/ARMSNES-libretro/archive
ARMSNES_SOURCE = 0.2.tar.gz
ARMSNES_TARGET = libarmsnes.so

define ARMSNES_BUILD_CMDS
	$(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" \
		CFLAGS="$(TARGET_CFLAGS)" LD="$(TARGET_LD)" \
		TARGET="$(ARMSNES_TARGET)" -C $(@D) all
endef

define ARMSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(ARMSNES_TARGET) \
		$(TARGET_DIR)/usr/lib/libretro/$(ARMSNES_TARGET)
endef

$(eval $(generic-package))
