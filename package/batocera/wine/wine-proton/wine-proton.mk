################################################################################
#
# wine-proton
#
################################################################################

WINE_PROTON_VERSION = proton-11.0-2
WINE_PROTON_SOURCE = wine-$(WINE_PROTON_VERSION)-amd64.tar.xz
WINE_PROTON_SITE = \
    https://github.com/Kron4ek/Wine-Builds/releases/download/$(WINE_PROTON_VERSION)
WINE_PROTON_LICENSE = MIT License
WINE_PROTON_LICENSE_FILE = LICENSE
# the wine-mono version this Proton asks for, it also runs fine on the newer system one
WINE_PROTON_MONO_VERSION = 10.4.1

define WINE_PROTON_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/wine/wine-proton
	rsync -a --exclude='.*' $(@D)/ $(TARGET_DIR)/usr/wine/wine-proton/
endef

ifeq ($(BR2_PACKAGE_WINE_MONO),y)
ifneq ($(WINE_PROTON_MONO_VERSION),$(WINE_MONO_VERSION))
define WINE_PROTON_LINK_MONO
	mkdir -p $(TARGET_DIR)/usr/share/wine/mono
	ln -sfn wine-mono-$(WINE_MONO_VERSION) \
	    $(TARGET_DIR)/usr/share/wine/mono/wine-mono-$(WINE_PROTON_MONO_VERSION)
endef
WINE_PROTON_POST_INSTALL_TARGET_HOOKS += WINE_PROTON_LINK_MONO
endif
endif

$(eval $(generic-package))
