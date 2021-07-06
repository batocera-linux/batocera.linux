################################################################################
#
# alllinuxfirmwares
#
################################################################################
# Version from 2021-03-15
ALLLINUXFIRMWARES_VERSION = 20210315
ALLLINUXFIRMWARES_SITE = http://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
ALLLINUXFIRMWARES_SITE_METHOD = git

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware

	# -n is mandatory while some other packages provides firmwares too
	# this is not ideal, but i don't know how to tell to buildroot to install this package first (and not worry about all packages installing firmwares)
	cp -prn $(@D)/* $(TARGET_DIR)/lib/firmware/
endef

# because it adds so non required files on the rpi ; we prefer the specific rpi firmware packages
define ALLLINUXFIRMWARES_DELETE_BRCM
	rm -rf $(@D)/brcm
endef

# remove x86 world only firmware
define ALLLINUXFIRMWARES_DELETE_X86_ONLY_FIRMWARE
	rm -rf $(@D)/amdgpu
	rm -rf $(@D)/i915
	rm -rf $(@D)/intel
	rm -rf $(@D)/iwlwifi*
	rm -rf $(@D)/radeon
endef

# remove obscure firmware
define ALLLINUXFIRMWARES_DELETE_OBSCURE_FIRMWARE
	rm -rf $(@D)/dpaa2
	rm -rf $(@D)/liquidio
	rm -rf $(@D)/mellanox
	rm -rf $(@D)/netronome
	rm -rf $(@D)/qcom
	rm -rf $(@D)/qed
endef

ifeq ($(BR2_PACKAGE_BATOCERA_RPI_ANY),y)
ALLLINUXFIRMWARES_PRE_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_DELETE_BRCM
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
else
ALLLINUXFIRMWARES_PRE_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_DELETE_X86_ONLY_FIRMWARE
endif

ALLLINUXFIRMWARES_PRE_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_DELETE_OBSCURE_FIRMWARE

$(eval $(generic-package))
