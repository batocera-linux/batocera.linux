#!/bin/sh

BNAME=$1

FBOARD="${BNAME}.board"

if ! test -e "${FBOARD}"
then
    echo "file ${FBOARD} not found" >&2
    exit 1
fi

TMPL0="${BNAME}_defconfig.tmpl0"
TMPL1="${BNAME}_defconfig.tmpl1"
CONFDIR=$(dirname "${FBOARD}")
FDEFCONFIG="${BNAME}_defconfig"

> "${TMPL0}" || exit 1 # level 0
> "${TMPL1}" || exit 1 # level 1 (includes of includes)

# For untracked local changes
touch -a "${CONFDIR}/batocera-board.local.common"

grep -E 'include ' "${FBOARD}" | while read INC X
do
    echo "# from file ${X}" >> "${TMPL0}"
    cat "${CONFDIR}/${X}"   >> "${TMPL0}"
    echo                    >> "${TMPL0}"
done

grep -E 'include ' "${TMPL0}" | while read INC X
do
    echo "# from file ${X}" >> "${TMPL1}"
    cat "${CONFDIR}/${X}"   >> "${TMPL1}"
    echo                    >> "${TMPL1}"
done

> "${FDEFCONFIG}" || exit 1
grep -vE '^include ' "${TMPL1}" >> "${FDEFCONFIG}"
grep -vE '^include ' "${TMPL0}" >> "${FDEFCONFIG}"

rm -f "${TMPL1}" || exit 1
rm -f "${TMPL0}" || exit 1

echo "### from board file ###"   >> "${FDEFCONFIG}" || exit 1
grep -vE '^include ' "${FBOARD}" >> "${FDEFCONFIG}" || exit 1

exit 0
