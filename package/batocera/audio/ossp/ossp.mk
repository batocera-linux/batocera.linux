################################################################################
#
# ossp
#
################################################################################

OSSP_VERSION = v1.3.3
OSSP_SITE = $(call github,OpenMandrivaSoftware,ossp,$(OSSP_VERSION))
OSSP_LICENSE = GPLv2
OSSP_DEPENDENCIES = libfuse3

OSSP_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OSSP_CONF_OPTS += -Ddaemon=ON
OSSP_CONF_OPTS += -Dtest=OFF

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
OSSP_CONF_OPTS += -Dalsa=ON
OSSP_DEPENDENCIES += alsa-lib
else
OSSP_CONF_OPTS += -Dalsa=ON
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
OSSP_CONF_OPTS += -Dpulseaudio=ON
OSSP_DEPENDENCIES += pulseaudio
else
OSSP_CONF_OPTS += -Dpulseaudio=OFF
endif

define OSSP_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/sbin
    cp $(@D)/osspd $(TARGET_DIR)/usr/sbin/
    cp $(@D)/ossp-alsap $(TARGET_DIR)/usr/sbin/
    cp $(@D)/ossp-padsp $(TARGET_DIR)/usr/sbin/
endef

define OSSP_INITD
	mkdir -p $(TARGET_DIR)/etc/init.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/audio/ossp/osspd \
	    $(TARGET_DIR)/etc/init.d/S34osspd
endef

OSSP_POST_INSTALL_TARGET_HOOKS += OSSP_INITD

$(eval $(cmake-package))
