################################################################################
#
# recalbox-x86_64_efi
#
################################################################################

RECALBOX_X86_64_EFI_VERSION = 1.0
RECALBOX_X86_64_EFI_SOURCE = bootx64.efi.gz
RECALBOX_X86_64_EFI_SITE = https://github.com/recalbox/recalbox-x86_64_efi/releases/download/$(RECALBOX_X86_64_EFI_VERSION)

define RECALBOX_X86_64_EFI_EXTRACT_CMDS
	cp $(DL_DIR)/$(RECALBOX_X86_64_EFI_SOURCE) $(@D)
	gunzip $(@D)/$(RECALBOX_X86_64_EFI_SOURCE)
endef

define RECALBOX_X86_64_EFI_INSTALL_TARGET_CMDS
	cp $(@D)/bootx64.efi $(BINARIES_DIR)
endef

$(eval $(generic-package))
