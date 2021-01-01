################################################################################
#
# alllinuxfirmwares
#
################################################################################
# Version from 2020-04-14 10:37 - amdgpu: update vega20 to the latest 19.50 firmware
ALLLINUXFIRMWARES_VERSION = 78c0348458c035cf1de6093555db5431cc8c1268
ALLLINUXFIRMWARES_SITE = http://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
ALLLINUXFIRMWARES_SITE_METHOD = git

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware
	# -n is mandatory while some other packages provides firmwares too
	# this is not ideal, but i don't know how to tell to buildroot to install this package first (and not worry about all packages installing firmwares)
	cp -prn $(@D)/* $(TARGET_DIR)/lib/firmware/

	# exclude some dirs not required on batocera
	rm -rf $(TARGET_DIR)/lib/firmware/liquidio
	rm -rf $(TARGET_DIR)/lib/firmware/netronome
endef

$(eval $(generic-package))
