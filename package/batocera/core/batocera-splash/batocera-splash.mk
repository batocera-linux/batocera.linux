################################################################################
#
# Batocera splash
#
################################################################################
BATOCERA_SPLASH_VERSION = 1.0
BATOCERA_SPLASH_SOURCE=

BATOCERA_SPLASH_TGVERSION=$(BATOCERA_SYSTEM_VERSION) $(BATOCERA_SYSTEM_DATE_TIME)

ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_OMXPLAYER),y)
	BATOCERA_SPLASH_SCRIPT=S02splash-omx
	BATOCERA_SPLASH_MEDIA=video
else ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_FFPLAY),y)
	BATOCERA_SPLASH_SCRIPT=S02splash-ffplay
	BATOCERA_SPLASH_MEDIA=video
else
	BATOCERA_SPLASH_SCRIPT=S02splash-image
	BATOCERA_SPLASH_MEDIA=image
endif

BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_SCRIPT

ifeq ($(BATOCERA_SPLASH_MEDIA),image)
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_IMAGE
endif

ifeq ($(BATOCERA_SPLASH_MEDIA),video)
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_VIDEO
endif

define BATOCERA_SPLASH_INSTALL_SCRIPT
	mkdir -p $(TARGET_DIR)/etc/init.d
	cp package/batocera/core/batocera-splash/$(BATOCERA_SPLASH_SCRIPT)  $(TARGET_DIR)/etc/init.d/S02splash
endef

define BATOCERA_SPLASH_INSTALL_VIDEO
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	cp package/batocera/core/batocera-splash/splash.mp4 $(TARGET_DIR)/usr/share/batocera/splash
	echo -e "1\n00:00:00,000 --> 00:00:02,000\n$(BATOCERA_SPLASH_TGVERSION)" > "${TARGET_DIR}/usr/share/batocera/splash/splash.srt"
endef

define BATOCERA_SPLASH_INSTALL_IMAGE
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	convert "package/batocera/core/batocera-splash/logo.png" -fill white -pointsize 30 -annotate +50+1020 "$(BATOCERA_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version.png"
endef

$(eval $(generic-package))
