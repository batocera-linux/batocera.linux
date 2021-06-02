################################################################################
#
# Batocera notice
#
################################################################################
BATOCERA_NOTICE_VERSION = e6241340d292dee20406a0567262a78ff34d45f7
BATOCERA_NOTICE_SITE = $(call github,batocera-linux,batocera-notice,$(BATOCERA_NOTICE_VERSION))

define BATOCERA_NOTICE_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/doc
    cp -r $(@D)/notice.pdf $(TARGET_DIR)/usr/share/batocera/doc/notice.pdf
endef

$(eval $(generic-package))
