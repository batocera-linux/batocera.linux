################################################################################
#
# WINBTRFS - driver to mount btrfs on windows
#
################################################################################

WINBTRFS_VERSION = 1.9
WINBTRFS_SOURCE = btrfs-$(WINBTRFS_VERSION).zip
WINBTRFS_SITE = https://github.com/maharmstone/btrfs/releases/download/v$(WINBTRFS_VERSION)

define WINBTRFS_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(WINBTRFS_DL_SUBDIR)/$(WINBTRFS_SOURCE) -d $(@D)
endef

define WINBTRFS_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/tools/btrfs_on_windows
	cp $(@D)/btrfs.cat $(BINARIES_DIR)/tools/btrfs_on_windows
	cp $(@D)/btrfs.inf $(BINARIES_DIR)/tools/btrfs_on_windows
	cp -pr $(@D)/x86 $(BINARIES_DIR)/tools/btrfs_on_windows/
	cp -pr $(@D)/amd64 $(BINARIES_DIR)/tools/btrfs_on_windows/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/winbtrfs/readme.txt $(BINARIES_DIR)/tools/btrfs_on_windows/
endef

$(eval $(generic-package))
