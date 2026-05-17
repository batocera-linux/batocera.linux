################################################################################
#
# rapidyaml
#
################################################################################

RAPIDYAML_VERSION = v0.12.1
RAPIDYAML_SITE = https://github.com/biojppm/rapidyaml
RAPIDYAML_SITE_METHOD = git
RAPIDYAML_GIT_SUBMODULES = YES
RAPIDYAML_LICENSE = MIT license
RAPIDYAML_LICENSE_FILE = LICENSE.txt
RAPIDYAML_INSTALL_STAGING = YES
RAPIDYAML_INSTALL_TARGET = NO

$(eval $(cmake-package))
