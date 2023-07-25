################################################################################
#
# CORSIXTH
#
################################################################################

CORSIXTH_VERSION = v0.66
CORSIXTH_SITE = $(call github,CorsixTH,CorsixTH,$(CORSIXTH_VERSION))
CORSIXTH_DEPENDENCIES = sdl2 sdl2_image

ifeq ($(BR2_PACKAGE_LUAJIT),y)
CORSIXTH_CONF_OPTS += -DWITH_LUAJIT=ON
CORSIXTH_CONF_ENV += LDFLAGS="-lluajit-5.2"
endif

# Install into package prefix
#CORSIXTH_INSTALL_TARGET_OPTS = DESTDIR="$(CORSIXTH_PKG_INSTALL_DIR)" install

$(eval $(cmake-package))
