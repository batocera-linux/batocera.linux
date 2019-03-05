################################################################################
#
# RetroGame Batocera
#
################################################################################
BATOCERA_RETROGAME_VERSION = 1.0
BATOCERA_RETROGAME_SOURCE=  

define BATOCERA_RETROGAME_EXTRACT_CMDS
	cp package/batocera/core/batocera-retrogame/RetroGame/* $(@D)
endef

define BATOCERA_RETROGAME_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) retrogame
endef

define BATOCERA_RETROGAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/retrogame \
		$(TARGET_DIR)/usr/bin/recalbox-retrogame
endef

$(eval $(generic-package))
