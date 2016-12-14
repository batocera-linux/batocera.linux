#!/bin/bash

#BR_LAST_MERGE_COMMIT=8b639c7f318aec5a18907ae11a1f13e70be7eab4
#git checkout ${BR_LAST_MERGE_COMMIT}
#git checkout -b buildroot-${BR_LAST_MERGE_COMMIT}
#git checkout rb-5.0.X-recalbox.remix
#git diff --name-only buildroot-${BR_LAST_MERGE_COMMIT} > buildroot.recalbox.diff

cat buildroot.recalbox.diff                              |
    grep -vE '^board/recalbox/'                          | # recalbox board
    grep -vE '^configs/recalbox-'                        | # recalbox defconfig
    grep -vE '^scripts/linux'                            | # recalbox utilities
    grep -vE '^package/recalbox-'                        | # recalbox packages
    grep -vE '^package/.*\.patch$'                       | # custom patches, patches should be put in board/recalbox/patches
    
    # emulators
    grep -vE '^package/mupen64plus-'                     |
    grep -vE '^package/reicast/'                         |
    grep -vE '^package/retroarch/'                       |
    grep -vE '^package/libretro-'                        |
    grep -vE '^package/scummvm/'                         |
    grep -vE '^package/moonlight-embedded/'              |
    grep -vE '^package/dolphin-emu/'                     |
    grep -vE '^package/dosbox/'                          |
    grep -vE '^package/ppsspp/'                          |
    grep -vE '^package/linapple-pie/'                    |
    grep -vE '^package/pifba/'                           |

    # pads
    grep -vE '^package/xarcade2jstick/'                  |
    grep -vE '^package/xboxdrv/'                         |
    grep -vE '^package/qtsixa/'                          |
    grep -vE '^package/qtsixa-shanwan/'                  |
    grep -vE '^package/virtualgamepads/'                 |

    # kodi plugins
    grep -vE '^package/kodi-resource-language-'          |
    grep -vE '^package/kodi-plugin-video-youtube/'       |
    grep -vE '^package/kodi-plugin-video-filmon/'        |
    grep -vE '^package/kodi-script.module.t0mm0.common/' |
    grep -vE '^package/kodi-superrepo-all/'              |
    grep -vE '^package/kodi-superrepo-repositories/'     |

    # to be removed ?
    grep -vE '^package/scummvm-vanfanel/'                | # ?
    grep -vE '^package/emulation-station/'               | # ?

    # prerequisites
    grep -vE '^package/sfml/'                            | # required by dolphin

    # specific to boards
    grep -vE '^package/evwait/'                          | # odroid xu4 power button management
    grep -vE '^package/mali-450/'                        | # odroid c2 gpu
    grep -vE '^package/mali-t62x/'                       | # odroid xu4 gpu
    grep -vE '^package/mali-opengles-sdk/'               | # odroid gpu sdk
    
    # tools
    grep -vE '^package/megatools/'                       |
    grep -vE '^package/jstest2/'                         |

    cat
