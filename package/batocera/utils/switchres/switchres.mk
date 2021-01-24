################################################################################
#
# SwitchRes
#
################################################################################

SWITCHRES_VERSION = 904763355437612644697c6a9e91eb32ef383463
SWITCHRES_SITE = $(call github,antonioginer,switchres,$(SWITCHRES_VERSION))

SWITCHRES_DEPENDENCIES = libdrm
#SWITCHRES_INSTALL_STAGING = YES

define SWITCHRES_CONFIGURE_CMDS
	# Make proper pkgconfig .pc file
	cd $(@D) && \
        $(SED) "s+@prefix@+/usr+g" \
         -e "s+@libdir@+/usr/lib+g" \
         -e "s+@includedir@+/usr/include+g" \
         $(@D)/switchres.pc.in \
	&& cp $(@D)/switchres.pc.in $(@D)/switchres.pc
endef

define SWITCHRES_BUILD_CMDS
	# Cross-compile standalone and libswitchres
	cd $(@D) && \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	PREFIX="$(STAGING_DIR)/usr" \
	DESTDIR="$(STAGING_DIR)" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) libswitchres switchres

	# Copy to staging (dirty...)
	cd $(@D) && \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	PREFIX="$(STAGING_DIR)/usr" \
	BASE_DIR="" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) install
	$(INSTALL) -D -m 0644 $(@D)/libswitchres.a $(TARGET_DIR)/usr/lib/libswitchres.a
endef

define SWITCHRES_INSTALL_TARGET_CMDS
	# Copy to target (dirty...)
	cd $(@D) && \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	PREFIX="$(TARGET_DIR)/usr" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) install
	$(INSTALL) -D -m 0755 $(@D)/switchres $(TARGET_DIR)/usr/bin/switchres
endef

$(eval $(autotools-package))
