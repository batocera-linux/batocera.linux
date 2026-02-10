################################################################################
#
# pipewire-ffmpeg-plugins
#
################################################################################

PIPEWIRE_FFMPEG_PLUGINS_VERSION = $(PIPEWIRE_VERSION)
PIPEWIRE_FFMPEG_PLUGINS_SOURCE = pipewire-$(PIPEWIRE_VERSION).tar.bz2
PIPEWIRE_FFMPEG_PLUGINS_SITE = https://gitlab.freedesktop.org/pipewire/pipewire/-/archive/$(PIPEWIRE_VERSION)
PIPEWIRE_FFMPEG_PLUGINS_LICENSE = MIT, LGPL-2.1+
PIPEWIRE_FFMPEG_PLUGINS_LICENSE_FILES = COPYING LICENSE
PIPEWIRE_FFMPEG_PLUGINS_DEPENDENCIES = host-pkgconf pipewire ffmpeg

PIPEWIRE_FFMPEG_PLUGINS_CONF_OPTS = \
	-Ddocs=disabled \
	-Dman=disabled \
	-Dtests=disabled \
	-Dinstalled_tests=disabled \
	-Dexamples=disabled \
	-Dspa-plugins=enabled \
	-Dffmpeg=enabled \
	-Dvideoconvert=enabled \
	-Daudiomixer=disabled \
	-Daudioconvert=enabled \
	-Daudiotestsrc=disabled \
	-Dcontrol=disabled \
	-Dsupport=enabled \
	-Dvideotestsrc=disabled \
	-Dvolume=disabled \
	-Dvulkan=disabled \
	-Dpipewire-alsa=disabled \
	-Dpipewire-jack=disabled \
	-Dpipewire-v4l2=disabled \
	-Dalsa=disabled \
	-Dbluez5=disabled \
	-Dbluez5-codec-opus=disabled \
	-Djack=disabled \
	-Dlibcamera=disabled \
	-Dv4l2=disabled \
	-Ddbus=disabled \
	-Dflatpak=disabled \
	-Dgstreamer=disabled \
	-Dsystemd=disabled \
	-Dsystemd-system-service=disabled \
	-Dsystemd-user-service=disabled \
	-Davahi=disabled \
	-Dlv2=disabled \
	-Dx11=disabled \
	-Dx11-xfixes=disabled \
	-Dlibpulse=disabled \
	-Dreadline=disabled \
	-Dsdl2=disabled \
	-Dudev=disabled \
	-Decho-cancel-webrtc=disabled \
	-Draop=disabled \
	-Dcompress-offload=disabled \
	-Davb=disabled \
	-Dlibcanberra=disabled \
	-Dgsettings=disabled \
	-Dlibusb=disabled \
	-Dopus=disabled \
	-Dsession-managers= \
	-Dlegacy-rtkit=false \
	-Devl=disabled \
	-Dtest=disabled \
	--wrap-mode=default

ifeq ($(BR2_PACKAGE_LIBSNDFILE),y)
PIPEWIRE_FFMPEG_PLUGINS_CONF_OPTS += -Dpw-cat=enabled -Dpw-cat-ffmpeg=enabled -Dsndfile=enabled
PIPEWIRE_FFMPEG_PLUGINS_DEPENDENCIES += libsndfile
else
PIPEWIRE_FFMPEG_PLUGINS_CONF_OPTS += -Dpw-cat=disabled -Dpw-cat-ffmpeg=disabled -Dsndfile=disabled
endif

define PIPEWIRE_FFMPEG_PLUGINS_INSTALL_TARGET_CMDS
	$(INSTALL) -d $(TARGET_DIR)/usr/lib/spa-0.2/ffmpeg
	$(INSTALL) -m 0755 $(@D)/build/spa/plugins/ffmpeg/libspa-ffmpeg.so \
		$(TARGET_DIR)/usr/lib/spa-0.2/ffmpeg/
	$(INSTALL) -m 0755 $(@D)/build/spa/plugins/videoconvert/libspa-videoconvert.so \
		$(TARGET_DIR)/usr/lib/spa-0.2/videoconvert/
endef

ifeq ($(BR2_PACKAGE_LIBSNDFILE),y)
define PIPEWIRE_FFMPEG_PLUGINS_INSTALL_PW_CAT
	$(INSTALL) -m 0755 $(@D)/build/src/tools/pw-cat \
		$(TARGET_DIR)/usr/bin/pw-cat
endef

PIPEWIRE_FFMPEG_PLUGINS_POST_INSTALL_TARGET_HOOKS += PIPEWIRE_FFMPEG_PLUGINS_INSTALL_PW_CAT
endif

$(eval $(meson-package))
