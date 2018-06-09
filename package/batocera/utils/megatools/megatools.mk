################################################################################
#
# MEGATOOLS
#
################################################################################
MEGATOOLS_VERSION = 1.9.97
MEGATOOLS_SOURCE = megatools-$(MEGATOOLS_VERSION).tar.gz
MEGATOOLS_SITE = https://megatools.megous.com/builds
MEGATOOLS_LICENCE = GPLv2
MEGATOOLS_DEPENDENCIES = openssl libcurl

MEGATOOLS_CONF_OPTS = \
    --prefix=/usr

$(eval $(autotools-package))
