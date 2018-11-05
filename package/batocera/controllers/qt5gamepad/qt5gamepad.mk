################################################################################
#
# QT5GAMEPAD
#
################################################################################

QT5GAMEPAD_VERSION = 5.11.2
QT5GAMEPAD_SITE =  https://download.qt.io/official_releases/qt/5.11/$(QT5GAMEPAD_VERSION)/submodules
QT5GAMEPAD_SOURCE = qtgamepad-everywhere-src-$(QT5GAMEPAD_VERSION).tar.xz
QT5GAMEPAD_DEPENDENCIES = qt5base
QT5GAMEPAD_INSTALL_STAGING = YES

define QT5GAMEPAD_CONFIGURE_CMDS
	-[ -f $(@D)/Makefile ] && $(MAKE) -C $(@D) distclean
	#A dirty hack to appease qmake (so it will run syncqt)
	touch $(@D)/.git
	#run qmake
	(cd $(@D); $(QT5_QMAKE))
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

$(eval $(generic-package))