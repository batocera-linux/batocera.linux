################################################################################
#
# opengl-meson-t82x
#
# openGL ES pre-compiled libraries for Mali GPUs found in Amlogic Meson SoCs.
# The libraries could be found in a Linux buildroot released by Amlogic at
# http://openlinux.amlogic.com:8000/download/ARM/filesystem/. See the opengl package.
#
################################################################################

ifeq ($(BR2_aarch64),y)
	OPENGL_MESON_T82X_VERSION = 64bit
endif

ifeq ($(BR2_arm),y)
	OPENGL_MESON_T82X_VERSION = 32bit
endif

OPENGL_MESON_T82X_SOURCE = opengl-meson-t82x-$(OPENGL_MESON_T82X_VERSION).tar.gz
OPENGL_MESON_T82X_SITE = https://github.com/suzuke/opengl-meson-t82x/archive
OPENGL_MESON_T82X_DEPENDENCIES = libhybris

OPENGL_MESON_T82X_TARGET_DIR="$(TARGET_DIR)/system"

define OPENGL_MESON_T82X_INSTALL_TARGET_CMDS
	@mkdir -p $(OPENGL_MESON_T82X_TARGET_DIR)
	@cp -r $(@D)/system/* $(OPENGL_MESON_T82X_TARGET_DIR)
endef

$(eval $(generic-package))
