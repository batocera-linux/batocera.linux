################################################################################
#
# uboot files for miqi
#
################################################################################
UBOOT_MIQI_VERSION = 2019.01
UBOOT_MIQI_SOURCE = $(UBOOT_MIQI_VERSION).tar.gz
UBOOT_MIQI_SITE = https://github.com/batocera-linux/uboot-miqi/archive/refs/tags

define UBOOT_MIQI_INSTALL_TARGET_CMDS
	mkdir -p   $(BINARIES_DIR)/miqi/
	cp $(@D)/* $(BINARIES_DIR)/miqi/
endef

$(eval $(generic-package))
