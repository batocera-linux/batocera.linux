################################################################################
#
# qrtr
#
################################################################################

QRTR_VERSION = v1.2
QRTR_SITE = $(call github,linux-msm,qrtr,$(QRTR_VERSION))
QRTR_LICENSE = BSD-3-Clause license
QRTR_LICENSE_FILE = LICENSE
QRTR_DEPENDENCIES = linux-headers
QRTR_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_SYSTEMD),y)
QRTR_CONF_OPTS += -Dsystemd-service=enabled
QRTR_DEPENDENCIES += systemd
else
QRTR_CONF_OPTS += -Dsystemd-service=disabled
endif

$(eval $(meson-package))
