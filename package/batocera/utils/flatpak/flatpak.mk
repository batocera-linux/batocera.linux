################################################################################
#
# FLATPAK
#
################################################################################

FLATPAK_VERSION = 1.10.1
FLATPAK_SOURCE = flatpak-$(FLATPAK_VERSION).tar.xz
FLATPAK_SITE = https://github.com/flatpak/flatpak/releases/download/$(FLATPAK_VERSION)

FLATPAK_DEPENDENCIES += pkgconf host-pkgconf libcap libarchive libglib2 libsoup libgpgme polkit libostree json-glib appstream-glib yaml-cpp python-pyparsing host-python-pyparsing python3-pyparsing host-python3-pyparsing

FLATPAK_CONF_OPTS += --with-sysroot=$(STAGING_DIR) --with-gpgme-prefix=$(STAGING_DIR)/usr --disable-selinux-module --disable-seccomp

FLATPAK_CONF_ENV += LDFLAGS=-lpthread PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig

$(eval $(autotools-package))
$(eval $(host-autotools-package))
