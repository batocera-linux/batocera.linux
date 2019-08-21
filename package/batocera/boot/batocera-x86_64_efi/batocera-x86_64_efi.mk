################################################################################
#
# batocera-x86_64_efi
#
################################################################################

BATOCERA_X86_64_EFI_VERSION = 1.1
BATOCERA_X86_64_EFI_SOURCE = bootx64.efi.gz
BATOCERA_X86_64_EFI_SITE = https://github.com/batocera-linux/batocera-x86_64_efi/releases/download/$(BATOCERA_X86_64_EFI_VERSION)

define BATOCERA_X86_64_EFI_EXTRACT_CMDS
	cp $(DL_DIR)/$(BATOCERA_X86_64_EFI_DL_SUBDIR)/$(BATOCERA_X86_64_EFI_SOURCE) $(@D)
	gunzip $(@D)/$(BATOCERA_X86_64_EFI_SOURCE)
endef

define BATOCERA_X86_64_EFI_INSTALL_TARGET_CMDS
	cp $(@D)/bootx64.efi $(BINARIES_DIR)
endef

$(eval $(generic-package))
