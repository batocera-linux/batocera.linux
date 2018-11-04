################################################################################
#
# QT5GAMEPAD
#
################################################################################

QT5GAMEPAD_VERSION = 5.11.2
QT5GAMEPAD_SITE =  https://download.qt.io/official_releases/qt/5.11/5.11.2/submodules/
QT5GAMEPAD_SOURCE = qtgamepad-everywhere-src-$(QT5GAMEPAD_VERSION).tar.xz
QT5GAMEPAD_DEPENDENCIES = qt5base
QT5GAMEPAD_INSTALL_STAGING = YES

define QT5GAMEPAD_CONFIGURE_CMDS
	-[ -f $(@D)/Makefile ] && $(MAKE) -C $(@D) distclean
	#A dirty hack to appease qmake (so it will run syncqt)
	touch $(@D)/.git
	#run qmake
	(cd $(@D) && $(HOST_DIR)/usr/bin/qmake )
endef

define QT5GAMEPAD_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)
endef

define QT5GAMEPAD_INSTALL_STAGING_CMDS
	$(MAKE) -C $(@D) install
endef

define QT5GAMEPAD_INSTALL_TARGET_CMDS
	cp -dpf $(STAGING_DIR)/usr/lib/libQt5Gamepad*.so.* $(TARGET_DIR)/usr/lib
endef

define QT5GAMEPAD_UNINSTALL_TARGET_CMDS
	-rm $(TARGET_DIR)/usr/lib/libQt5Gamepad*.so.*
endef

$(eval $(generic-package))