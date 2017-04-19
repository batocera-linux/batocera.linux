#!/bin/bash

#BR_LAST_MERGE_COMMIT=8b639c7f318aec5a18907ae11a1f13e70be7eab4
#git checkout ${BR_LAST_MERGE_COMMIT}
#git checkout -b buildroot-${BR_LAST_MERGE_COMMIT}
#git checkout master
#git diff --name-only buildroot-${BR_LAST_MERGE_COMMIT} > buildroot.batocera.diff

cat buildroot.batocera.diff                              |
    grep -vE '^board/recalbox/'                          | # batocera board
    grep -vE '^configs/batocera-'                        | # batocera defconfig
    grep -vE '^scripts/linux'                            | # batocera utilities
    grep -vE '^package/batocera/'                        | # batocera packages
    grep -vE '^\.gitignore$'
