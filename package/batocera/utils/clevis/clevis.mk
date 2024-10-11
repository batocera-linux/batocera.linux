################################################################################
#
# clevis
#
################################################################################

CLEVIS_VERSION = 21
CLEVIS_SITE = $(call github,latchset,clevis,v$(CLEVIS_VERSION))
CLEVIS_LICENSE = GPLv3
CLEVIS_LICENSE_FILES = COPYING

CLEVIS_DEPENDENCIES = cryptsetup host-cryptsetup jose luksmeta tpm2-tools

$(eval $(meson-package))
