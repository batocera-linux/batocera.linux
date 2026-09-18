################################################################################
#
# flatpak
#
################################################################################

FLATPAK_VERSION = 1.18.2
FLATPAK_SOURCE = flatpak-$(FLATPAK_VERSION).tar.xz
FLATPAK_SITE = https://github.com/flatpak/flatpak/releases/download/$(FLATPAK_VERSION)
FLATPAK_EMULATOR_INFO = flatpak.emulator.yml

FLATPAK_DEPENDENCIES += adwaita-icon-theme adwaita-icon-theme-light appstream bubblewrap
FLATPAK_DEPENDENCIES += gdk-pixbuf glib-networking hicolor-icon-theme host-bison
FLATPAK_DEPENDENCIES += host-pkgconf host-python3-pyparsing json-glib libarchive libcap
FLATPAK_DEPENDENCIES += libcurl libfuse3 libglib2 libgpgme libostree libseccomp libxml2
FLATPAK_DEPENDENCIES += polkit xdg-dbus-proxy

FLATPAK_CONF_OPTS += -Dsystem_install_dir=/userdata/saves/flatpak/binaries
FLATPAK_CONF_OPTS += -Drun_media_dir=/media
# the bundled bubblewrap/dbus-proxy are git wraps that can't be fetched here
FLATPAK_CONF_OPTS += -Dsystem_bubblewrap=/usr/bin/bwrap
FLATPAK_CONF_OPTS += -Dsystem_dbus_proxy=/usr/bin/xdg-dbus-proxy
FLATPAK_CONF_OPTS += -Dsystem_fusermount=/usr/bin/fusermount3
FLATPAK_CONF_OPTS += -Dselinux_module=disabled -Dsystemd=disabled
FLATPAK_CONF_OPTS += -Dmalcontent=disabled -Ddconf=disabled
FLATPAK_CONF_OPTS += -Dgir=disabled -Dgtkdoc=disabled -Ddocbook_docs=disabled -Dman=disabled
FLATPAK_CONF_OPTS += -Dtests=false -Dinstalled_tests=false

# polkit's ITS rules for the .policy translations are only in staging
FLATPAK_NINJA_ENV += GETTEXTDATADIRS=$(STAGING_DIR)/usr/share/gettext

ifeq ($(BR2_PACKAGE_XLIB_LIBXAU),y)
FLATPAK_CONF_OPTS += -Dxauth=enabled
FLATPAK_DEPENDENCIES += xlib_libXau
else
FLATPAK_CONF_OPTS += -Dxauth=disabled
endif

ifeq ($(BR2_PACKAGE_ZSTD),y)
FLATPAK_CONF_OPTS += -Dlibzstd=enabled
FLATPAK_DEPENDENCIES += zstd
else
FLATPAK_CONF_OPTS += -Dlibzstd=disabled
endif

ifeq ($(BR2_PACKAGE_WAYLAND)$(BR2_PACKAGE_WAYLAND_PROTOCOLS),yy)
FLATPAK_CONF_OPTS += -Dwayland_security_context=enabled
FLATPAK_DEPENDENCIES += wayland wayland-protocols
else
FLATPAK_CONF_OPTS += -Dwayland_security_context=disabled
endif

define FLATPAK_INSTALL_SCRIPTS
	install -m 0755 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/flatpak/batocera-flatpak-update \
		$(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/usr/share/emulationstation/hooks
	ln -sf /usr/bin/batocera-flatpak-update \
	    $(TARGET_DIR)/usr/share/emulationstation/hooks/preupdate-gamelists-flatpak
	ln -sf /usr/bin/batocera-steam-update \
	    $(TARGET_DIR)/usr/share/emulationstation/hooks/preupdate-gamelists-steam
endef

FLATPAK_POST_INSTALL_TARGET_HOOKS += FLATPAK_INSTALL_SCRIPTS

$(eval $(meson-package))
$(eval $(emulator-info-package))
