################################################################################
#
# lineapple
#
################################################################################
# Version.: Commits on May 26, 2020
LINAPPLE_VERSION = c93579fc7e71d3bd339079338cd9b2f05916828c
LINAPPLE_SITE = $(call github,linappleii,linapple,$(LINAPPLE_VERSION))
LINAPPLE_LICENSE = GPLv2
LINAPPLE_DEPENDENCIES = sdl sdl_image libcurl zlib libzip

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	LINAPPLE_DEPENDENCIES += rpi-userland
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
	LINAPPLE_EXTRA_ARGS = HAVE_X11=1
endif

define LINAPPLE_BUILD_CMDS
	$(SED) "s+/usr/local+$(STAGING_DIR)/usr+g" $(@D)/Makefile	
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CC="$(TARGET_CXX)" -C $(@D) \
		SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl-config \
		CURL_CONFIG=$(STAGING_DIR)/usr/bin/curl-config \
		$(LINAPPLE_EXTRA_ARGS)
endef

define LINAPPLE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/bin/linapple $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))