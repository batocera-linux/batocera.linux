################################################################################
#
# Batocera notice
#
################################################################################
BATOCERA_NOTICE_VERSION = 456fbde1ef4462ea72f23eb8836fcfa9514c6ca9
BATOCERA_NOTICE_SITE = $(call github,batocera-linux,batocera-notice,$(BATOCERA_NOTICE_VERSION))

define BATOCERA_NOTICE_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/doc
    cp -r $(@D)/notice.pdf $(TARGET_DIR)/usr/share/batocera/doc/notice.pdf
endef

$(eval $(generic-package))
