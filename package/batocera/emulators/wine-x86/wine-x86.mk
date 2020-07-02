################################################################################
#
# wine-x86
#
################################################################################

# version 5.18 means binary from 5.18 version (or the last built if the version is not yet out)
WINE_X86_VERSION = $(BATOCERA_SYSTEM_VERSION)
WINE_X86_SOURCE = wine-x86-$(WINE_X86_VERSION).tar.gz
WINE_X86_SITE = https://github.com/batocera-linux/wine-x86/releases/download/$(WINE_X86_VERSION)

# Wine Mono addon (required)
WINE_MONO_VERSION = 4.9.4
WINE_MONO_SOURCE = wine-mono-bin-$(WINE_MONO_VERSION).tar.gz
WINE_MONO_SITE = https://dl.winehq.org/wine/wine-mono/$(WINE_MONO_VERSION)/$(WINE_MONO_SOURCE)

# Wine Gecko addon (required)
WINE_GECKO_VERSION = 2.47.1
WINE_GECKO_SOURCE = wine-gecko-$(WINE_GECKO_VERSION)-x86.tar.bz2
WINE_GECKO_SITE = https://dl.winehq.org/wine/wine-gecko/$(WINE_GECKO_VERSION)/$(WINE_GECKO_SOURCE)

define WINE_X86_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(WINE_X86_DL_SUBDIR)/$(WINE_X86_SOURCE)
	mkdir -p $(@D)/target/usr/share/wine/mono && cd $(@D)/target/usr/share/wine/mono && wget -qO- $(WINE_MONO_SITE) | tar -xzf -
	mkdir -p $(@D)/target/usr/share/wine/gecko && cd $(@D)/target/usr/share/wine/gecko && wget -qO- $(WINE_GECKO_SITE) | tar -xjf -
endef

define WINE_X86_INSTALL_TARGET_CMDS
	cp -prn $(@D)/target/* $(TARGET_DIR)
endef

$(eval $(generic-package))
