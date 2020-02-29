################################################################################
#
# lineapple-pie
#
################################################################################
# Version.: Commits on Feb 27, 2020
LINAPPLE_PIE_VERSION = 8ddc3f61dbbaf984ec11e4577544a1fd86f9e7c9
LINAPPLE_PIE_SITE = $(call github,linappleii,linapple,$(LINAPPLE_PIE_VERSION))
LINAPPLE_PIE_LICENSE = GPLv2
LINAPPLE_PIE_DEPENDENCIES = sdl sdl_image libcurl zlib libzip

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	LINAPPLE_PIE_DEPENDENCIES += rpi-userland
endif

define LINAPPLE_PIE_BUILD_CMDS
	$(SED) "s+/usr/local+$(STAGING_DIR)/usr+g" $(@D)/Makefile	
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CC="$(TARGET_CXX)" -C $(@D) \
		SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl-config \
		CURL_CONFIG=$(STAGING_DIR)/usr/bin/curl-config
endef

define LINAPPLE_PIE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bin/linapple $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))