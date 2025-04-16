################################################################################
#
# ecm
#
################################################################################

ECM_VERSION = v6.13.0
ECM_SITE =  $(call github,KDE,extra-cmake-modules,$(ECM_VERSION))
ECM_INSTALL_STAGING = YES
ECM_INSTALL_TARGET = NO

ECM_CONF_OPTS += -DBUILD_TESTING=OFF
ECM_CONF_OPTS += -DBUILD_HTML_DOCS=OFF
ECM_CONF_OPTS += -DBUILD_MAN_DOCS=OFF
ECM_CONF_OPTS += -DBUILD_QTHELP_DOCS=OFF

$(eval $(cmake-package))
