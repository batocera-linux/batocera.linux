################################################################################
#
# pcsx2-x86
#
################################################################################

# version 5.18 means binary from 5.18 version (or the last built if the version is not yet out)
PCSX2_X86_VERSION = 5.26 #$(BATOCERA_SYSTEM_VERSION)
PCSX2_X86_SOURCE = pcsx2-x86-$(PCSX2_X86_VERSION).tar.gz
PCSX2_X86_SITE = https://github.com/batocera-linux/pcsx2-x86/releases/download/$(PCSX2_X86_VERSION)
PCSX2_X86_LICENSE = GPLv2 GPLv3 LGPLv2.1 LGPLv3

define PCSX2_X86_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(PCSX2_X86_DL_SUBDIR)/$(PCSX2_X86_SOURCE)
endef

define PCSX2_X86_INSTALL_TARGET_CMDS
	cp -pr $(@D)/target/* $(TARGET_DIR)
endef

$(eval $(generic-package))
