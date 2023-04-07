################################################################################
#
# batocera-llvm-cmake
#
################################################################################

BATOCERA_LLVM_CMAKE_VERSION = $(BATOCERA_LLVM_PROJECT_VERSION)
BATOCERA_LLVM_CMAKE_SITE = $(BATOCERA_LLVM_PROJECT_SITE)
BATOCERA_LLVM_CMAKE_SOURCE = cmake-$(BATOCERA_LLVM_CMAKE_VERSION).src.tar.xz
BATOCERA_LLVM_CMAKE_LICENSE = Apache-2.0 with exceptions

define HOST_BATOCERA_LLVM_CMAKE_INSTALL_CMDS
	mkdir -p $(HOST_DIR)/lib/cmake/llvm
	cp -Rv $(@D)/Modules/* $(HOST_DIR)/lib/cmake/llvm
endef

$(eval $(host-generic-package))

