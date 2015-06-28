################################################################################
#
# GAMBATTE
#
################################################################################
ADAFRUIT_RETROGAME_VERSION = 4d59757aa820dcf8ff90dd155ed8119bbb082b89
ADAFRUIT_RETROGAME_SITE = $(call github,adafruit,Adafruit-Retrogame,$(ADAFRUIT_RETROGAME_VERSION))

define ADAFRUIT_RETROGAME_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) retrogame
endef

define ADAFRUIT_RETROGAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/retrogame \
		$(TARGET_DIR)/usr/bin/adafruit-retrogame
endef

$(eval $(generic-package))
