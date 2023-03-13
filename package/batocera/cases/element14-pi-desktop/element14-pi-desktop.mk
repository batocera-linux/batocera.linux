################################################################################
#
# element14-pi-desktop
#
################################################################################

ELEMENT14_PI_DESKTOP_VERSION = 536649e9b2ee9d706cd1c600d1320ad78fd6ac47
ELEMENT14_PI_DESKTOP_SITE = $(call github,pi-desktop,deb-make,$(ELEMENT14_PI_DESKTOP_VERSION))

define ELEMENT14_PI_DESKTOP_CONFIGURE_CMDS
	sed -i '17a \    os.system("/etc/init.d/S31emulationstation stop")' $(@D)/pidesktop-base/usr/share/PiDesktop/python/restart.py
endef

define ELEMENT14_PI_DESKTOP_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/element14
	$(INSTALL) -D -m 0755 $(@D)/pidesktop-base/usr/share/PiDesktop/python/restart.py $(TARGET_DIR)/usr/bin/element14/restart.py
endef

$(eval $(generic-package))
