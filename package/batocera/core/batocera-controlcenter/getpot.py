import xml.etree.ElementTree as ET
import sys

def is_valid_element(txt):
    return "${" not in txt

def get_all_values_recurse(element, keys):
    display_value = element.get('display')
    if display_value is not None and is_valid_element(display_value) and display_value not in keys:
        keys[display_value] = {}

    for child in element:
        get_all_values_recurse(child, keys)

def get_all_values(file):
    # some hardcoded values
    keys = { "Select": {}, "Cancel": {}, "Confirm": {}, "ON": {}, "OFF": {}, "Close": {}, "Previous": {}, "Next": {} }
    tree = ET.parse(file)
    root = tree.getroot()
    get_all_values_recurse(root, keys)
    return keys

def write_pot(pot_file, keys):
    with open(pot_file, 'w') as f:

        f.write("""msgid ""
msgstr ""
"Project-Id-Version: controlcenter\\n"
"Language: fr\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=INTEGER; plural=EXPRESSION;\\n"

""")
        
        for key in sorted(keys.items()):
            f.write(f"msgid \"{key[0]}\"\n")
            f.write("msgstr \"\"\n\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("takes 2 arguments : input.xml and output.pot", file=sys.stderr)
        exit(1)
    xml_file = sys.argv[1]
    pot_file = sys.argv[2]
    keys = get_all_values(xml_file)
    write_pot(pot_file, keys)
