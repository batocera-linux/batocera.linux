################################################################################
#
# FLATPAK
#
################################################################################

FLATPAK_VERSION = 1.10.1
FLATPAK_SOURCE = flatpak-$(FLATPAK_VERSION).tar.xz
FLATPAK_SITE = https://github.com/flatpak/flatpak/releases/download/$(FLATPAK_VERSION)

FLATPAK_DEPENDENCIES += pkgconf host-pkgconf libcap libarchive libglib2 libsoup libgpgme polkit
FLATPAK_DEPENDENCIES += libostree json-glib appstream-glib yaml-cpp
FLATPAK_DEPENDENCIES += python3-pyparsing host-python3-pyparsing glib-networking libseccomp

FLATPAK_CONF_OPTS += --with-sysroot="$(STAGING_DIR)"
FLATPAK_CONF_OPTS += --with-gpgme-prefix="$(STAGING_DIR)/usr"
FLATPAK_CONF_OPTS += --with-system-install-dir="/userdata/flatpak"
FLATPAK_CONF_OPTS += --disable-selinux-module

FLATPAK_CONF_ENV += LDFLAGS=-lpthread

$(eval $(autotools-package))
$(eval $(host-autotools-package))
