################################################################################
#
# lineapple-pie
#
################################################################################
# Version.: Commits on Oct 22, 2018
LINAPPLE_PIE_VERSION = c22ba0c3ad6c317b4f13486b7ff06a340c831122
LINAPPLE_PIE_SITE = $(call github,dabonetn,linapple-pie,$(LINAPPLE_PIE_VERSION))
LINAPPLE_PIE_LICENSE = GPLv2
LINAPPLE_PIE_DEPENDENCIES = sdl sdl_image libcurl zlib libzip

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	LINAPPLE_PIE_DEPENDENCIES += rpi-userland
endif

define LINAPPLE_PIE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" \
	$(MAKE) all -C $(@D)/src/ \
				CC="$(TARGET_CC)" \
				CXX="$(TARGET_CXX) -I $(STAGING_DIR)/usr/lib/libzip/include/" \
				SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl-config \
				CURL_CONFIG=$(STAGING_DIR)/usr/bin/curl-config
endef

define LINAPPLE_PIE_FIX_EXTRACT
	$(SED) "s|strip|$(STAGING_DIR)/../bin/strip|g"  $(@D)/src/Makefile
	$(SED) "s|mkdir \"$(INSTDIR)|mkdir -p \"$(INSTDIR)|g" $(@D)/src/Makefile
endef

LINAPPLE_PIE_CONFDIR = $(TARGET_DIR)/usr/share/batocera/datainit/system/.linapple
LINAPPLE_PIE_CONFFILE = $(LINAPPLE_PIE_CONFDIR)/linapple.conf

define LINAPPLE_PIE_INSTALL_TARGET_CMDS
	cp $(@D)/linapple $(TARGET_DIR)/usr/bin/
	mkdir -p $(LINAPPLE_PIE_CONFDIR)
	cp $(@D)/Master.dsk $(LINAPPLE_PIE_CONFDIR)/
	cp $(@D)/linapple.installed.conf $(LINAPPLE_PIE_CONFFILE)
	$(SED) "s|^\(\s*\)Slot 6 Directory =.*|\1Slot 6 Directory = /userdata/roms/apple2|g" $(LINAPPLE_PIE_CONFFILE)
	$(SED) "s|^\(\s*\)Save State Directory =.*|\1Save State Directory = /userdata/saves/apple2|g" $(LINAPPLE_PIE_CONFFILE)
	$(SED) "s|^\(\s*\)FTP Local Dir =.*|\1FTP Local Dir = /userdata/roms/apple2|g" $(LINAPPLE_PIE_CONFFILE)
	$(SED) "s|^\(\s*\)Fullscreen =.*|\1Fullscreen = 1|g" $(LINAPPLE_PIE_CONFFILE)
endef

LINAPPLE_PIE_POST_EXTRACT_HOOKS += LINAPPLE_PIE_FIX_EXTRACT

$(eval $(generic-package))