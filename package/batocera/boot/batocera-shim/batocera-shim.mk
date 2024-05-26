################################################################################
#
# batocera-shim
#
################################################################################

BATOCERA_SHIM_VERSION = 15.7
BATOCERA_SHIM_SITE = https://github.com/rhboot/shim/releases/download/$(BATOCERA_SHIM_VERSION)
BATOCERA_SHIM_SOURCE = shim-$(BATOCERA_SHIM_VERSION).tar.bz2
BATOCERA_SHIM_LICENSE = BSD-2-Clause
BATOCERA_SHIM_LICENSE_FILES = COPYRIGHT
BATOCERA_SHIM_CPE_ID_VENDOR = redhat
BATOCERA_SHIM_INSTALL_TARGET = NO
BATOCERA_SHIM_INSTALL_IMAGES = YES

BATOCERA_SHIM_MAKE_OPTS = \
	ARCH="$(GNU_EFI_PLATFORM)" \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	DASHJ="-j$(PARALLEL_JOBS)"

define BATOCERA_SHIM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) $(BATOCERA_SHIM_MAKE_OPTS)
endef

define BATOCERA_SHIM_INSTALL_IMAGES_CMDS
	$(INSTALL) -m 0755 -t $(BINARIES_DIR) $(@D)/*.efi
endef

$(eval $(generic-package))
