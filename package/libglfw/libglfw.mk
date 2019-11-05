################################################################################
#
# libglfw
#
################################################################################

LIBGLFW_VERSION = 3.3
LIBGLFW_SITE = $(call github,glfw,glfw,$(LIBGLFW_VERSION))
LIBGLFW_INSTALL_STAGING = YES
LIBGLFW_DEPENDENCIES = libgl xlib_libXcursor xlib_libXext \
	xlib_libXinerama xlib_libXrandr
LIBGLFW_LICENSE = Zlib
LIBGLFW_LICENSE_FILES = LICENSE.md

LIBGLFW_CONF_OPTS += \
	-DGLFW_BUILD_EXAMPLES=OFF \
	-DGLFW_BUILD_TESTS=OFF \
	-DGLFW_BUILD_DOCS=OFF

ifeq ($(BR2_PACKAGE_XLIB_LIBXI),y)
LIBGLFW_DEPENDENCIES += xlib_libXi
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXXF86VM),y)
LIBGLFW_DEPENDENCIES += xlib_libXxf86vm
endif

$(eval $(cmake-package))
