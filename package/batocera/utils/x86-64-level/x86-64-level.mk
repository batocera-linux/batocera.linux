################################################################################
#
# x86-64-level
#
################################################################################

X86_64_LEVEL_VERSION = 0.2.2
X86_64_LEVEL_SITE =  $(call github,HenrikBengtsson,x86-64-level,$(X86_64_LEVEL_VERSION))
X86_64_LEVEL_LICENSE = BY-SA

define X86_64_LEVEL_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/x86-64-level $(TARGET_DIR)/usr/bin/x86-64-level
	$(INSTALL) -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/x86-64-level/batocera-x64-compatibility $(TARGET_DIR)/usr/bin/batocera-x64-compatibility
endef

$(eval $(generic-package))
