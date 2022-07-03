################################################################################
#
# ionfury
#
################################################################################
# June 13, 2022
IONFURY_VERSION = 54177821c32a0ba601da9b43f02647fb7d1aa291
IONFURY_SITE = https://voidpoint.io/terminx/eduke32/-/archive/$(IONFURY_VERSION)
IONFURY_DEPENDENCIES = sdl2 flac libvpx
IONFURY_LICENSE = GPL-2.0

# Some build options are documented here: https://wiki.ionfury.com/wiki/Building_EDuke32_on_Linux
IONFURY_BUILD_ARGS = FURY=1 STARTUP_WINDOW=0 HAVE_GTK2=0
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
    IONFURY_BUILD_ARGS += USE_OPENGL=0 OPTOPT="-mcpu=cortex-a72 -mtune=cortex-a72 -ffast-math"
endif

define IONFURY_BUILD_CMDS
    $(MAKE) $(TARGET_CONFIGURE_OPTS) $(IONFURY_BUILD_ARGS) -C $(@D)
endef

define IONFURY_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/fury $(TARGET_DIR)/usr/bin/ionfury
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/ionfury/ionfury.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))