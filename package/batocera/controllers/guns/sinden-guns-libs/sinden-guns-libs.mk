################################################################################
#
# sinden-guns-libs
#
################################################################################

SINDEN_GUNS_LIBS_VERSION = a18005ab0ce07d0d18f8575ba21162c58fbd2520
SINDEN_GUNS_LIBS_SITE = $(call github,batocera-linux,batocera-sinden-bundles,$(SINDEN_GUNS_LIBS_VERSION))

ifeq ($(BR2_x86_64),y)
  SINDEN_GUNS_LIBS_ARCH_DIR=x86_64
else ifeq ($(BR2_aarch64),y)
  SINDEN_GUNS_LIBS_ARCH_DIR=aarch64
else ifeq ($(BR2_arm),y)
  SINDEN_GUNS_LIBS_ARCH_DIR=arm
else ifeq ($(BR2_riscv),y)
  SINDEN_GUNS_LIBS_ARCH_DIR=riscv
else
  SINDEN_GUNS_LIBS_ARCH_DIR=undefined
endif

define SINDEN_GUNS_LIBS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(@D)/$(SINDEN_GUNS_LIBS_ARCH_DIR)/libCameraInterface.so $(TARGET_DIR)/usr/share/sinden/libCameraInterface.so
endef

$(eval $(generic-package))
