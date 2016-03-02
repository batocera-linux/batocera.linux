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
	 
     $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/devLib all
	 
     $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)"  -C $(@D)/gpio all
endef

define WIRINGPI_INSTALL_STAGING_CMDS
     $(INSTALL) -D -m 0644  $(@D)/wiringPi/*.h $(STAGING_DIR)/usr/include
     $(INSTALL) -D -m 0644  $(@D)/devLib/*.h $(STAGING_DIR)/usr/include
    # $(INSTALL) -D -m 0755 $(@D)/libfoo.a $(STAGING_DIR)/usr/lib/libfoo.a
    # $(INSTALL) -D -m 0644 $(@D)/foo.h $(STAGING_DIR)/usr/include/foo.h
    # $(INSTALL) -D -m 0755 $(@D)/libfoo.so* $(STAGING_DIR)/usr/lib
endef


define WIRINGPI_INSTALL_TARGET_CMDS
	
     cd $(@D)
	 VERSION=$(shell cat ./VERSION)
	 
	 # Install wiringPi lib
	 #$(INSTALL) -D -m 0644  $(@D)/wiringPi/*.h $(TARGET_DIR)/usr/include
     	 $(INSTALL) -D -m 0755 $(@D)/wiringPi/libwiringPi.so.$(VERSION) $(TARGET_DIR)/usr/lib
	 ln -sf $(TARGET_DIR)/usr/lib/libwiringPi.so.$(VERSION) $(TARGET_DIR)/lib/libwiringPi.so
	 
	 # Install device lib
	 #$(INSTALL) -D -m 0644  $(@D)/devLib/*.h $(TARGET_DIR)/usr/include
         $(INSTALL) -D -m 0755 $(@D)/devLib/libwiringPiDev.so.$(VERSION) $(TARGET_DIR)/usr/lib
	 ln -sf $(TARGET_DIR)/usr/lib/libwiringPiDev.so.$(VERSION) $(TARGET_DIR)/lib/libwiringPiDev.so
	 
	 
	 # Install gpio bin
	 cp $(@D)/gpio/gpio  $(TARGET_DIR)/bin
	 chown root.root	$(TARGET_DIR)/bin/gpio
	 chmod 4755		$(TARGET_DIR)/bin/gpio
	 mkdir -p		$(TARGET_DIR)/man/man1
	 cp $(@D)/gpio/gpio.1		$(TARGET_DIR)/man/man1
	 
endef


$(eval $(generic-package))
