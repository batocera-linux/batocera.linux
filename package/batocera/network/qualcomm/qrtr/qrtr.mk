################################################################################
#
# qrtr
#
################################################################################

QRTR_VERSION = ef44ad10f284410e2db4c4ce22c8645f988f8402
QRTR_SITE = $(call github,andersson,qrtr,$(QRTR_VERSION))
QRTR_LICENSE = BSD-3-Clause license
QRTR_LICENSE_FILE = LICENSE
QRTR_DEPENDENCIES = linux-headers
QRTR_INSTALL_STAGING = YES
HOST_QRTR_DEPENDENCIES = linux-headers toolchain

$(eval $(meson-package))
$(eval $(host-meson-package))
