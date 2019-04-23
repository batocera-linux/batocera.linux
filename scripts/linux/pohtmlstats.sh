#!/bin/bash

print_usage() {
    echo "${1}"" <batocera-emulationstation-buildroot directory>"
}

if test $# -ne 1
then
    print_usage "${0}"
    exit 1
fi

ESDIR="${1}"
GENDATE=$(date +%D)

echo '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
echo '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr" lang="fr">'
echo '<head>'
echo '<meta http-equiv="Content-type" content="text/html; charset=utf-8" />'
echo '<title>batocera.linux translation status - '${GENDATE}'</title>'
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
    
    echo "<tr>"
    echo "<td>${POLANG}</td>"
    echo "<td>"
    echo "<div style=\"width:${PER_TRANSLATED_W}px; height:20px; background:green; float:left\"></div><div style=\"width:${PER_FUZZY_W}px; height:20px; background:orange; float:left\"></div><div style=\"width:${PER_UNTRANSLATED_W}px; height:20px; background:red; float:left\"></div>"
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
echo "Generated on ${GENDATE}"
echo '</body>'
echo '</html>'
