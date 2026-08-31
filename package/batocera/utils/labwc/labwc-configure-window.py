#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import argparse
import sys
import subprocess

def remove_action(rule_elem, action_name):
    """Removes a specific action element from a window rule if it exists."""
    for action in rule_elem.findall("action"):
        if action.get("name", "") == action_name:
            rule_elem.remove(action)
            return True # Action found and removed
    return False # Action was not present

# value is     set and child_name is not set : set the text
# value is     set and child_name is     set : set the text in the child
# value is not set and child_name is not set : create the node
# value is not set and child_name is     set : create the child node
def set_action(rule_elem, action_name, value=None, child_name=None):
    """Adds, updates, or removes an action element within a window rule."""
    modified = False

    # Find existing action
    action_elem = None
    for action in rule_elem.findall("action"):
        if action.get("name", "") == action_name:
            action_elem = action
            break

    # Create the action element if missing
    if action_elem is None:
        action_elem = ET.SubElement(rule_elem, "action")
        modified = True

    # Find existing child
    child_elem = None
    if child_name is not None:
        for child in action_elem.findall(child_name):
            child_elem = child
            break

    # Create the child element if missing
    if child_name is not None:
        if child_elem is None:
            child_elem = ET.SubElement(action_elem, child_name)
            modified = True

    action_elem.set("name", action_name)
    if value is not None:
        if child_elem is None:
            action_elem.text = str(value)
            modified = True
        else:
            child_elem.text = str(value)
            modified = True

    return modified

def configure_window_rule(
    xmlroot,
    identifier=None,
    title=None,
    output=None,
    toggle_fullscreen=None,
):
    """Updates an existing labwc window rule or creates a new one if not found."""

    # Ensure <windowRules> exists
    window_rules = xmlroot.find("windowRules")
    if window_rules is None:
        window_rules = ET.SubElement(xmlroot, "windowRules")

    # Locate matching windowRule (by identifier/title)
    target_rule = None
    for rule in window_rules.findall("windowRule"):
        match_id = identifier and rule.get("identifier") == identifier
        match_title = title and rule.get("title") == title

        # the couple identifier/title must match
        if identifier is not None and title is None and match_id:
            target_rule = rule
            break
        if identifier is None and title is not None and match_title:
            target_rule = rule
            break
        if identifier is not None and title is not None and match_id and match_title:
            target_rule = rule
            break

    # Create a new rule if no match is found
    if target_rule is None:
        target_rule = ET.SubElement(window_rules, "windowRule")
        if identifier:
            target_rule.set("identifier", identifier)
        if title:
            target_rule.set("title", title)

    # Update identifier/title attributes on match
    if identifier:
        target_rule.set("identifier", identifier)
    if title:
        target_rule.set("title", title)

    # example of rule
    #<windowRule identifier="net.kuribo64.melonDS" title="*w2*">
    #  <action name="MoveToOutput"><output>HDMI1</output></action>
    #  <action name="ToggleFullscreen" />
    #</windowRule>

    # Apply actions based on provided parameters
    save_required = False
    # MoveToOutput
    if output is not None:
        if output == "None":
            if remove_action(target_rule, "MoveToOutput"):
                save_required = True
        else:
            if set_action(target_rule, "MoveToOutput", output, "output"):
                save_required = True

    # ToggleFullscreen
    if toggle_fullscreen is not None:
        if toggle_fullscreen == "true":
            if set_action(target_rule, "ToggleFullscreen"):
                save_required = True
        else:
            if remove_action(target_rule, "ToggleFullscreen"):
                save_required = True

    return save_required

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-path", default="/userdata/system/.config/labwc/rc.xml", help="path to rc.xml")
    parser.add_argument("--identifier", help="window id")
    parser.add_argument("--title", help="window title")
    parser.add_argument("--output", default=None, help="output screen")
    parser.add_argument("--toggle-fullscreen", default=None, help="set to fullscreen (true/false)")
    args = parser.parse_args()

    if not args.identifier and not args.title:
        parser.error("Error : --identifier or --title must be specified")

    try:
        tree = ET.parse(args.config_path)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"Error :file {args.config_path} not found.", file=sys.stderr)
        sys.exit(1)
    except ET.ParseError:
        print(f"Error : invalid file {args.config_path}.", file=sys.stderr)
        sys.exit(1)

    if configure_window_rule(
            root,
            identifier=args.identifier,
            title=args.title,
            output=args.output,
            toggle_fullscreen=args.toggle_fullscreen
    ):
        ET.indent(tree, space="  ")
        tree.write(args.config_path, encoding="UTF-8", xml_declaration=True, short_empty_elements=True)

        res = subprocess.run(["/usr/bin/labwc", "--reconfigure"])
        if res.returncode != 0:
            print(f"Error : labwc reconfigure failed", file=sys.stderr)

if __name__ == "__main__":
    main()
