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
echo "<a href=\"batocera_systemsReport.html\">Emulator details</a>"

echo "<h2>Translations</h2>"
echo "<table>"
echo "<tr><th>Language</th><th>Status</th><th>Translated</th><th>Fuzzy</th><th>Untranslated</th></tr>"
for POFILE in "${ESDIR}"/locale/lang/*/LC_MESSAGES/emulationstation2.po
do
    POLANG=$(echo "${POFILE}" | sed -e s+"^.*/locale/lang/\([^/]*\)/.*$"+'\1'+)
    NBFUZZY=$(msgattrib --only-fuzzy "${POFILE}" | grep -E '^msgid' | wc -l)
    test ${NBFUZZY} -gt 0 && let NBFUZZY-- # header added
    NBUNTRANSLATED=$(msgattrib --untranslated "${POFILE}" | grep -E '^msgid' | wc -l)
    test ${NBUNTRANSLATED} -gt 0 && let NBUNTRANSLATED-- # header added
    NBTRANSLATED=$(msgattrib --translated "${POFILE}" | grep -E '^msgid' | wc -l)
    test ${NBTRANSLATED} -gt 0 && let NBTRANSLATED-- # header added
    let NBTRANSLATED=$NBTRANSLATED-$NBFUZZY

    let TOTAL=$NBTRANSLATED+$NBFUZZY+$NBUNTRANSLATED
    #let PER_TRANSLATED_W=$NBTRANSLATED'*'100/$TOTAL'*'2
    let PER_FUZZY_W=$NBFUZZY'*'100/$TOTAL'*'2
    let PER_UNTRANSLATED_W=$NBUNTRANSLATED'*'100/$TOTAL'*'2
    let PER_TRANSLATED_W=200-$PER_FUZZY_W-PER_UNTRANSLATED_W
    let PER_TRANSLATED=$NBTRANSLATED'*'100/$TOTAL
    LINK="https://raw.githubusercontent.com/batocera-linux/batocera-emulationstation/master/locale/lang/${POLANG}/LC_MESSAGES/emulationstation2.po"
    
    echo "<tr>"
    echo "<td><a href=\"${LINK}\">${POLANG}</a></td>"
    echo "<td>"
    echo "<div style=\"width:${PER_TRANSLATED_W}px; height:20px; background:green; float:left\">${PER_TRANSLATED}%</div><div style=\"width:${PER_FUZZY_W}px; height:20px; background:orange; float:left\"></div><div style=\"width:${PER_UNTRANSLATED_W}px; height:20px; background:red; float:left\"></div>"
    echo "</td>"
    echo "<td>"
    test "${NBTRANSLATED}" -gt 0 && echo "${NBTRANSLATED}"
    echo "</td>"
    echo "<td>"
    test "${NBFUZZY}" -gt 0 && echo "${NBFUZZY}"
    echo "</td>"
    echo "<td>"
    test "${NBUNTRANSLATED}" -gt 0 && echo "${NBUNTRANSLATED}"
    echo "</td>"
    echo "</tr>"
done
echo '</table>'
echo "<p>If your language is not available, please translate <a href=\"https://raw.githubusercontent.com/batocera-linux/batocera-emulationstation/master/locale/emulationstation2.pot\">this file</a> and send it us.<br />You can read other translations to take them as exemple.</p>"
echo "<p><a href=\"archives\">archives</a></p>"
echo "Generated on ${GENDATE}"
echo '</body>'
echo '</html>'
