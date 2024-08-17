################################################################################
#
# qtsixa-shanwan
#
################################################################################
QTSIXA_SHANWAN_VERSION = shanwan
QTSIXA_SHANWAN_SITE = $(call github,batocera-linux,qtsixa,$(QTSIXA_SHANWAN_VERSION))
QTSIXA_SHANWAN_DEPENDENCIES = linux-headers qtsixa libusb-compat bluez5_utils
PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig

QTSIXA_SHANWAN_INCLUDES =-I$(STAGING_DIR)/usr/include
QTSIXA_SHANWAN_CFLAGS = -D__ARM_PCS_VFP -DARM_ARCH -Wall $(QTSIXA_SHANWAN_INCLUDES)
QTSIXA_SHANWAN_LIBS = -ldl -lpthread -lz -L$(STAGING_DIR)/usr/lib -lrt -lusb -lbluetooth

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	QTSIXA_INCLUDES +=-I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux
	QTSIXA_CFLAGS += -DRPI_BUILD
	QTSIXA_LIBS += -lbcm_host -lvcos -lvchiq_arm -lvchostif
endif


define QTSIXA_SHANWAN_BUILD_CMDS
	# Make SHANWAN
	$(SED) "s|/usr/.\+\?/sixad-remote|/usr/sixad/shanwan/sixad-remote|g" $(@D)/sixad/bluetooth.cpp
	$(SED) "s|/usr/.\+\?/sixad-sixaxis|/usr/sixad/shanwan/sixad-sixaxis|g" $(@D)/sixad/bluetooth.cpp
	$(MAKE) CXX="$(TARGET_CXX)" \
		CXXFLAGS="$(TARGET_CFLAGS) $(QTSIXA_SHANWAN_CFLAGS) -DSHANWAN_FAKE_DS3" \
		LIBS="$(QTSIXA_SHANWAN_LIBS)" INSTALLDIR="shanwan" BINDIR="shanwan"\
		-C $(@D)/sixad all
endef

define QTSIXA_SHANWAN_INSTALL_TARGET_CMDS
	$(MAKE) INSTALLDIR="shanwan" BINDIR="shanwan" DESTDIR=$(TARGET_DIR) -C $(@D)/sixad install 
endef

define QTSIXA_SHANWAN_RPI_FIXUP
	$(SED) 's|WANT_JACK = true|WANT_JACK = false|g' $(@D)/utils/Makefile
	$(SED) 's|`pkg-config --cflags --libs libusb`| $(QTSIXA_SHANWAN_LIBS) |g' $(@D)/utils/Makefile
	$(SED) 's|`pkg-config --cflags --libs bluez`| $(QTSIXA_SHANWAN_INCLUDES) $(QTSIXA_SHANWAN_LIBS) |g' $(@D)/sixad/Makefile
endef

QTSIXA_SHANWAN_PRE_CONFIGURE_HOOKS += QTSIXA_SHANWAN_RPI_FIXUP

$(eval $(generic-package))
