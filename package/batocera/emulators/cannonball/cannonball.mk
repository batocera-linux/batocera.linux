################################################################################
#
# cannonball
#
################################################################################
# Version.: Commits on Oct 19, 2019
CANNONBALL_VERSION = b6aa525ddd552f96b43b3b3a6f69326a277206bd
CANNONBALL_SITE = $(call github,djyt,cannonball,$(CANNONBALL_VERSION))
CANNONBALL_LICENSE = GPLv2
CANNONBALL_DEPENDENCIES = sdl2 boost

CANNONBALL_TARGET = sdl2

CANNONBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DTARGET=$(CANNONBALL_TARGET)

CANNONBALL_SUPPORTS_IN_SOURCE_BUILD = NO

define CANNONBALL_SETUP_CMAKE
	cd $(@D)
	cp $(@D)/cmake/* $(@D)/
endef

CANNONBALL_PRE_CONFIGURE_HOOKS += CANNONBALL_SETUP_CMAKE

#define CANNONBALL_BUILD_CMDS
	#cd $(@D)
	#cp cmake/* .
	#$(TARGET_CONFIGURE_OPTS) $(MAKE) -G "Unix Makefiles" $(CANNONBALL_CONF_OPTS)
	#$(SED) "s+/usr/local+$(STAGING_DIR)/usr+g" $(@D)/Makefile
	#$(TARGET_CONFIGURE_OPTS) $(MAKE) CC="$(TARGET_CXX)" -C $(@D) \
	#	SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl-config \
	#	CURL_CONFIG=$(STAGING_DIR)/usr/bin/curl-config \
	#	$(CANNONBALL_EXTRA_ARGS)
#endef

define CANNONBALL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/cannonball $(TARGET_DIR)/usr/bin/
endef

$(eval $(cmake-package))
