################################################################################
#
# moonlight-qt
#
################################################################################

MOONLIGHT_QT_VERSION = v6.1.0
MOONLIGHT_QT_SITE = https://github.com/moonlight-stream/moonlight-qt
MOONLIGHT_QT_SITE_METHOD = git
MOONLIGHT_QT_GIT_SUBMODULES = YES
MOONLIGHT_QT_LICENSE = GPLv3

MOONLIGHT_QT_DEPENDENCIES = \
	qt6base \
	qt6svg \
	qt6declarative \
	sdl2 \
	sdl2_ttf \
	opus \
	ffmpeg \
	openssl

MOONLIGHT_QT_CONF_OPTS += PREFIX=/usr

MOONLIGHT_QT_CONF_OPTS += QMAKE_CC=$(TARGET_CC)
MOONLIGHT_QT_CONF_OPTS += QMAKE_CXX=$(TARGET_CXX)
MOONLIGHT_QT_CONF_OPTS += QMAKE_LINK=$(TARGET_CXX)
MOONLIGHT_QT_CONF_OPTS += QMAKE_CFLAGS+="$(TARGET_CFLAGS)"
MOONLIGHT_QT_CONF_OPTS += QMAKE_CXXFLAGS+="$(TARGET_CXXFLAGS)"

ifeq ($(BR2_PACKAGE_LIBDRM),y)
MOONLIGHT_QT_DEPENDENCIES += libdrm
else
MOONLIGHT_QT_CONF_OPTS += CONFIG+=disable-libdrm
endif

ifeq ($(BR2_PACKAGE_LIBVA),y)
MOONLIGHT_QT_DEPENDENCIES += libva
else
MOONLIGHT_QT_CONF_OPTS += CONFIG+=disable-libva
endif

ifeq ($(BR2_PACKAGE_LIBVDPAU),y)
MOONLIGHT_QT_DEPENDENCIES += libvdpau
else
MOONLIGHT_QT_CONF_OPTS += CONFIG+=disable-libvdpau
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
MOONLIGHT_QT_DEPENDENCIES += xlib_libX11 libxkbcommon
else
MOONLIGHT_QT_CONF_OPTS += CONFIG+=disable-x11
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
MOONLIGHT_QT_DEPENDENCIES += wayland wayland-protocols qt6wayland
else
MOONLIGHT_QT_CONF_OPTS += CONFIG+=disable-wayland
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
ifneq ($(BR2_PACKAGE_BATOCERA_RPI_ANY),y)
MOONLIGHT_QT_DEPENDENCIES += libplacebo vulkan-headers vulkan-loader
endif
endif

ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
MOONLIGHT_QT_CONF_OPTS += CONFIG+=gpuslow
endif

MOONLIGHT_QT_CONF_OPTS += CONFIG+=embedded

MOONLIGHT_QT_CONF_OPTS += moonlight-qt.pro

# The file "qt6.conf" can be used to override the hard-coded paths that are
# compiled into the Qt library. We need it to make "qmake" relocatable and
# tweak the per-package install paths
define MOONLIGHT_QT_INSTALL_QT_CONF
	rm -f $(HOST_DIR)/bin/qt6.conf
	sed -e "s|@@HOST_DIR@@|$(HOST_DIR)|" -e "s|@@STAGING_DIR@@|$(STAGING_DIR)|" \
		$(MOONLIGHT_QT_PKGDIR)/qt.conf.in > $(HOST_DIR)/bin/qt6.conf
endef

MOONLIGHT_QT_PRE_CONFIGURE_HOOKS += MOONLIGHT_QT_INSTALL_QT_CONF

define MOONLIGHT_QT_CONFIGURE_CMDS
	cd $(@D) && \
	$(TARGET_MAKE_ENV) $(MOONLIGHT_QT_CONF_ENV) \
	$(HOST_DIR)/bin/qmake6 -spec devices/linux-generic-g++ $(MOONLIGHT_QT_CONF_OPTS)
endef

define MOONLIGHT_QT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MOONLIGHT_QT_MAKE_ENV) $(MAKE) -C $(@D)
endef

define MOONLIGHT_QT_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/app/moonlight \
		$(TARGET_DIR)/usr/bin/moonlight-qt
endef

$(eval $(generic-package))
