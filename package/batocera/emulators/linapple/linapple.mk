################################################################################
#
# lineapple
#
################################################################################
# Version.: Commits on Jun 01, 2020
LINAPPLE_VERSION = ae9fd93457469c260ba53a20246ad1669df1ba6e
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
	# force -j 1 to avoid parallel issues in the makefile
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -j 1 CC="$(TARGET_CXX)" -C $(@D) \
		SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl-config \
		CURL_CONFIG=$(STAGING_DIR)/usr/bin/curl-config \
		$(LINAPPLE_EXTRA_ARGS)
endef

define LINAPPLE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/bin/linapple $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))