#!/usr/bin/env python3
"""Structural checks on a .keylayout file.

xmllint can't help here: .keylayout is XML 1.1 (it needs C0 control characters
in `output` attributes, which XML 1.0 forbids) and libxml2 only implements 1.0.
So we normalise the document down to something an XML 1.0 parser accepts, then
check the invariants macOS actually cares about — the ones that make a layout
silently fail to load rather than error visibly.
"""

import re
import sys
import xml.etree.ElementTree as ET

# C0 controls are legal output in XML 1.1 but unparseable as XML 1.0. Swap them
# for a placeholder before parsing; we only inspect structure, not the glyphs.
CONTROL_REF = re.compile(r"&#x00(0[0-9a-fA-F]|1[0-9a-fA-F]);")


def load(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace('<?xml version="1.1"', '<?xml version="1.0"', 1)
    text = CONTROL_REF.sub("�", text)
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text, count=1)
    return ET.fromstring(text)


def main(path):
    errors = []

    try:
        kb = load(path)
    except ET.ParseError as exc:
        print(f"{path}: not well-formed: {exc}", file=sys.stderr)
        return 1

    if kb.tag != "keyboard":
        errors.append(f"root element is <{kb.tag}>, expected <keyboard>")

    try:
        if int(kb.get("id", "0")) >= 0:
            errors.append(
                f"keyboard id={kb.get('id')} should be negative for a "
                "third-party layout, to avoid colliding with Apple's"
            )
    except ValueError:
        errors.append(f"keyboard id={kb.get('id')!r} is not an integer")

    key_map_sets = {ks.get("id"): ks for ks in kb.iter("keyMapSet")}
    modifier_maps = {mm.get("id"): mm for mm in kb.iter("modifierMap")}

    # Every <layout> has to point at a keyMapSet and a modifierMap that exist.
    for layout in kb.iter("layout"):
        if layout.get("mapSet") not in key_map_sets:
            errors.append(f"layout references missing keyMapSet {layout.get('mapSet')!r}")
        if layout.get("modifiers") not in modifier_maps:
            errors.append(f"layout references missing modifierMap {layout.get('modifiers')!r}")

    for set_id, key_map_set in key_map_sets.items():
        indices = [km.get("index") for km in key_map_set.iter("keyMap")]
        if len(indices) != len(set(indices)):
            errors.append(f"keyMapSet {set_id}: duplicate keyMap index")

        # Codes must be unique within a keyMap, or the later one silently wins.
        for key_map in key_map_set.iter("keyMap"):
            codes = [k.get("code") for k in key_map.iter("key")]
            dupes = {c for c in codes if codes.count(c) > 1}
            if dupes:
                errors.append(
                    f"keyMapSet {set_id} keyMap {key_map.get('index')}: "
                    f"duplicate key code(s) {sorted(dupes)}"
                )
            for key in key_map.iter("key"):
                if key.get("output") is None and key.get("action") is None:
                    errors.append(
                        f"keyMapSet {set_id} keyMap {key_map.get('index')} "
                        f"code {key.get('code')}: no output and no action"
                    )

    # Every index a modifierMap selects must exist in the keyMapSet it feeds.
    for layout in kb.iter("layout"):
        key_map_set = key_map_sets.get(layout.get("mapSet"))
        modifier_map = modifier_maps.get(layout.get("modifiers"))
        if key_map_set is None or modifier_map is None:
            continue
        available = {km.get("index") for km in key_map_set.iter("keyMap")}
        for select in modifier_map.iter("keyMapSelect"):
            if select.get("mapIndex") not in available:
                errors.append(
                    f"modifierMap {modifier_map.get('id')} selects mapIndex "
                    f"{select.get('mapIndex')!r}, absent from keyMapSet "
                    f"{key_map_set.get('id')}"
                )
        default = modifier_map.get("defaultIndex")
        if default is not None and default not in available:
            errors.append(
                f"modifierMap {modifier_map.get('id')} defaultIndex "
                f"{default!r} is absent from keyMapSet {key_map_set.get('id')}"
            )

    # Actions referenced by keys have to be defined, or the key does nothing.
    defined_actions = {a.get("id") for a in kb.iter("action")}
    for key in kb.iter("key"):
        action = key.get("action")
        if action is not None and action not in defined_actions:
            errors.append(f"key code {key.get('code')} uses undefined action {action!r}")

    if errors:
        for error in errors:
            print(f"{path}: {error}", file=sys.stderr)
        return 1

    key_count = sum(1 for _ in kb.iter("key"))
    map_count = sum(len(list(ks.iter("keyMap"))) for ks in key_map_sets.values())
    print(f"    valid: {map_count} keyMaps, {key_count} keys, "
          f"{len(defined_actions)} actions")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
