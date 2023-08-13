################################################################################
#
# pixelcade
#
################################################################################

PIXELCADE_VERSION = 5bf13124c2a8ca0392284f791952383ebc7e4a8f
PIXELCADE_SITE = $(call github,alinke,pixelcade-linux-builds,$(PIXELCADE_VERSION))

ifeq ($(BR2_x86_64),y)
  PIXELCADE_ARCH_DIR=linux_amd64
else ifeq ($(BR2_aarch64),y)
  PIXELCADE_ARCH_DIR=linux_arm64
else ifeq ($(BR2_arm1176jzf_s),y) # rpi1
  PIXELCADE_ARCH_DIR=linux_arm_v6
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y) # rpi2
  PIXELCADE_ARCH_DIR=linux_arm_v7pi
else ifeq ($(BR2_arm),y)
  PIXELCADE_ARCH_DIR=linux_arm_v7
else
  PIXELCADE_ARCH_DIR=undefined
endif

define PIXELCADE_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/$(PIXELCADE_ARCH_DIR)/pixelweb $(TARGET_DIR)/usr/bin/pixelweb
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/pixelcade/pixelcade-tools    $(TARGET_DIR)/usr/bin/pixelcade-tools
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/pixelcade/pixelcade-add      $(TARGET_DIR)/usr/bin/pixelcade-add
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/pixelcade/99-pixelcade.rules $(TARGET_DIR)/etc/udev/rules.d/99-pixelcade.rules

	mkdir -p $(TARGET_DIR)/usr/share/pixelcade/images/system
	mkdir -p $(TARGET_DIR)/usr/share/pixelcade/scripts
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/pixelcade/batocera.png $(TARGET_DIR)/usr/share/pixelcade/images/system/batocera.png
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/screens/pixelcade/scripts/*.sh $(TARGET_DIR)/usr/share/pixelcade/scripts/
endef

$(eval $(generic-package))
