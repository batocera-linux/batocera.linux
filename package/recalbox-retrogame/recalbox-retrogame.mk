################################################################################
#
# Retrogame Recalbox https://github.com/ian57/Recalbox-Retrogame-2Players-Pi2
#
################################################################################
RECALBOX_RETROGAME_VERSION = master
RECALBOX_RETROGAME_SITE = $(call github,ian57,Recalbox-Retrogame-2Players-Pi2,$(RECALBOX_RETROGAME_VERSION))

define RECALBOX_RETROGAME_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) retrogame
endef

define RECALBOX_RETROGAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/retrogame \
		$(TARGET_DIR)/usr/bin/recalbox-retrogame
endef

$(eval $(generic-package))
