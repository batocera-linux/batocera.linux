################################################################################
#
# openmsx
#
################################################################################

OPENMSX_VERSION = RELEASE_19_1
OPENMSX_SITE = $(call github,openMSX,openMSX,$(OPENMSX_VERSION))
OPENMSX_LICENSE = GPLv2
OPENMSX_DEPENDENCIES = zlib sdl2 sdl2_ttf libpng tcl freetype

OPENMSX_CONF_ENV += $(TARGET_CONFIGURE_OPTS) \
                CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
                CC_FOR_BUILD="$(TARGET_CC)" GCC_FOR_BUILD="$(TARGET_CC)" \
                CXX_FOR_BUILD="$(TARGET_CXX)" \
                CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
                PREFIX="$(STAGING_DIR)" \
                PKG_CONFIG="$(STAGING_DIR)/usr/bin/pkg-config" \
                PATH="$(HOST_DIR)/bin:$(HOST_DIR)/sbin:$(PATH):$(STAGING_DIR)/usr/bin" \
                TCL_CONFIG="$(STAGING_DIR)/usr/lib" LD_FOR_BUILD="$(TARGET_CROSS)ld"

# additional config options
#linux
ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
OPENMSX_CONF_OPTS += -Dalsamidi=enabled
OPENMSX_DEPENDENCIES += alsa-lib
else
OPENMSX_CONF_OPTS += -Dalsamidi=disabled
endif
#glrenderer
ifeq ($(BR2_PACKAGE_LIBGLEW),y)
OPENMSX_CONF_OPTS += -Dglrenderer=enabled
OPENMSX_DEPENDENCIES += libglew
else
OPENMSX_CONF_OPTS += -Dglrenderer=disabled
endif
#laserdisc
ifeq ($(BR2_PACKAGE_LIBOGG)$(BR2_PACKAGE_LIBTHEORA)$(BR2_PACKAGE_LIBVORBIS),yyy)
OPENMSX_CONF_OPTS += -Dlaserdisc=enabled
OPENMSX_DEPENDENCIES += libogg libtheora libvorbis
else
OPENMSX_CONF_OPTS += -Dlaserdisc=disabled
endif

#fix tclConfig.sh paths!
define OPENMSX_TCL_CONFIG_FIXUP
    cp $(STAGING_DIR)/usr/lib/tclConfig.sh $(STAGING_DIR)/usr/lib/tclConfig.sh.bak
    sed -i "s@TCL_LIB_SPEC='-L/usr/lib -ltcl8.6'@TCL_LIB_SPEC='-L$(STAGING_DIR)/usr/lib -ltcl8.6'@" \
        $(STAGING_DIR)/usr/lib/tclConfig.sh
    sed -i "s@TCL_INCLUDE_SPEC='-I/usr/include'@TCL_INCLUDE_SPEC='-I$(STAGING_DIR)/usr/include'@" \
        $(STAGING_DIR)/usr/lib/tclConfig.sh
endef

#change the appropriate directories & then compile & install.
define OPENMSX_BUILD_CMDS
    sed -i 's@SYMLINK_FOR_BINARY:=true@SYMLINK_FOR_BINARY:=false@' $(@D)/build/custom.mk
    sed -i 's@INSTALL_BASE:=/opt/openMSX@INSTALL_BASE:=$(TARGET_DIR)/usr/share/openmsx@' $(@D)/build/custom.mk
    echo 'INSTALL_DOC_DIR:=$(TARGET_DIR)/usr/share/doc/openmsx' >> $(@D)/build/custom.mk
    echo 'INSTALL_SHARE_DIR:=$(TARGET_DIR)/usr/share/openmsx' >> $(@D)/build/custom.mk
    echo 'INSTALL_BINARY_DIR:=$(TARGET_DIR)/usr/bin' >> $(@D)/build/custom.mk
    $(OPENMSX_CONF_ENV) $(MAKE) -C $(@D) install
endef

define OPENMSX_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/openmsx/*.keys \
        $(TARGET_DIR)/usr/share/evmapy/
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/openmsx/settings.xml \
        $(TARGET_DIR)/usr/share/openmsx
endef

define OPENMSX_POST_INSTALL_CLEANUP
    mv -f $(STAGING_DIR)/usr/lib/tclConfig.sh.bak $(STAGING_DIR)/usr/lib/tclConfig.sh
endef

OPENMSX_PRE_CONFIGURE_HOOKS += OPENMSX_TCL_CONFIG_FIXUP

OPENMSX_POST_INSTALL_TARGET_HOOKS += OPENMSX_POST_INSTALL_CLEANUP

$(eval $(autotools-package))
