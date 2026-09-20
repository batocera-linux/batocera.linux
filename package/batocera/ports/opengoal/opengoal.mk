################################################################################
#
# opengoal
#
################################################################################

OPENGOAL_VERSION = v0.3.6
OPENGOAL_SITE = $(call github,open-goal,jak-project,$(OPENGOAL_VERSION))
OPENGOAL_LICENSE = ISC
OPENGOAL_LICENSE_FILES = LICENSE
OPENGOAL_EMULATOR_INFO = opengoal.emulator.yml
OPENGOAL_SUPPORTS_IN_SOURCE_BUILD = NO

OPENGOAL_DEPENDENCIES = host-nasm alsa-lib libcurl mesa3d openssl pulseaudio sdl3 sqlite zlib

OPENGOAL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENGOAL_CONF_OPTS += -DSTATICALLY_LINK=ON
# the bundled SDL3 is older and built without udev, which changes how controllers enumerate
OPENGOAL_CONF_OPTS += -DUSE_SYSTEM_LIBS=ON
OPENGOAL_CONF_OPTS += -DBUILD_TESTING=OFF
OPENGOAL_CONF_OPTS += -DCODE_COVERAGE=OFF
OPENGOAL_CONF_OPTS += -DCMAKE_ASM_NASM_COMPILER=$(HOST_DIR)/bin/nasm

OPENGOAL_BUILD_OPTS = --target gk goalc extractor

define OPENGOAL_SET_BUILD_REVISION
	printf '#define BUILT_TAG "%s"\n#define BUILT_SHA ""\n' '$(OPENGOAL_VERSION)' \
		> $(@D)/common/versions/revision.h
endef

OPENGOAL_POST_CONFIGURE_HOOKS += OPENGOAL_SET_BUILD_REVISION

OPENGOAL_TARGET = $(TARGET_DIR)/usr/bin/opengoal

define OPENGOAL_INSTALL_TARGET_CMDS
	mkdir -p $(OPENGOAL_TARGET)/data/decompiler
	mkdir -p $(OPENGOAL_TARGET)/data/game/graphics/opengl_renderer

	$(INSTALL) -D -m 0755 -t $(OPENGOAL_TARGET) \
		$(@D)/buildroot-build/game/gk \
		$(@D)/buildroot-build/goalc/goalc \
		$(@D)/buildroot-build/decompiler/extractor

	cp -r $(@D)/decompiler/config $(OPENGOAL_TARGET)/data/decompiler/
	cp -r $(@D)/goal_src $(OPENGOAL_TARGET)/data/
	cp -r $(@D)/custom_assets $(OPENGOAL_TARGET)/data/
	cp -r $(@D)/game/assets $(OPENGOAL_TARGET)/data/game/
	cp -r $(@D)/game/graphics/opengl_renderer/shaders \
		$(OPENGOAL_TARGET)/data/game/graphics/opengl_renderer/
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
