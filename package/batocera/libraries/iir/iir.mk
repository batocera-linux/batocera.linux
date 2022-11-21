################################################################################
#
# iir
#
################################################################################

IIR_VERSION = 1.9.3
IIR_SITE =  $(call github,berndporr,iir1,$(IIR_VERSION))
IIR_LICENSE = MIT
IIR_INSTALL_STAGING = YES

$(eval $(cmake-package))
