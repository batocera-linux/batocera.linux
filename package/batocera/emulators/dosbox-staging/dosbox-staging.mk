################################################################################
#
# dosbox-staging
#
################################################################################

DOSBOX_STAGING_VERSION = v0.82.2
DOSBOX_STAGING_SITE = $(call github,dosbox-staging,dosbox-staging,$(DOSBOX_STAGING_VERSION))
DOSBOX_STAGING_DEPENDENCIES = iir libpng libogg libvorbis opus opusfile
DOSBOX_STAGING_DEPENDENCIES += sdl2 sdl2_image speexdsp zlib 
DOSBOX_STAGING_LICENSE = GPLv2

DOSBOX_STAGING_CONF_OPTS = \
    -Dtracy=false \
    -Dunit_tests=disabled \
    -Dnarrowing_warnings=false \
    -Dautovec_info=false \
    -Dasm=false \
    -Dtime_trace=false

ifeq ($(BR2_PACKAGE_SDL2_NET),y)
DOSBOX_STAGING_CONF_OPTS += -Duse_sdl2_net=true
DOSBOX_STAGING_DEPENDENCIES += sdl2_net
else
DOSBOX_STAGING_CONF_OPTS += -Duse_sdl2_net=false
endif

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
DOSBOX_STAGING_CONF_OPTS += -Duse_fluidsynth=true
DOSBOX_STAGING_DEPENDENCIES += fluidsynth
else
DOSBOX_STAGING_CONF_OPTS += -Duse_fluidsynth=false
endif

ifeq ($(BR2_PACKAGE_MUNT),y)
DOSBOX_STAGING_CONF_OPTS += -Duse_mt32emu=true
DOSBOX_STAGING_DEPENDENCIES += munt
else
DOSBOX_STAGING_CONF_OPTS += -Duse_mt32emu=false
endif

ifeq ($(BR2_PACKAGE_SLIRP),y)
DOSBOX_STAGING_CONF_OPTS += -Duse_slirp=true
DOSBOX_STAGING_DEPENDENCIES += slirp
else
DOSBOX_STAGING_CONF_OPTS += -Duse_slirp=false
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
DOSBOX_STAGING_CONF_OPTS += -Duse_alsa=true
DOSBOX_STAGING_DEPENDENCIES += alsa-lib
else
DOSBOX_STAGING_CONF_OPTS += -Duse_alsa=false
endif

ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif

$(eval $(meson-package))
