################################################################################
#
# Batocera splash
#
################################################################################
BATOCERA_SPLASH_VERSION = 5.1
BATOCERA_SPLASH_SOURCE=
BATOCERA_SYSTEM_GIT_VERSION = $(shell git log -n 1 --pretty=format:"%h")

ifeq ($(findstring dev,$(BATOCERA_SYSTEM_VERSION)),dev)
	BATOCERA_SPLASH_TGVERSION=$(BATOCERA_SYSTEM_VERSION)-$(BATOCERA_SYSTEM_GIT_VERSION) $(BATOCERA_SYSTEM_DATE_TIME)
else
	BATOCERA_SPLASH_TGVERSION=$(BATOCERA_SYSTEM_VERSION) $(BATOCERA_SYSTEM_DATE)
endif

BATOCERA_SPLASH_PLAYER_OPTIONS=

ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_OMXPLAYER),y)
	BATOCERA_SPLASH_SCRIPT=Ssplash-omx
	BATOCERA_SPLASH_MEDIA=video
else ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_FFPLAY),y)
	BATOCERA_SPLASH_SCRIPT=Ssplash-ffplay
	BATOCERA_SPLASH_MEDIA=video
else ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_MPV),y)
	BATOCERA_SPLASH_SCRIPT=Ssplash-mpv.template
	BATOCERA_SPLASH_MEDIA=video
else ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_ROTATE_IMAGE),y)
    BATOCERA_SPLASH_SCRIPT=Ssplash-image
    ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326_ANY),y)
        BATOCERA_SPLASH_MEDIA=rotate-rk3326-image
    else
        BATOCERA_SPLASH_MEDIA=rotate-image
    endif
else
	BATOCERA_SPLASH_SCRIPT=Ssplash-image
	BATOCERA_SPLASH_MEDIA=image
endif

ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_MPV),y)
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
        # drm doesn't work on my nvidia card. sdl run smoothly.
        BATOCERA_SPLASH_PLAYER_OPTIONS=--vo=drm,sdl --hwdec=yes
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
        # hwdec=yes doesnt work for n2
        BATOCERA_SPLASH_PLAYER_OPTIONS=
else
	BATOCERA_SPLASH_PLAYER_OPTIONS=--hwdec=yes
endif
endif

BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_SCRIPT

ifeq ($(BATOCERA_SPLASH_MEDIA),image)
    ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_GAMEFORCE)$(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
        BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_SMALL_IMAGE
    else
	    BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_IMAGE
    endif
endif

ifeq ($(BATOCERA_SPLASH_MEDIA),rotate-rk3326-image)
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_ROTATE_RK3326_IMAGE
endif

ifeq ($(BATOCERA_SPLASH_MEDIA),rotate-image)
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_ROTATE_IMAGE
endif

ifeq ($(BATOCERA_SPLASH_MEDIA),video)
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SPLASH_INSTALL_VIDEO
endif

define BATOCERA_SPLASH_INSTALL_SCRIPT
	mkdir -p $(TARGET_DIR)/etc/init.d
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/Ssystem-splash	$(TARGET_DIR)/etc/init.d/S03system-splash
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/Ssplashscreencontrol	$(TARGET_DIR)/etc/init.d/S30splashscreencontrol
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/$(BATOCERA_SPLASH_SCRIPT)	$(TARGET_DIR)/etc/init.d/S28splash
	sed -i -e s+"%PLAYER_OPTIONS%"+"$(BATOCERA_SPLASH_PLAYER_OPTIONS)"+g $(TARGET_DIR)/etc/init.d/S28splash
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
	BATO_SPLASH=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/Capcom.mp4
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SYSTEM_SPLASH
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2)$(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	BATO_SPLASH=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/splash720p.mp4
    BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SYSTEM_SPLASH
else ifeq ($(BR2_PACKAGE_BATOCERA_SPLASH_ROTATE_IMAGE),y)
	BATO_SPLASH=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/splash.mp4
	BATOCERA_SPLASH_POST_INSTALL_TARGET_HOOKS += BATOCERA_SYSTEM_SPLASH
endif

define BATOCERA_SYSTEM_SPLASH
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo.png" "${TARGET_DIR}/usr/share/batocera/splash/boot-logo.png"
endef

define BATOCERA_SPLASH_INSTALL_VIDEO
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	cp $(BATO_SPLASH) $(TARGET_DIR)/usr/share/batocera/splash/splash.mp4
	echo -e "1\n00:00:00,000 --> 00:00:02,000\n$(BATOCERA_SPLASH_TGVERSION)" > "${TARGET_DIR}/usr/share/batocera/splash/splash.srt"
endef

define BATOCERA_SPLASH_INSTALL_IMAGE
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo.png" -fill white -pointsize 30 -annotate +50+1020 "$(BATOCERA_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version.png"
endef

define BATOCERA_SPLASH_INSTALL_SMALL_IMAGE
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
    cp "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo480p.png" "${TARGET_DIR}/usr/share/batocera/splash/boot-logo.png"
    convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo480p.png" -fill white -pointsize 20 -annotate +40+440 "$(BATOCERA_SPLASH_TGVERSION)" "${TARGET_DIR}/usr/share/batocera/splash/logo-version.png"
endef

define BATOCERA_SPLASH_INSTALL_ROTATE_RK3326_IMAGE
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo.png" -shave 150x0 -resize 480x320 -fill white -pointsize 15 -annotate +40+300 "$(BATOCERA_SPLASH_TGVERSION)" -rotate -90 "${TARGET_DIR}/usr/share/batocera/splash/logo-version-320x480.png"
	convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo.png"              -resize 854x480 -fill white -pointsize 15 -annotate +40+440 "$(BATOCERA_SPLASH_TGVERSION)" -rotate -90 "${TARGET_DIR}/usr/share/batocera/splash/logo-version-480x854.png"
endef

define BATOCERA_SPLASH_INSTALL_ROTATE_IMAGE
	mkdir -p $(TARGET_DIR)/usr/share/batocera/splash
	convert "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-splash/logo.png" -fill white -pointsize 30 -annotate +50+1020 "$(BATOCERA_SPLASH_TGVERSION)" -rotate -90 "${TARGET_DIR}/usr/share/batocera/splash/logo-version.png"
	ln -sf "logo-version.png" "${TARGET_DIR}/usr/share/batocera/splash/boot-logo.png"
endef

$(eval $(generic-package))
