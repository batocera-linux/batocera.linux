################################################################################
#
# REICAST
#
################################################################################

REICAST_VERSION = 0a1689cb40753d7c4ec572304f9de57ae76897d8
REICAST_SITE = $(call github,reicast,reicast-emulator,$(REICAST_VERSION))
REICAST_DEPENDENCIES = sdl2 libpng

define REICAST_UPDATE_INCLUDES
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/shell/linux/Makefile
	sed -i "s+sdl2-config+$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/shell/linux/Makefile
endef
REICAST_PRE_CONFIGURE_HOOKS += REICAST_UPDATE_INCLUDES

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
	RECALBOX_SYSTEM=rpi3
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
	RECALBOX_SYSTEM=rpi2
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_XU4),y)
	RECALBOX_SYSTEM=odroidxu4
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_X86),y)
	RECALBOX_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_X86_64),y)
	RECALBOX_SYSTEM=x64
endif

# Sadly the NEON optimizations in the PNG library don't work yet, so disable them
define REICAST_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CPP="$(TARGET_CPP)" \
		CXX="$(TARGET_CXX) -D_GLIBCXX_USE_CXX11_ABI=0" \
		CC="$(TARGET_CC) -DPNG_ARM_NEON_OPT=0" \
		AS="$(TARGET_CC)" \
		STRIP="$(TARGET_STRIP)" \
		-C $(@D)/shell/linux -f Makefile platform=$(RECALBOX_SYSTEM)
endef

define REICAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/shell/linux/reicast.elf $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))

