#!/bin/bash

print_usage() {
    echo "${1}"" <buildroot directory> <board>"
}

if test $# -ne 2
then
    print_usage "${0}"
    exit 1
fi

BROUTPUTDIR="${1}"
BOARD="${2}"
ESDIR="${BROUTPUTDIR}/build/"$(ls -t "${BROUTPUTDIR}/build" | grep -E "^batocera-emulationstation-" | head -1)

GENDATE=$(date "+%Y/%m/%d %H:%m:%S")

echo '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
echo '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr" lang="fr">'
echo '<head>'
echo '<meta http-equiv="Content-type" content="text/html; charset=utf-8" />'
echo '<title>batocera.linux - '${GENDATE}'</title>'
echo '</head>'
echo "<style>
table {
  text-align: center;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #bbb;
  padding-left: 15px;
  padding-right: 15px;
}
</style>"
echo '<body>'

echo -n "<h1>"
echo -n "${BOARD} - "
cat "${BROUTPUTDIR}/images/batocera/batocera.version"
echo "</h1>"
echo "<h2>Files</h2>"
echo "<ul>"
echo "<li>""<a href=\"boot.tar.xz\">boot.tar.xz</a></li>"
ls "${BROUTPUTDIR}/images/batocera/images/${BOARD}/"*.gz |
    while read FILE
    do
	FILENAME=$(basename "${FILE}")
	echo "<li>""<a href=\"${FILENAME}\">${FILENAME}</a></li>"
    done
echo "</ul>"

echo "<h2>Emulators details</h2>"
echo "<a href=\"https://batocera.org/compatibility.php?boards=${BOARD}\">Emulator details</a>"

echo "<p><a href=\"..\">archives</a></p>"
echo "Generated on ${GENDATE}"
echo '</body>'
echo '</html>'
