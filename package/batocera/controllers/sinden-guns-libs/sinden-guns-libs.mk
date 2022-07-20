################################################################################
#
# sinden-guns-libs
#
################################################################################

SINDEN_GUNS_LIBS_VERSION = 326d6710c7d4de3f3b6111ccd9bf5d402535233b
SINDEN_GUNS_LIBS_SITE = $(call github,batocera-linux,batocera-sinden-bundles,$(SINDEN_GUNS_LIBS_VERSION))

ifeq ($(BR2_x86_64),y)
  SINDEN_GUNS_LIBS_ARCH_DIR=x86_64
else ifeq ($(BR2_aarch64),y)
  SINDEN_GUNS_LIBS_ARCH_DIR=aarch64
else ifeq ($(BR2_arm),y)
  SINDEN_GUNS_LIBS_ARCH_DIR=arm
else
  SINDEN_GUNS_LIBS_ARCH_DIR=undefined
endif

define SINDEN_GUNS_LIBS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(@D)/$(SINDEN_GUNS_LIBS_ARCH_DIR)/libCameraInterface.so $(TARGET_DIR)/usr/share/sinden/libCameraInterface.so
endef

$(eval $(generic-package))
