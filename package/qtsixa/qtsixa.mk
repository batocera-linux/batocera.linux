################################################################################
#
# qtsixa
#
################################################################################
QTSIXA_VERSION = master
QTSIXA_SITE = $(call github,yarick123,qtsixa,$(QTSIXA_VERSION))
QTSIXA_DEPENDENCIES = sdl linux-headers
PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig

QTSIXA_INCLUDES =-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux
QTSIXA_CFLAGS = -D__ARM_PCS_VFP -DARM_ARCH -DRPI_BUILD -Wall $(QTSIXA_INCLUDES) 

ifeq ($(BR2_PACKAGE_QTSIXA_GASIA),y)
	QTSIXA_CFLAGS += -DGASIA_GAMEPAD_HACKS
endif

ifeq ($(BR2_PACKAGE_QTSIXA_SHANWAN),y)
	QTSIXA_CFLAGS += -DSHANWAN_FAKE_DS3
endif
	
QTSIXA_LIBS = -ldl -lpthread -lz -L$(STAGING_DIR)/usr/lib -lbcm_host -lvcos -lvchiq_arm -lrt -lvchostif -lusb -lbluetooth

define QTSIXA_BUILD_CMDS
	$(MAKE) CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS) $(QTSIXA_CFLAGS)" \
		LIBS="$(QTSIXA_LIBS)" \
		-C $(@D)/utils all
	$(MAKE) CXX="$(TARGET_CXX)" \
		CXXFLAGS="$(TARGET_CFLAGS) $(QTSIXA_CFLAGS)" \
		LIBS="$(QTSIXA_LIBS)" \
		-C $(@D)/sixad all
endef

define QTSIXA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/utils/bins/sixpair \
		$(TARGET_DIR)/usr/bin/sixpair
	$(INSTALL) -d $(TARGET_DIR)/etc/init.d/
	$(INSTALL) -m 755 $(@D)/sixad/sixad $(TARGET_DIR)/usr/bin/
	$(INSTALL) -m 755 $(@D)/sixad/bins/sixad-bin $(TARGET_DIR)/usr/sbin/
	$(INSTALL) -m 755 $(@D)/sixad/bins/sixad-sixaxis $(TARGET_DIR)/usr/sbin/
	$(INSTALL) -m 755 $(@D)/sixad/bins/sixad-remote $(TARGET_DIR)/usr/sbin/
	$(INSTALL) -m 755 $(@D)/sixad/bins/sixad-3in1 $(TARGET_DIR)/usr/sbin/
	$(INSTALL) -m 755 $(@D)/sixad/bins/sixad-raw $(TARGET_DIR)/usr/sbin/
endef

define QTSIXA_RPI_FIXUP
	$(SED) 's|WANT_JACK = true|WANT_JACK = false|g' $(@D)/utils/Makefile
	$(SED) 's|`pkg-config --cflags --libs libusb`| $(QTSIXA_LIBS) |g' $(@D)/utils/Makefile
	$(SED) 's|`pkg-config --cflags --libs bluez`| $(QTSIXA_INCLUDES) $(QTSIXA_LIBS) |g' $(@D)/sixad/Makefile
endef

QTSIXA_PRE_CONFIGURE_HOOKS += QTSIXA_RPI_FIXUP

$(eval $(generic-package))
