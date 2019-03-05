################################################################################
#
# RetroGame
#
################################################################################
RETROGAME_VERSION = 1.0
RETROGAME_SOURCE=

define RETROGAME_EXTRACT_CMDS
	cp package/batocera/controllers/retrogame/RetroGame/* $(@D)
endef

define RETROGAME_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) retrogame
endef

define RETROGAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/retrogame \
		$(TARGET_DIR)/usr/bin/recalbox-retrogame
endef

$(eval $(generic-package))
