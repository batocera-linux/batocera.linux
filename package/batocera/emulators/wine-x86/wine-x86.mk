################################################################################
#
# wine-x86
#
################################################################################

# version 5.18 means binary from 5.18 version (or the last built if the version is not yet out)
WINE_X86_VERSION = $(BATOCERA_SYSTEM_VERSION)
WINE_X86_SOURCE = wine-x86-$(WINE_X86_VERSION).tar.gz
WINE_X86_SITE = https://github.com/rtissera/wine-x86/releases/download/$(WINE_X86_VERSION)

define WINE_X86_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(WINE_X86_DL_SUBDIR)/$(WINE_X86_SOURCE)
endef

define WINE_X86_INSTALL_TARGET_CMDS
	cp -pr $(@D)/target/* $(TARGET_DIR)
endef

$(eval $(generic-package))
