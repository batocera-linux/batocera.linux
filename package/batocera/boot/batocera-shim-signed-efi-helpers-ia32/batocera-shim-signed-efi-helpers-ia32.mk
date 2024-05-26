################################################################################
#
# batocera-shim-signed-ef-helpers-ia32
#
################################################################################

BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_VERSION = 1+15.7+1
BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_SITE = https://ftp.debian.org/debian/pool/main/s/shim-helpers-i386-signed
BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_SOURCE = shim-helpers-i386-signed_$(BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_VERSION)_i386.deb

define BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_EXTRACT_CMDS
	mkdir -p $(@D)/shim-signed
	dpkg-deb -R $(BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_DL_DIR)/$(BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_SOURCE) $(@D)/shim-signed
endef

define BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_BUILD_CMDS
endef

define BATOCERA_SHIM_SIGNED_EFI_HELPERS_IA32_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/shim-signed

	cp $(@D)/shim-signed/usr/lib/shim/fbia32.efi.signed $(BINARIES_DIR)/shim-signed/fbia32.efi
	cp $(@D)/shim-signed/usr/lib/shim/mmia32.efi.signed $(BINARIES_DIR)/shim-signed/mmia32.efi
endef

$(eval $(generic-package))
