################################################################################
#
# wine-mono
#
################################################################################

WINE_MONO_VERSION = 10.3.0
WINE_MONO_SOURCE = wine-mono-$(WINE_MONO_VERSION)-x86.tar.xz
WINE_MONO_SITE = https://github.com/wine-mono/wine-mono/releases/download/wine-mono-$(WINE_MONO_VERSION)

define WINE_MONO_INSTALL_TARGET_CMDS
    mkdir -p \
	    $(TARGET_DIR)/usr/wine/wine-tkg/share/wine/mono/wine-mono-$(WINE_MONO_VERSION)
	mkdir -p \
	    $(TARGET_DIR)/usr/wine/wine-proton/share/wine/mono/wine-mono-$(WINE_MONO_VERSION)
	rsync -a --exclude='.*' $(@D)/ \
	    $(TARGET_DIR)/usr/wine/wine-tkg/share/wine/mono/wine-mono-$(WINE_MONO_VERSION)
	rsync -a --exclude='.*' $(@D)/ \
	    $(TARGET_DIR)/usr/wine/wine-proton/share/wine/mono/wine-mono-$(WINE_MONO_VERSION)
endef

$(eval $(generic-package))
