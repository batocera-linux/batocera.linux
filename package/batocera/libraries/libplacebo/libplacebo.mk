################################################################################
#
# libplacebo
#
################################################################################

LIBPLACEBO_VERSION = v7.349.0
LIBPLACEBO_SITE = https://github.com/haasn/libplacebo
LIBPLACEBO_SITE_METHOD = git
LIBPLACEBO_GIT_SUBMODULES = YES
LIBPLACEBO_LICENSE = LGPL-2.1
LIBPLACEBO_LICENSE_FILES = LICENSE
LIBPLACEBO_INSTALL_STAGING = YES

LIBPLACEBO_CONF_OPTS = -Ddemos=false

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
LIBPLACEBO_CONF_OPTS += -Dvulkan=enabled
LIBPLACEBO_DEPENDENCIES += vulkan-headers vulkan-loader
else
LIBPLACEBO_CONF_OPTS += -Dvulkan=disabled
endif

ifeq ($(BR2_PACKAGE_GLSLANG),y)
LIBPLACEBO_CONF_OPTS += -Dglslang=enabled
LIBPLACEBO_DEPENDENCIES += glslang
LIBPLACEBO_LDFLAGS = -lglslang
else
LIBPLACEBO_CONF_OPTS += -Dglslang=disabled
endif

ifeq ($(BR2_PACKAGE_SHADERC),y)
LIBPLACEBO_CONF_OPTS += -Dshaderc=enabled
LIBPLACEBO_DEPENDENCIES += shaderc
else
LIBPLACEBO_CONF_OPTS += -Dshaderc=disabled
endif

$(eval $(meson-package))
