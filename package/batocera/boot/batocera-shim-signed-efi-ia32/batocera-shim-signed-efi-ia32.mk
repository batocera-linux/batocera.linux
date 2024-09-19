################################################################################
#
# batocera-shim-signed-efi-ia32
#
################################################################################

BATOCERA_SHIM_SIGNED_EFI_IA32_VERSION = 1.44~1+deb12u1+15.8-1~deb12u1
BATOCERA_SHIM_SIGNED_EFI_IA32_SITE = https://ftp.debian.org/debian/pool/main/s/shim-signed
BATOCERA_SHIM_SIGNED_EFI_IA32_SOURCE = shim-signed_$(BATOCERA_SHIM_SIGNED_EFI_IA32_VERSION)_i386.deb

define BATOCERA_SHIM_SIGNED_EFI_IA32_EXTRACT_CMDS
	mkdir -p $(@D)/shim-signed
	dpkg-deb -R $(BATOCERA_SHIM_SIGNED_EFI_IA32_DL_DIR)/$(BATOCERA_SHIM_SIGNED_EFI_IA32_SOURCE) $(@D)/shim-signed
endef

define BATOCERA_SHIM_SIGNED_EFI_IA32_BUILD_CMDS
endef

define BATOCERA_SHIM_SIGNED_EFI_IA32_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/shim-signed

	cp $(@D)/shim-signed/usr/lib/shim/shimia32.efi.signed $(BINARIES_DIR)/shim-signed/shimia32.efi
endef

$(eval $(generic-package))
