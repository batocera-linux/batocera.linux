################################################################################
#
# broadcom-bt-firmware
#
################################################################################

BROADCOM_BT_FIRMWARE_VERSION = v12.0.1.1105_p4
BROADCOM_BT_FIRMWARE_SITE = https://github.com/winterheart/broadcom-bt-firmware.git
BROADCOM_BT_FIRMWARE_SITE_METHOD=git
BROADCOM_BT_FIRMWARE_LICENSE = MIT, Broadcom
BROADCOM_BT_FIRMWARE_LICENSE_FILE = LICENSE.MIT.txt, LICENSE.broadcom_bcm20702
BROADCOM_BT_FIRMWARE_DEPENDENCIES += alllinuxfirmwares

$(eval $(cmake-package))
