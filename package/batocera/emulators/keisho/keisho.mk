################################################################################
#
# keisho
#
################################################################################

KEISHO_VERSION = v0.9.63
KEISHO_SITE = https://github.com/Keisho-Emu/Keisho.git
KEISHO_SITE_METHOD = git
KEISHO_GIT_SUBMODULES = YES
KEISHO_LICENSE = GPL-3.0+
KEISHO_LICENSE_FILES = LICENSE
KEISHO_EMULATOR_INFO = keisho.emulator.yml
KEISHO_SUPPORTS_IN_SOURCE_BUILD = NO

KEISHO_DEPENDENCIES = sdl3 pugixml miniz imgui lzma-sdk host-shaderc libcurl

KEISHO_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
KEISHO_CONF_OPTS += -DCMAKE_PREFIX_PATH=$(STAGING_DIR)/usr
KEISHO_CONF_OPTS += -DSM2_BUILD_TESTS=OFF
KEISHO_CONF_OPTS += -DSM2_GLSLC=$(HOST_DIR)/bin/glslc
KEISHO_CONF_OPTS += -DSM2_LTO=ON

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
KEISHO_CONF_OPTS += -DSM2_BUILD_OPENGL_DESKTOP=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
KEISHO_CONF_OPTS += -DSM2_BUILD_OPENGL_DESKTOP=OFF -DSM2_BUILD_OPENGL_ES=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
KEISHO_DEPENDENCIES += vulkan-headers vulkan-loader
KEISHO_CONF_OPTS += -DSM2_BUILD_VULKAN=ON
else
KEISHO_CONF_OPTS += -DSM2_BUILD_VULKAN=OFF
endif

# default saves for model2/ and model3/
define KEISHO_INSTALL_NVRAM
	mkdir -p $(TARGET_DIR)/usr/share/keisho/nvram
	$(TAR) -xJf $(KEISHO_PKGDIR)/nvram.tar.xz -C $(TARGET_DIR)/usr/share/keisho/nvram
endef

KEISHO_POST_INSTALL_TARGET_HOOKS += KEISHO_INSTALL_NVRAM

$(eval $(cmake-package))
$(eval $(emulator-info-package))
