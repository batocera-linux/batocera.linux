################################################################################
#
# intel-clc
#
################################################################################

INTEL_CLC_VERSION = $(MESA3D_VERSION)
INTEL_CLC_SOURCE = mesa-$(INTEL_CLC_VERSION).tar.xz
INTEL_CLC_SITE = https://archive.mesa3d.org
INTEL_CLC_LICENSE = MIT, SGI, Khronos
INTEL_CLC_LICENSE_FILES = docs/license.rst
INTEL_CLC_CPE_ID_VENDOR = mesa3d
INTEL_CLC_CPE_ID_PRODUCT = mesa

HOST_INTEL_CLC_DEPENDENCIES = \
	host-bison \
	host-flex \
	host-llvm \
	host-python-mako \
	host-expat \
	libdrm \
	host-libclc \
	host-spirv-tools \
	host-spirv-llvm-translator \
	host-zlib

HOST_INTEL_CLC_CONF_OPTS = \
	-Dgallium-omx=disabled \
	-Dpower8=disabled \
	-Dgallium-drivers="" \
	-Dvulkan-drivers="" \
	-Dglx=disabled \
	-Dplatforms="" \
	-Dintel-clc=enabled \
	-Dllvm=enabled \
	-Dinstall-intel-clc=true

INTEL_CLC_MESON_EXTRA_BINARIES += llvm-config='$(STAGING_DIR)/usr/bin/llvm-config'

$(eval $(meson-package))
$(eval $(host-meson-package))