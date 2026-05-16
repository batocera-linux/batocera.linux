################################################################################
#
# gamenetworkingsockets
#
################################################################################

GAMENETWORKINGSOCKETS_VERSION = v1.5.1
GAMENETWORKINGSOCKETS_SITE = https://github.com/ValveSoftware/GameNetworkingSockets
GAMENETWORKINGSOCKETS_SITE_METHOD = git
GAMENETWORKINGSOCKETS_GIT_SUBMODULES = YES
GAMENETWORKINGSOCKETS_SUPPORTS_IN_SOURCE_BUILD = NO
GAMENETWORKINGSOCKETS_LICENSE = BSD-3-Clause license
GAMENETWORKINGSOCKETS_LICENSE_FILES = LICENSE
GAMENETWORKINGSOCKETS_INSTALL_STAGING = YES

GAMENETWORKINGSOCKETS_DEPENDENCIES = openssl protobuf

GAMENETWORKINGSOCKETS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
