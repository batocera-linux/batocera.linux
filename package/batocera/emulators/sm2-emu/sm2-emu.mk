################################################################################
#
# sm2-emu
#
################################################################################

SM2_EMU_VERSION = v0.9.4
SM2_EMU_SITE = https://github.com/dmanlfc/sm2-emu.git
SM2_EMU_SITE_METHOD = git
SM2_EMU_GIT_SUBMODULES = YES
SM2_EMU_LICENSE = BSD-3-Clause
SM2_EMU_LICENSE_FILES = LICENSE
SM2_EMU_EMULATOR_INFO = sm2-emu.emulator.yml
SM2_EMU_SUPPORTS_IN_SOURCE_BUILD = NO

SM2_EMU_DEPENDENCIES = sdl3 pugixml miniz imgui lzma-sdk host-shaderc libcurl

SM2_EMU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SM2_EMU_CONF_OPTS += -DCMAKE_PREFIX_PATH=$(STAGING_DIR)/usr
SM2_EMU_CONF_OPTS += -DSM2_BUILD_TESTS=OFF
SM2_EMU_CONF_OPTS += -DSM2_GLSLC=$(HOST_DIR)/bin/glslc
SM2_EMU_CONF_OPTS += -DSM2_LTO=ON

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
SM2_EMU_CONF_OPTS += -DSM2_BUILD_OPENGL_DESKTOP=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
SM2_EMU_CONF_OPTS += -DSM2_BUILD_OPENGL_DESKTOP=OFF -DSM2_BUILD_OPENGL_ES=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
SM2_EMU_DEPENDENCIES += vulkan-headers vulkan-loader
SM2_EMU_CONF_OPTS += -DSM2_BUILD_VULKAN=ON
else
SM2_EMU_CONF_OPTS += -DSM2_BUILD_VULKAN=OFF
endif

$(eval $(cmake-package))
$(eval $(emulator-info-package))
