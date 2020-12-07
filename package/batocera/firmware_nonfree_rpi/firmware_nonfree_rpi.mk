################################################################################
#
# firmware-nonfree_rpi
#
################################################################################
# Version from 1:20190114-1+rpt10 release
FIRMWARE_NONFREE_RPI_VERSION = b66ab26cebff689d0d3257f56912b9bb03c20567
FIRMWARE_NONFREE_RPI_SITE = https://github.com/RPi-Distro/firmware-nonfree.git
FIRMWARE_NONFREE_RPI_SITE_METHOD = git

define FIRMWARE_NONFREE_RPI_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware
	# -n is mandatory while some other packages provides firmwares too
	# this is not ideal, but i don't know how to tell to buildroot to install this package first (and not worry about all packages installing firmwares)
	cp -prn $(@D)/brcm/{brcmfmac43456-sdio.bin,brcmfmac43456-sdio.txt,brcmfmac43456-sdio.clm_blob} $(TARGET_DIR)/lib/firmware/
endef

$(eval $(generic-package))
