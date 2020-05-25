#############################################################
#
# alsa-plugins
#
#############################################################
ALSA_PLUGINS_VERSION = 1.2.2
ALSA_PLUGINS_SOURCE = alsa-plugins-$(ALSA_PLUGINS_VERSION).tar.bz2
ALSA_PLUGINS_SITE = ftp://ftp.alsa-project.org/pub/plugins
ALSA_PLUGINS_INSTALL_STAGING = NO
ALSA_PLUGINS_DEPENDENCIES = alsa-lib libsamplerate

ALSA_PLUGINS_CONF_OPTS += --with-plugindir=/usr/lib/alsa \
	--localstatedir=/var \
	--disable-jack \
	--enable-samplerate \
	--disable-avcodec \
	--with-speex=builtin

$(eval $(autotools-package))
