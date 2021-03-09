################################################################################
#
# adwaita-icon-theme-light
#
################################################################################

ADWAITA_ICON_THEME_LIGHT_VERSION_MAJOR = 3.38
ADWAITA_ICON_THEME_LIGHT_VERSION = $(ADWAITA_ICON_THEME_LIGHT_VERSION_MAJOR).0
ADWAITA_ICON_THEME_LIGHT_SITE = http://ftp.gnome.org/pub/gnome/sources/adwaita-icon-theme/$(ADWAITA_ICON_THEME_LIGHT_VERSION_MAJOR)
ADWAITA_ICON_THEME_LIGHT_SOURCE = adwaita-icon-theme-$(ADWAITA_ICON_THEME_LIGHT_VERSION).tar.xz
ADWAITA_ICON_THEME_LIGHT_INSTALL_STAGING = YES
ADWAITA_ICON_THEME_LIGHT_LICENSE = LGPL-3.0 or CC-BY-SA-3.0
ADWAITA_ICON_THEME_LIGHT_LICENSE_FILES = COPYING COPYING_LGPL COPYING_CCBYSA3
ADWAITA_ICON_THEME_LIGHT_DEPENDENCIES = host-intltool host-libgtk3

define ADWAITA_ICON_THEME_LIGHT_REDUCE
        mkdir -p $(STAGING_DIR)/usr/share/icons/Adwaita/cursors
        mkdir -p $(TARGET_DIR)/usr/share/icons/Adwaita/cursors
	rm -rf $(@D)/Adwaita/96x96
	rm -rf $(@D)/Adwaita/256x256
	rm -rf $(@D)/Adwaita/512x512
	rm -rf $(@D)/Adwaita/*/mimetypes
	rm -rf $(@D)/Adwaita/*/apps
	rm -rf $(@D)/Adwaita/*/status
	rm -rf $(@D)/Adwaita/*/emotes
	rm -rf $(@D)/Adwaita/*/emblems
	rm -rf $(@D)/Adwaita/*/categories
	rm -rf $(@D)/Adwaita/*/ui
	rm -rf  $(@D)/Adwaita/cursors
endef

ADWAITA_ICON_THEME_LIGHT_PRE_CONFIGURE_HOOKS += ADWAITA_ICON_THEME_LIGHT_REDUCE


$(eval $(autotools-package))
