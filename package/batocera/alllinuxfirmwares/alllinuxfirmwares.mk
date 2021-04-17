################################################################################
#
# alllinuxfirmwares
#
################################################################################
# Version from 2020-12-18
ALLLINUXFIRMWARES_VERSION = 20210208
ALLLINUXFIRMWARES_SITE = http://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
ALLLINUXFIRMWARES_SITE_METHOD = git

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware

	# exclude some dirs not required on batocera
	rm -rf $(@D)/liquidio
	rm -rf $(@D)/netronome

	# -n is mandatory while some other packages provides firmwares too
	# this is not ideal, but i don't know how to tell to buildroot to install this package first (and not worry about all packages installing firmwares)
	cp -prn $(@D)/* $(TARGET_DIR)/lib/firmware/
endef

# because it adds so non required files on the rpi ; we prefer the specific rpi firmware packages
define ALLLINUXFIRMWARES_DELETE_BRCM
	rm -rf $(@D)/brcm
endef

ifeq ($(BR2_PACKAGE_BATOCERA_RPI_ANY),y)
ALLLINUXFIRMWARES_PRE_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_DELETE_BRCM
endif

$(eval $(generic-package))
