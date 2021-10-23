################################################################################
#
# Abuse
#
################################################################################
# Version.: Commits on Aug 18, 2021
ABUSE_VERSION = eb33c63145587454d9d6ce9e5d0d535208bc15e5
ABUSE_SITE = $(call github,Xenoveritas,abuse,$(ABUSE_VERSION))

ABUSE_DEPENDENCIES = sdl2 sdl2_mixer abuse-data
ABUSE_SUPPORTS_IN_SOURCE_BUILD = NO
ABUSE_CONF_OPTS += -DASSETDIR=/usr/share/abuse

define ABUSE_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/abuse
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/src/abuse $(TARGET_DIR)/usr/bin/abuse
	cp -pvr $(@D)/data/* $(TARGET_DIR)/usr/share/abuse
	rm $(TARGET_DIR)/usr/share/abuse/CMakeLists.txt
	rm $(TARGET_DIR)/usr/share/abuse/READMD.md
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/abuse/abuse.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
