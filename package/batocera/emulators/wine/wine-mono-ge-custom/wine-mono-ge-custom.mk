################################################################################
#
# wine-mono-ge-custom
#
################################################################################

# Wine Mono addon (required)
WINE_MONO_GE_CUSTOM_VERSION = 8.1.0
WINE_MONO_GE_CUSTOM_SOURCE = wine-mono-$(WINE_MONO_GE_CUSTOM_VERSION)-x86.tar.xz
WINE_MONO_GE_CUSTOM_SITE = https://dl.winehq.org/wine/wine-mono/$(WINE_MONO_GE_CUSTOM_VERSION)

define WINE_MONO_GE_CUSTOM_EXTRACT_CMDS
	mkdir -p $(@D)/target/usr/wine/ge-custom/share/wine/mono/
	cd $(@D)/target/usr/wine/ge-custom/share/wine/mono/ && \
	    tar xf $(DL_DIR)/$(WINE_MONO_GE_CUSTOM_DL_SUBDIR)/$(WINE_MONO_GE_CUSTOM_SOURCE)
endef

define WINE_MONO_GE_CUSTOM_INSTALL_TARGET_CMDS
	cp -prn $(@D)/target/* $(TARGET_DIR)
endef

$(eval $(generic-package))
