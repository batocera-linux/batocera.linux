################################################################################
#
# Batocera splash
#
################################################################################
BATOCERA_SPLASH_VERSION = 1.1
BATOCERA_SPLASH_SOURCE=

BATOCERA_SPLASH_TGVERSION=$(BATOCERA_SYSTEM_VERSION) $(BATOCERA_SYSTEM_DATE_TIME)

ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_OMXPLAYER),y)
	BATOCERA_SPLASH_SCRIPT=S03splash-omx
	BATOCERA_SPLASH_MEDIA=video
else ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_FFPLAY),y)
	BATOCERA_SPLASH_SCRIPT=S03splash-ffplay
	BATOCERA_SPLASH_MEDIA=video
else ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_ROTATE_IMAGE),y)
	BATOCERA_SPLASH_SCRIPT=S03splash-image
	BATOCERA_SPLASH_MEDIA=rotate-image
else ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_MPV),y)
	BATOCERA_SPLASH_SCRIPT=S03splash-mpv
	BATOCERA_SPLASH_MEDIA=video
else
	BATOCERA_SPLASH_SCRIPT=S03splash-image
	BATOCERA_SPLASH_MEDIA=image
endif

BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_SCRIPT

ifeq ($(BATOCERA_SPLASH_MEDIA),image)
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_IMAGE
endif

ifeq ($(BATOCERA_SPLASH_MEDIA),rotate-image)
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_ROTATE_IMAGE
endif

ifeq ($(BATOCERA_SPLASH_MEDIA),video)
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_VIDEO
endif

define BATOCERA_SPLASH_INSTALL_SCRIPT
	mkdir -p $(TARGET_DIR)/etc/init.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/$(BATOCERA_SPLASH_SCRIPT)  $(TARGET_DIR)/etc/init.d/S03splash
endef

define BATOCERA_SPLASH_INSTALL_VIDEO
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/splash.mp4 $(TARGET_DIR)/usr/share/batocera/splash
	echo -e "1\n00:00:00,000 --> 00:00:02,000\n$(BATOCERA_SPLASH_TGVERSION)" > "${TARGET_DIR}/usr/share/batocera/splash/splash.srt"
endef

define BATOCERA_SPLASH_INSTALL_IMAGE
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo.png" -fill white -pointsize 30 -annotate +50+1020 "$(BATOCERA_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version.png"
endef

define BATOCERA_SPLASH_INSTALL_ROTATE_IMAGE
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo.png" -fill white -pointsize 30 -annotate +50+1020 "$(BATOCERA_SPLASH_TGVERSION)" -rotate -90 "${TARGET_DIR}/usr/share/batocera/splash/logo-version.png"
endef

$(eval $(generic-package))
