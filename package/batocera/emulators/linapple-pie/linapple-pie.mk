################################################################################
#
# lineapple-pie
#
################################################################################

LINAPPLE_PIE_VERSION = recalbox
LINAPPLE_PIE_SITE = $(call github,LaurentMarchelli,linapple-pie,$(LINAPPLE_PIE_VERSION))
LINAPPLE_PIE_LICENSE = GPL2
LINAPPLE_PIE_LICENSE_FILES = COPYING

LINAPPLE_PIE_DEPENDENCIES = sdl sdl_image libcurl zlib libzip
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
LINAPPLE_PIE_DEPENDENCIES += rpi-userland
endif

LINAPPLE_PIE_MAKE_ENV = CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)"
LINAPPLE_PIE_MAKE_OPTS = \
	-C $(@D)/linapple-pie/src/ \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX) -I $(STAGING_DIR)/usr/lib/libzip/include/" \
	SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl-config \
	CURL_CONFIG=$(STAGING_DIR)/usr/bin/curl-config

define LINAPPLE_PIE_FIX_EXTRACT
	$(SED) "s|strip|$(STAGING_DIR)/../bin/strip|g"  $(@D)/linapple-pie/src/Makefile
	$(SED) "s|mkdir \"$(INSTDIR)|mkdir -p \"$(INSTDIR)|g" $(@D)/linapple-pie/src/Makefile
endef

define LINAPPLE_PIE_BUILD_CMDS
	$(LINAPPLE_PIE_MAKE_ENV) $(MAKE) all $(LINAPPLE_PIE_MAKE_OPTS)
endef

ifeq ($(BR2_PACKAGE_RECALBOX_SYSTEM),y)
LINAPPLE_PIE_CONFDIR = $(TARGET_DIR)/recalbox/share_init/system/.linapple
LINAPPLE_PIE_CONFFILE = $(LINAPPLE_PIE_CONFDIR)/linapple.conf
define LINAPPLE_PIE_INSTALL_TARGET_CMDS
	cp $(@D)/linapple-pie/linapple $(TARGET_DIR)/usr/bin/
	mkdir -p $(LINAPPLE_PIE_CONFDIR)
	cp $(@D)/linapple-pie/Master.dsk $(LINAPPLE_PIE_CONFDIR)/
	cp $(@D)/linapple-pie/linapple.installed.conf $(LINAPPLE_PIE_CONFFILE)
	$(SED) "s|^\(\s*\)Slot 6 Directory =.*|\1Slot 6 Directory = /recalbox/share/roms/apple2|g" $(LINAPPLE_PIE_CONFFILE)
	$(SED) "s|^\(\s*\)Save State Directory =.*|\1Save State Directory = /recalbox/share/saves/apple2|g" $(LINAPPLE_PIE_CONFFILE)
	$(SED) "s|^\(\s*\)FTP Local Dir =.*|\1FTP Local Dir = /recalbox/share/roms/apple2|g" $(LINAPPLE_PIE_CONFFILE)
	echo -e "\n##########################################################################" >> $(LINAPPLE_PIE_CONFFILE)
	echo -e "#\tRecalbox specific parameters\n" >> $(LINAPPLE_PIE_CONFFILE)
	echo -e "\tRecalboxRomDirectory =\t/recalbox/share/roms/apple2" >> $(LINAPPLE_PIE_CONFFILE)
	echo -e "\tRecalboxSaveDirectory =\t/recalbox/share/saves/apple2" >> $(LINAPPLE_PIE_CONFFILE)
endef
else
LINAPPLE_PIE_STARTUP = /usr/bin/linapple
LINAPPLE_PIE_INSTDIR = /usr/linapple
define LINAPPLE_PIE_INSTALL_TARGET_CMDS
	$(LINAPPLE_PIE_MAKE_ENV) $(MAKE) install $(LINAPPLE_PIE_MAKE_OPTS) \
		STARTUP=$(TARGET_DIR)$(LINAPPLE_PIE_STARTUP)\
		INSTDIR=$(TARGET_DIR)$(LINAPPLE_PIE_INSTDIR)
	echo "cd \"$(LINAPPLE_PIE_INSTDIR)\"; ./linapple; cd -" >"$(TARGET_DIR)$(LINAPPLE_PIE_STARTUP)"
	chmod 755 "$(TARGET_DIR)$(LINAPPLE_PIE_STARTUP)"
endef
endif

LINAPPLE_PIE_POST_EXTRACT_HOOKS += LINAPPLE_PIE_FIX_EXTRACT

$(eval $(generic-package))
