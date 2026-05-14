################################################################################
#
# Batocera notice
#
################################################################################
BATOCERA_NOTICE_VERSION = d8877e6282868d30e1c2d70c28ec1d1e2491d5b7
BATOCERA_NOTICE_SITE = $(call github,batocera-linux,batocera-notice,$(BATOCERA_NOTICE_VERSION))

define BATOCERA_NOTICE_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/doc
    cp -r $(@D)/notice.pdf $(TARGET_DIR)/usr/share/batocera/doc/notice.pdf
endef

$(eval $(generic-package))
