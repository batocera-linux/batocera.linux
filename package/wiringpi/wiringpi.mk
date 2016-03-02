################################################################################
#
# wiringpi
#
################################################################################

WIRINGPI_VERSION = 9a8f8bee5df60061645918231110a7c2e4d3fa6b # VERSION = 2.32
WIRINGPI_SITE = $(call github,WiringPi,WiringPi,$(WIRINGPI_VERSION))
WIRINGPI_LICENSE = GPLv3+
WIRINGPI_LICENSE_FILES = COPYING

define WIRINGPI_BUILD_CMDS

	$(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/wiringPi all
	$(MAKE) CC=$(TARGET_CC) LD=$(TARGET_LD) -C $(@D)/wiringPi static
	$(MAKE) LDFLAGS="-L$(@D)/wiringPi" INCLUDE="-I$(@D)/wiringPi" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/devLib all
	$(MAKE) CC=$(TARGET_CC) LD=$(TARGET_LD) -C $(@D)/devLib static   
	$(MAKE) LDFLAGS="-L$(@D)/devLib -L$(@D)/wiringPi" INCLUDE="-I$(@D)/devLib -I$(@D)/wiringPi" CC="$(TARGET_CC)" LD="$(TARGET_LD)"  -C $(@D)/gpio all
endef

define WIRINGPI_INSTALL_TARGET_CMDS
	
	 # Install wiringPi lib
     	 $(INSTALL) -D -m 0755 $(@D)/wiringPi/libwiringPi.so.2.32 $(TARGET_DIR)/usr/lib
	 cd $(TARGET_DIR)/usr/lib; ln -sf libwiringPi.so.2.32 libwiringPi.so
	 
	 # Install device lib
	 $(INSTALL) -D -m 0755 $(@D)/devLib/libwiringPiDev.so.2.32 $(TARGET_DIR)/usr/lib
	 cd $(TARGET_DIR)/usr/lib; ln -sf libwiringPiDev.so.2.32 libwiringPiDev.so
	 
	 # Install gpio bin
	 $(INSTALL) -D -m 0755 $(@D)/gpio/gpio  $(TARGET_DIR)/bin
	 
endef

$(eval $(generic-package))
