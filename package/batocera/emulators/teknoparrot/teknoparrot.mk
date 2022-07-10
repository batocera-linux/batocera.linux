################################################################################
#
# teknoparrot
#
################################################################################

TEKNOPARROT_VERSION = 1.0.0.794
TEKNOPARROT_SITE = https://github.com/batocera-linux/teknoparrot/raw/main
TEKNOPARROT_SOURCE = teknoparrot_$(TEKNOPARROT_VERSION).tar.xz
TEKNOPARROT_LICENSE = GPLv3

define TEKNOPARROT_EXTRACT_CMDS
	tar -xf $(TEKNOPARROT_DL_DIR)/$(TEKNOPARROT_SOURCE) -C $(@D)
endef

define TEKNOPARROT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/teknoparrot
	cp -pr $(@D)/* $(TARGET_DIR)/usr/teknoparrot/
endef

$(eval $(generic-package))
