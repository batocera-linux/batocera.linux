#!/bin/bash

BR_LAST_MERGE_COMMIT=198bdaadd03f75fe959c21089c354d36c90069bc
git diff --name-only $BR_LAST_MERGE_COMMIT > buildroot.batocera.diff

cat buildroot.batocera.diff                              |
    grep -vE '^board/batocera/'                          | # batocera board
    grep -vE '^configs/batocera-'                        | # batocera defconfig
    grep -vE '^scripts/linux'                            | # batocera utilities
    grep -vE '^package/batocera/'                        | # batocera packages
    grep -vE '^\.gitignore$'
