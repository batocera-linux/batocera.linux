#!/bin/bash

#BR_LAST_MERGE_COMMIT=8ce27bb9fee80a406a4199657ef90e3c315e7457
#git diff --name-only $BR_LAST_MERGE_COMMIT > buildroot.batocera.diff

cat buildroot.batocera.diff                              |
    grep -vE '^board/batocera/'                          | # batocera board
    grep -vE '^configs/batocera-'                        | # batocera defconfig
    grep -vE '^scripts/linux'                            | # batocera utilities
    grep -vE '^package/batocera/'                        | # batocera packages
    grep -vE '^\.gitignore$'
