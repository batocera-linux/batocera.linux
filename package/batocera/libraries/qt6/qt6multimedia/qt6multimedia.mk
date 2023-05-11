################################################################################
#
# qt6multimedia
#
################################################################################

QT6MULTIMEDIA_VERSION = $(QT6_VERSION)
QT6MULTIMEDIA_SITE = $(QT6_SITE)
QT6MULTIMEDIA_SOURCE = qtmultimedia-$(QT6_SOURCE_TARBALL_PREFIX)-$(QT6MULTIMEDIA_VERSION).tar.xz
QT6MULTIMEDIA_INSTALL_STAGING = YES
QT6MULTIMEDIA_SUPPORTS_IN_SOURCE_BUILD = NO

QT6MULTIMEDIA_LICENSE = \
    GPL-2.0+ or LGPL-3.0, \
    GPL-3.0, GFDL-1.3 no invariants (docs)

QT6MULTIMEDIA_LICENSE_FILES = \
    LICENSES/GPL-2.0-only.txt \
    LICENSES/GPL-3.0-only.txt \
    LICENSES/LGPL-3.0-only.txt \
    LICENSES/GFDL-1.3-no-invariants-only.txt

QT6MULTIMEDIA_CONF_OPTS = \
    -GNinja \
    -DQT_HOST_PATH=$(HOST_DIR) \
    -DBUILD_WITH_PCH=OFF \
    -DQT_BUILD_EXAMPLES=OFF \
    -DQT_BUILD_TESTS=OFF

QT6MULTIMEDIA_DEPENDENCIES = qt6base qt6shadertools qt6declarative

define QT6MULTIMEDIA_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(BR2_CMAKE) --build $(QT6MULTIMEDIA_BUILDDIR)
endef

define QT6MULTIMEDIA_INSTALL_STAGING_CMDS
    $(TARGET_MAKE_ENV) DESTDIR=$(STAGING_DIR) $(BR2_CMAKE) --install $(QT6MULTIMEDIA_BUILDDIR)
endef

define QT6MULTIMEDIA_INSTALL_TARGET_CMDS
    $(TARGET_MAKE_ENV) DESTDIR=$(TARGET_DIR) $(BR2_CMAKE) --install $(QT6MULTIMEDIA_BUILDDIR)
endef

$(eval $(cmake-package))
