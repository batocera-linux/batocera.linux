################################################################################
#
# python-es-scraper
#
################################################################################

PYTHON_ES_SCRAPER_VERSION = 58d0fdac534472c31c6223e3c9353aa16ed9fd07
PYTHON_ES_SCRAPER_SITE = $(call github,digitallumberjack,ES-scraper,$(PYTHON_ES_SCRAPER_VERSION))

PYTHON_ES_SCRAPER_LICENSE = MIT
PYTHON_ES_SCRAPER_LICENSE_FILES = LICENSE.txt
PYTHON_ES_SCRAPER_SETUP_TYPE = distutils

$(eval $(python-package))
