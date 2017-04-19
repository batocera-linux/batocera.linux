################################################################################
#
# raspi2png 
#
################################################################################
RASPI2PNG_VERSION = caa4068e9879f09afa045ee89f219bf6f8a3560d
RASPI2PNG_SITE = $(call github,AndrewFromMelbourne,raspi2png,$(RASPI2PNG_VERSION))
RASPI2PNG_LDFLAGS = -L$(STAGING_DIR)/usr/lib -lbcm_host -lpng -lm -lvchostif
RASPI2PNG_INCLUDES = -I$(STAGING_DIR)/usr/include/ -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux

define RASPI2PNG_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LDFLAGS="$(RASPI2PNG_LDFLAGS)" INCLUDES="$(RASPI2PNG_INCLUDES)" -C $(@D)
endef

define RASPI2PNG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/raspi2png \
		$(TARGET_DIR)/usr/bin/raspi2png
endef

$(eval $(generic-package))
