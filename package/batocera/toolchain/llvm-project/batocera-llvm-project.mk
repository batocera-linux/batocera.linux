################################################################################
#
# batocera-llvm-project
#
################################################################################

BATOCERA_LLVM_PROJECT_VERSION_MAJOR = 17
BATOCERA_LLVM_PROJECT_VERSION = $(BATOCERA_LLVM_PROJECT_VERSION_MAJOR).0.6
BATOCERA_LLVM_PROJECT_SITE = https://github.com/llvm/llvm-project/releases/download/llvmorg-$(BATOCERA_LLVM_PROJECT_VERSION)

include $(sort $(wildcard package/batocera/toolchain/llvm-project/*/*.mk))
