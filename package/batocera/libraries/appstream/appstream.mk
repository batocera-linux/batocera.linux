################################################################################
#
# appstream
#
################################################################################

APPSTREAM_VERSION = 1.2.0
APPSTREAM_SOURCE = AppStream-$(APPSTREAM_VERSION).tar.xz
APPSTREAM_SITE = https://www.freedesktop.org/software/appstream/releases
# the tarball's entries are prefixed with ./
APPSTREAM_STRIP_COMPONENTS = 2
APPSTREAM_LICENSE = LGPL-2.1+
APPSTREAM_LICENSE_FILES = COPYING
APPSTREAM_INSTALL_STAGING = YES

APPSTREAM_DEPENDENCIES = host-gperf host-pkgconf libcurl libfyaml libglib2 libxml2 libxmlb
APPSTREAM_DEPENDENCIES += $(TARGET_NLS_DEPENDENCIES)

APPSTREAM_CONF_OPTS = -Dstemming=false -Dsystemd=false -Dvapi=false -Dqt=false
APPSTREAM_CONF_OPTS += -Dcompose=false -Dblake3-support=false -Dbash-completion=false
APPSTREAM_CONF_OPTS += -Dgir=false -Dtools=false -Ddisplay-detection=none
APPSTREAM_CONF_OPTS += -Ddocs=false -Dapidocs=false -Dinstall-docs=false -Dman=false

ifeq ($(BR2_PACKAGE_ZSTD),y)
APPSTREAM_CONF_OPTS += -Dzstd-support=true
APPSTREAM_DEPENDENCIES += zstd
else
APPSTREAM_CONF_OPTS += -Dzstd-support=false
endif

$(eval $(meson-package))
