################################################################################
#
# wine-proton
#
################################################################################

WINE_PROTON_VERSION = proton-10.0-3
WINE_PROTON_SOURCE = wine-$(WINE_PROTON_VERSION)-amd64.tar.xz
WINE_PROTON_SITE = \
    https://github.com/Kron4ek/Wine-Builds/releases/download/$(WINE_PROTON_VERSION)
WINE_PROTON_LICENSE = MIT License
WINE_PROTON_LICENSE_FILE = LICENSE

define WINE_PROTON_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/wine/wine-proton
	rsync -a --exclude='.*' $(@D)/ $(TARGET_DIR)/usr/wine/wine-proton/
endef

$(eval $(generic-package))
