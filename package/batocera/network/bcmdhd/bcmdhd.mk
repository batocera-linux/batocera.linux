################################################################################
#
# bcmdhd
#
################################################################################
# Version: 101.10.591.52.27-11, Commits on Nov 18, 2026
BCMDHD_VERSION = 3b12c096d0fc2e6363920e80ec6ba71618e7cd29
BCMDHD_SITE = $(call github,armbian,bcmdhd-dkms,$(BCMDHD_VERSION))
BCMDHD_LICENSE = GPL-2.0

BCMDHD_MODULE_SUBDIRS = src
BCMDHD_MODULE_MAKE_OPTS = \
	CONFIG_BCMDHD_SDIO=y \
	CONFIG_BCMDHD_PCIE= \
	CONFIG_BCMDHD_USB=

$(eval $(kernel-module))
$(eval $(generic-package))
