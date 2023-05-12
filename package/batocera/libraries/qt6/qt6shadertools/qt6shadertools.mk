################################################################################
#
# qt6shadertools
#
################################################################################

QT6SHADERTOOLS_VERSION = $(QT6_VERSION)
QT6SHADERTOOLS_SITE = $(QT6_SITE)
QT6SHADERTOOLS_SOURCE = qtshadertools-$(QT6_SOURCE_TARBALL_PREFIX)-$(QT6SHADERTOOLS_VERSION).tar.xz
QT6SHADERTOOLS_INSTALL_STAGING = YES
QT6SHADERTOOLS_SUPPORTS_IN_SOURCE_BUILD = NO

QT6SHADERTOOLS_LICENSE = \
    GPL-2.0+ or LGPL-3.0, \
    GPL-3.0, GFDL-1.3 no invariants (docs)

QT6SHADERTOOLS_LICENSE_FILES = \
    LICENSES/GPL-2.0-only.txt \
    LICENSES/GPL-3.0-only.txt \
    LICENSES/LGPL-3.0-only.txt \
    LICENSES/GFDL-1.3-no-invariants-only.txt

QT6SHADERTOOLS_CONF_OPTS = \
    -GNinja \
    -DQT_HOST_PATH=$(HOST_DIR) \
    -DBUILD_WITH_PCH=OFF \
    -DQT_BUILD_TOOLS_BY_DEFAULT=ON \
    -DQT_BUILD_TESTS_BY_DEFAULT=OFF \
    -DQT_BUILD_EXAMPLES_BY_DEFAULT=OFF

QT6SHADERTOOLS_DEPENDENCIES = qt6base host-qt6shadertools

define QT6SHADERTOOLS_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(BR2_CMAKE) --build $(QT6SHADERTOOLS_BUILDDIR)
endef

define QT6SHADERTOOLS_INSTALL_STAGING_CMDS
    $(TARGET_MAKE_ENV) DESTDIR=$(STAGING_DIR) $(BR2_CMAKE) --install $(QT6SHADERTOOLS_BUILDDIR)
endef

define QT6SHADERTOOLS_INSTALL_TARGET_CMDS
    $(TARGET_MAKE_ENV) DESTDIR=$(TARGET_DIR) $(BR2_CMAKE) --install $(QT6SHADERTOOLS_BUILDDIR)
endef

HOST_QT6SHADERTOOLS_DEPENDENCIES = \
	host-ninja \
	host-double-conversion \
	host-libb2 \
	host-pcre2 \
	host-zlib \
    host-qt6base
HOST_QT6SHADERTOOLS_CONF_OPTS = \
    -GNinja \
    -DQT_HOST_PATH=$(HOST_DIR)

define HOST_QT6SHADERTOOLS_BUILD_CMDS
	$(HOST_MAKE_ENV) $(BR2_CMAKE) --build $(HOST_QT6SHADERTOOLS_BUILDDIR)
endef

define HOST_QT6SHADERTOOLS_INSTALL_CMDS
	$(HOST_MAKE_ENV) $(BR2_CMAKE) --install $(HOST_QT6SHADERTOOLS_BUILDDIR)
endef

$(eval $(cmake-package))
$(eval $(host-cmake-package))
