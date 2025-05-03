################################################################################
#
# munt
#
################################################################################

MUNT_VERSION = libmt32emu_2_7_2
MUNT_SITE = https://github.com/munt/munt.git
MUNT_SITE_METHOD = git

MUNT_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
MUNT_CONF_OPTS += -Dmunt_WITH_MT32EMU_QT=OFF
MUNT_CONF_OPTS += -Dmunt_WITH_MT32EMU_SMF2WAV=OFF

MUNT_INSTALL_STAGING = YES

$(eval $(cmake-package))
