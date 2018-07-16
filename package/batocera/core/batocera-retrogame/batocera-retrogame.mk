################################################################################
#
# Retrogame Batocera https://github.com/batocera-linux/Recalbox-Retrogame-2Players-Pi2
#
################################################################################
BATOCERA_RETROGAME_VERSION = 8d3e90ed179146d717201b6f4337290100f9ca26
BATOCERA_RETROGAME_SITE = $(call github,batocera-linux,Recalbox-Retrogame-2Players-Pi2,$(BATOCERA_RETROGAME_VERSION))

define BATOCERA_RETROGAME_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) retrogame
endef

define BATOCERA_RETROGAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/retrogame \
		$(TARGET_DIR)/usr/bin/recalbox-retrogame
endef

$(eval $(generic-package))
