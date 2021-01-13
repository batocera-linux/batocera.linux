################################################################################
#
# gl4es-openmw
#
################################################################################

GL4ES_OPENMW_VERSION = v1.1.4
GL4ES_OPENMW_SITE = $(call github,ptitSeb,gl4es,$(GL4ES_OPENMW_VERSION))
GL4ES_OPENMW_LICENSE = GPL-3.0+
GL4ES_OPENMW_DEPENDENCIES = libgles
GL4ES_OPENMW_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_XORG7),y)
GL4ES_OPENMW_DEPENDENCIES += xlib_libX11
GL4ES_OPENMW_CONF_OPTS += -DNOX11=OFF
else
GL4ES_OPENMW_CONF_OPTS += -DNOX11=ON
endif

# EGL does not work reliably for feature detection.
#
# Instead, we initialize gl4es manually via an openmw patch
# and disable everything here.
GL4ES_OPENMW_CONF_OPTS += \
	-DNOEGL=ON -DNO_GBM=ON -DNO_LOADER=ON -DNO_INIT_CONSTRUCTOR=ON -DDEFAULT_ES=2

define GL4ES_OPENMW_INSTALL_TARGET_CMDS
$(INSTALL) -D -m 0755 $(@D)/lib/*.so.1 -t $(TARGET_DIR)/usr/lib/openmw/gl4es/
endef

define GL4ES_OPENMW_INSTALL_STAGING_CMDS
$(INSTALL) -D -m 0644 $(@D)/include/gl4es*.h -t $(STAGING_DIR)/usr/include/openmw/gl4es/
$(INSTALL) -D -m 0644 $(@D)/include/GL/*.h -t $(STAGING_DIR)/usr/include/openmw/gl4es/GL
endef

$(eval $(cmake-package))
