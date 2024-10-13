################################################################################
#
# batocera-shim-signed-efi-x64
#
################################################################################

BATOCERA_SHIM_SIGNED_EFI_X64_VERSION = 1.58+15.8-0ubuntu1
BATOCERA_SHIM_SIGNED_EFI_X64_SITE = https://launchpad.net/ubuntu/+archive/primary/+files
BATOCERA_SHIM_SIGNED_EFI_X64_SOURCE = shim-signed_$(BATOCERA_SHIM_SIGNED_EFI_X64_VERSION)_amd64.deb

define BATOCERA_SHIM_SIGNED_EFI_X64_EXTRACT_CMDS
	mkdir -p $(@D)/shim-signed
	dpkg-deb -R $(BATOCERA_SHIM_SIGNED_EFI_X64_DL_DIR)/$(BATOCERA_SHIM_SIGNED_EFI_X64_SOURCE) $(@D)/shim-signed
endef

define BATOCERA_SHIM_SIGNED_EFI_X64_BUILD_CMDS
endef

define BATOCERA_SHIM_SIGNED_EFI_X64_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/shim-signed

	cp $(@D)/shim-signed/usr/lib/shim/fbx64.efi                 $(BINARIES_DIR)/shim-signed/
	cp $(@D)/shim-signed/usr/lib/shim/shimx64.efi.signed.latest $(BINARIES_DIR)/shim-signed/shimx64.efi
	cp $(@D)/shim-signed/usr/lib/shim/mmx64.efi                 $(BINARIES_DIR)/shim-signed/
endef

$(eval $(generic-package))
