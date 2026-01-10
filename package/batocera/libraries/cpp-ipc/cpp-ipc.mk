################################################################################
#
# cpp-ipc
#
################################################################################

CPP_IPC_VERSION = 006a46e09fd3b33245e406e00d674fe3017fc4ef
CPP_IPC_SITE = $(call github,mutouyun,cpp-ipc,$(CPP_IPC_VERSION))
CPP_IPC_LICENSE_FILES = LICENSE
CPP_IPC_SUPPORTS_IN_SOURCE_BUILD = NO
CPP_IPC_INSTALL_STAGING = YES
CPP_IPC_INSTALL_TARGET = NO

CPP_IPC_DEPENDENCIES = 

$(eval $(cmake-package))
