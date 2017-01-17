################################################################################
#
# Emulation Station 2 - recalbox version https://github.com/digitalLumberjack/recalbox-emulationstation
#
################################################################################

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
        RECALBOX_EMULATIONSTATION2_CONF_OPTS = -DRPI_VERSION=3
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
        RECALBOX_EMULATIONSTATION2_CONF_OPTS = -DRPI_VERSION=2
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI1),y)
        RECALBOX_EMULATIONSTATION2_CONF_OPTS = -DRPI_VERSION=1
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI0),y)
        RECALBOX_EMULATIONSTATION2_CONF_OPTS = -DRPI_VERSION=1
endif

RECALBOX_EMULATIONSTATION2_SITE = $(call github,nadenislamarre,recalbox-emulationstation,$(RECALBOX_EMULATIONSTATION2_VERSION))
RECALBOX_EMULATIONSTATION2_VERSION = batocera-5.X

RECALBOX_EMULATIONSTATION2_LICENSE = MIT
RECALBOX_EMULATIONSTATION2_DEPENDENCIES = sdl2 sdl2_mixer boost freeimage freetype eigen alsa-lib \
	libcurl openssl

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
RECALBOX_EMULATIONSTATION2_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
RECALBOX_EMULATIONSTATION2_DEPENDENCIES += libgles
endif


define RECALBOX_EMULATIONSTATION2_RPI_FIXUP
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/CMakeLists.txt
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/CMakeLists.txt
	$(SED) 's|/usr/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/CMakeLists.txt
endef

RECALBOX_EMULATIONSTATION2_PRE_CONFIGURE_HOOKS += RECALBOX_EMULATIONSTATION2_RPI_FIXUP

$(eval $(cmake-package))
