################################################################################
#
# wine-mono
#
################################################################################

WINE_MONO_VERSION = 9.3.0
WINE_MONO_SOURCE = wine-mono-$(WINE_MONO_VERSION)-x86.tar.xz
WINE_MONO_SITE = https://dl.winehq.org/wine/wine-mono/$(WINE_MONO_VERSION)

define WINE_MONO_EXTRACT_CMDS
	mkdir -p $(@D)/target/usr/wine/wine-tkg/share/wine/mono/
	cd $(@D)/target/usr/wine/wine-tkg/share/wine/mono/ && \
	    tar xf $(DL_DIR)/$(WINE_MONO_DL_SUBDIR)/$(WINE_MONO_SOURCE)
endef

define WINE_MONO_INSTALL_TARGET_CMDS
	cp -prn $(@D)/target/* $(TARGET_DIR)
endef

$(eval $(generic-package))
