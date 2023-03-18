################################################################################
#
# Abuse-data
#
################################################################################

# This is now replaced by a Pacman package from the content downloader (saves 16MB)

ABUSE_DATA_VERSION = 2.00
ABUSE_DATA_SITE = abuse.zoy.org/raw-attachment/wiki/download
ABUSE_DATA_SOURCE = abuse-data-2.00.tar.gz
ABUSE_DATA_LICENSE = Public Domain

define ABUSE_DATA_EXTRACT_CMDS
    tar -xf $(ABUSE_DATA_DL_DIR)/$(ABUSE_DATA_SOURCE) -C $(@D)
endef

define ABUSE_DATA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/abuse/
	cp -pvr $(@D)/* $(TARGET_DIR)/usr/share/abuse
endef

$(eval $(generic-package))
