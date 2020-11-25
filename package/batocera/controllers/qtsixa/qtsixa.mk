################################################################################
#
# qtsixa
#
################################################################################
QTSIXA_VERSION = gasia
QTSIXA_SITE = $(call github,batocera-linux,qtsixa,$(QTSIXA_VERSION))
QTSIXA_DEPENDENCIES = linux-headers libusb-compat bluez5_utils
PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig

QTSIXA_INCLUDES =-I$(STAGING_DIR)/usr/include
QTSIXA_CFLAGS = -D__ARM_PCS_VFP -DARM_ARCH -Wall $(QTSIXA_INCLUDES)
QTSIXA_LIBS = -ldl -lpthread -lz -L$(STAGING_DIR)/usr/lib -lrt -lusb -lbluetooth

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	QTSIXA_DEPENDENCIES += rpi-userland
	QTSIXA_INCLUDES +=-I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux
	QTSIXA_CFLAGS += -DRPI_BUILD
	QTSIXA_LIBS += -lbcm_host -lvcos -lvchiq_arm -lvchostif
endif

define QTSIXA_BUILD_CMDS
	$(MAKE) CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS) $(QTSIXA_CFLAGS)" \
		LIBS="$(QTSIXA_LIBS)" \
		-C $(@D)/utils all
	# Make standard
	$(SED) "s|/usr/.\+\?/sixad-remote|/usr/sixad/official/sixad-remote|g" $(@D)/sixad/bluetooth.cpp
	$(SED) "s|/usr/.\+\?/sixad-sixaxis|/usr/sixad/official/sixad-sixaxis|g" $(@D)/sixad/bluetooth.cpp

	$(MAKE) CXX="$(TARGET_CXX)" \
		CXXFLAGS="$(TARGET_CFLAGS) $(QTSIXA_CFLAGS)" \
		LIBS="$(QTSIXA_LIBS)" INSTALLDIR="official" BINDIR="official"\
		-C $(@D)/sixad all
endef

define QTSIXA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/utils/bins/sixpair \
		$(TARGET_DIR)/usr/bin/sixpair
	$(INSTALL) -D $(@D)/utils/bins/sixpair-kbd \
		$(TARGET_DIR)/usr/bin/sixpair-kbd
	$(MAKE) INSTALLDIR="official" BINDIR="official" DESTDIR=$(TARGET_DIR) -C $(@D)/sixad install
endef

define QTSIXA_RPI_FIXUP
	$(SED) 's|WANT_JACK = true|WANT_JACK = false|g' $(@D)/utils/Makefile
	$(SED) 's|`pkg-config --cflags --libs libusb`| $(QTSIXA_LIBS) |g' $(@D)/utils/Makefile
	$(SED) 's|`pkg-config --cflags --libs bluez`| $(QTSIXA_INCLUDES) $(QTSIXA_LIBS) |g' $(@D)/sixad/Makefile
endef

QTSIXA_PRE_CONFIGURE_HOOKS += QTSIXA_RPI_FIXUP

$(eval $(generic-package))
