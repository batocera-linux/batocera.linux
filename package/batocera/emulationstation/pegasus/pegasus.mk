################################################################################
#
# Pegasus
#
################################################################################
# Version.: Commits on Nov 11, 2018 (Alpha 10)
PEGASUS_VERSION = d905e3a3aaca2f5bd5efb924da0b04ffa77c2d6f
PEGASUS_SITE = https://github.com/mmatyas/pegasus-frontend.git
PEGASUS_SITE_METHOD = git
PEGASUS_GIT_SUBMODULES = YES
PEGASUS_LICENSE = GPL3
PEGASUS_DEPENDENCIES = qt5base qt5multimedia qt5declarative qt5quickcontrols2 qt5graphicaleffects qt5tools qt5imageformats qt5svg qt5gamepad gst1-plugins-good gst1-libav gst1-plugins-base

define PEGASUS_CONFIGURE_CMDS
    (cd $(@D); $(TARGET_MAKE_ENV) $(HOST_DIR)/bin/qmake pegasus.pro)
endef

define PEGASUS_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D)
endef

define PEGASUS_INSTALL_TARGET_CMDS
    cp -r $(@D)/src/app/pegasus-fe $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
