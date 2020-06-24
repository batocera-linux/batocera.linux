#############################################################
#
# alsa-plugins
#
#############################################################
ALSA_PLUGINS_VERSION = 1.2.2
ALSA_PLUGINS_SOURCE = alsa-plugins-$(ALSA_PLUGINS_VERSION).tar.bz2
ALSA_PLUGINS_SITE = ftp://ftp.alsa-project.org/pub/plugins
ALSA_PLUGINS_INSTALL_STAGING = NO
ALSA_PLUGINS_DEPENDENCIES = alsa-lib
ALSA_PLUGINS_POST_INSTALL_TARGET_HOOKS = ALSA_PLUGINS_PULSEAUDIO_CONF

ALSA_PLUGINS_CONF_OPTS += --with-plugindir=/usr/lib/alsa-lib \
	--localstatedir=/var \
	--disable-jack \
	--disable-avcodec \
	--with-speex=builtin

define ALSA_PLUGINS_PULSEAUDIO_CONF
	mv $(TARGET_DIR)/etc/alsa/conf.d/99-pulseaudio-default.conf.example \
		$(TARGET_DIR)/etc/alsa/conf.d/99-pulseaudio-default.conf
endef

$(eval $(autotools-package))
