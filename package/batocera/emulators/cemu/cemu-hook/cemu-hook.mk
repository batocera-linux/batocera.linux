################################################################################
#
# Cemu-hook
#
################################################################################

CEMU_HOOK_VERSION = 1159_0573
CEMU_HOOK_SOURCE = cemuhook_$(CEMU_HOOK_VERSION).zip
CEMU_HOOK_SITE = https://files.sshnuke.net

define CEMU_HOOK_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(CEMU_HOOK_DL_SUBDIR)/$(CEMU_HOOK_SOURCE)
endef

define CEMU_HOOK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/cemu/
	cp $(@D)/keystone.dll $(TARGET_DIR)/usr/cemu/
	cp $(@D)/dbghelp.dll  $(TARGET_DIR)/usr/cemu/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/cemu/cemu-hook/cemuhook.ini $(TARGET_DIR)/usr/cemu/
endef

$(eval $(generic-package))
