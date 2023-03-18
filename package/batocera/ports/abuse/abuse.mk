################################################################################
#
# Abuse
#
################################################################################
# Version.: Commits on Oct 27, 2022
ABUSE_VERSION = v0.9.1
ABUSE_SITE = $(call github,Xenoveritas,abuse,$(ABUSE_VERSION))

ABUSE_DEPENDENCIES = sdl2 sdl2_mixer
ABUSE_SUPPORTS_IN_SOURCE_BUILD = NO
ABUSE_CONF_OPTS += -DASSETDIR=/userdata/roms/abuse

# Data files and evmapy keys are moved to a Pacman package (saves 16MB)
define ABUSE_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/abuse
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/src/abuse $(TARGET_DIR)/usr/bin/abuse
endef

$(eval $(cmake-package))
