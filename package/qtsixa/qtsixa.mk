################################################################################
#
# qtsixa
#
################################################################################
QTSIXA_VERSION = ceef35906f4c894ee0b5b0b3994b956d1f1f643c
QTSIXA_SITE = $(call github,yarick123,qtsixa,$(QTSIXA_VERSION))
QTSIXA_DEPENDENCIES = sdl linux-headers
PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig

QTSIXA_INCLUDES =-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux
QTSIXA_CFLAGS = -D__ARM_PCS_VFP -DARM_ARCH -DRPI_BUILD -Wall $(QTSIXA_INCLUDES) 

	
QTSIXA_LIBS = -ldl -lpthread -lz -L$(STAGING_DIR)/usr/lib -lbcm_host -lvcos -lvchiq_arm -lrt -lvchostif -lusb -lbluetooth

define QTSIXA_BUILD_CMDS
	$(MAKE) CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS) $(QTSIXA_CFLAGS)" \
		LIBS="$(QTSIXA_LIBS)" \
		-C $(@D)/utils all
	# Make standard
	$(MAKE) CXX="$(TARGET_CXX)" \
		CXXFLAGS="$(TARGET_CFLAGS) $(QTSIXA_CFLAGS)" \
		LIBS="$(QTSIXA_LIBS)" INSTALLDIR="official" BINDIR="official"\
		-C $(@D)/sixad all
	# Make GASIA
	$(MAKE) CXX="$(TARGET_CXX)" \
		CXXFLAGS="$(TARGET_CFLAGS) $(QTSIXA_CFLAGS) -DGASIA_GAMEPAD_HACKS" \
		LIBS="$(QTSIXA_LIBS)" INSTALLDIR="gasia" BINDIR="gasia"\
		-C $(@D)/sixad all
	# Make SHANWAN
	$(MAKE) CXX="$(TARGET_CXX)" \
		CXXFLAGS="$(TARGET_CFLAGS) $(QTSIXA_CFLAGS) -DSHANWAN_FAKE_DS3" \
		LIBS="$(QTSIXA_LIBS)" INSTALLDIR="shanwan" BINDIR="shanwan"\
		-C $(@D)/sixad all
endef

define QTSIXA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/utils/bins/sixpair \
		$(TARGET_DIR)/usr/bin/sixpair
	$(MAKE) INSTALLDIR="official" BINDIR="official" DESTDIR=$(TARGET_DIR) -C $(@D)/sixad install 
	$(MAKE) INSTALLDIR="gasia" BINDIR="gasia" DESTDIR=$(TARGET_DIR) -C $(@D)/sixad install 
	$(MAKE) INSTALLDIR="shanwan" BINDIR="shanwan" DESTDIR=$(TARGET_DIR) -C $(@D)/sixad install 
endef

define QTSIXA_RPI_FIXUP
	$(SED) 's|WANT_JACK = true|WANT_JACK = false|g' $(@D)/utils/Makefile
	$(SED) 's|`pkg-config --cflags --libs libusb`| $(QTSIXA_LIBS) |g' $(@D)/utils/Makefile
	$(SED) 's|`pkg-config --cflags --libs bluez`| $(QTSIXA_INCLUDES) $(QTSIXA_LIBS) |g' $(@D)/sixad/Makefile
endef

QTSIXA_PRE_CONFIGURE_HOOKS += QTSIXA_RPI_FIXUP

$(eval $(generic-package))
