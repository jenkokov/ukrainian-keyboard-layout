# Roadmap

Phases 1–3 are done: the repo builds a valid bundle from source, publishes it on a
tag, and generates its own layout diagrams from the `.keylayout`. Everything still
unticked below is deferred work, roughly in the order it makes sense to do.

## Phase 2 — the layout changes

The point of the fork. `src/Ukrainian - Mac PC.keylayout` is currently
byte-identical to upstream except the `<keyboard>` identity line.

- [x] Apply the mapping changes
- [ ] Test each change locally (`./scripts/install-local.sh`, log out, log back in)
- [x] Record what changed and why in `CHANGELOG.md` — for a keyboard layout the
      "why" is the part nobody can reconstruct from a diff of key codes
- [ ] Tag `v1.0.0` once the mappings settle

Worth deciding early: does this layout stay a strict superset of upstream
"Ukrainian - PC" (safe to switch to, nothing moves), or does it move existing keys?
That answer belongs at the top of the README, because it is the first thing anyone
evaluating the layout needs to know.

## Phase 3 — images

SVG diagrams generated from the `.keylayout` itself, so they can never drift from
the source. Output goes to `docs/images/`, is committed, and CI regenerates it and
runs `git diff --exit-code` — a mapping change with a stale diagram fails the build.

- [x] `scripts/keylayout.py` — shared parser producing `{(keycode, modifiers): output}`.
      The XML 1.1 normalisation currently in `validate.py` moves here, and
      `validate.py` imports it instead.
- [x] Modifier resolution inside that parser. Do **not** hardcode "map 5 is base";
      `modifierMap` is an ordered match table and has to be evaluated as one:
      a bare token means the modifier must be down, a `?` suffix means it may be,
      an unmentioned modifier must be up, `anyShift` matches either side, and the
      first matching `keyMapSelect` in document order wins. `resolve({})` → map 5,
      `resolve({shift})` → map 1, `resolve({command})` → map 0. Unit-test this;
      everything downstream is wrong if it is wrong.
- [x] Geometry table: virtual keycode → row, column, keycap width. This is the one
      thing not derivable from the file and has to be hardcoded (`0`→A, `12`→Q,
      `49`→space). Guard it with an assertion that the base plane's upper letter row
      reads `йцукенгшщзхї`, so an off-by-one fails loudly instead of rendering a
      subtly wrong picture.
- [x] `scripts/render.py` → deterministic SVG. No timestamps, no generated IDs, so
      diffs stay readable.
- [x] Two files per diagram (light/dark), referenced from the README with
      `<picture>` and `prefers-color-scheme`. A single SVG carrying a CSS media
      query does not reliably follow the theme on GitHub.
- [x] Render both keycap styles off the same code, differing only in the keycap
      template: a combined diagram (base + shift + option on one cap) as the README
      hero, and one diagram per plane (base, shift, option, shift+option) for the
      docs, which is far more readable for the option layer.
- [x] Skip the ⌘/control planes in the docs — maps 0, 2, 7 and 8 are Latin
      passthrough and control characters, not part of the Ukrainian layout.
- [ ] A real `src/icon.icns` — currently inherited from upstream, so the layout is
      visually indistinguishable from it in the input menu. Needs to be a distinct
      1024×1024 source rendered through `iconutil`

## Phase 4 — docs

- [x] README: rewrite around the diagrams, lead with what differs from upstream
- [ ] Install section: screenshots of the System Settings flow, which is the step
      people actually get stuck on
- [x] Uninstall instructions (remove the bundle, log out; the input source also has
      to be removed in System Settings or it lingers as a ghost entry)
- [x] Troubleshooting: layout not appearing after install is nearly always a missed
      logout, or two layouts sharing a bundle ID
- [ ] `CONTRIBUTING.md` if this goes beyond personal use

## Phase 5 — distribution, if it's ever worth it

Deliberately skipped for now; a zip that unpacks into `~/Library/Keyboard Layouts`
is the whole install.

- [ ] Homebrew cask — the natural next step, and it needs no Apple developer account
- [ ] `.pkg` installer — only worth it with a Developer ID certificate, since an
      unsigned pkg gets a worse Gatekeeper experience than the plain zip
- [ ] Ukrainian-language README

## Decided against

**Simplifying the `modifierMap`.** Map 7 selects on 19 alternative `<modifier>`
patterns, which looks like cruft. It is: the file was produced by `kluchrtoxml`
from a binary `uchr` resource, where the modifier map is a flat 256-entry table,
and the converter re-compresses that table non-minimally. Map 7 covers the largest
region (181 of 256 states) so it fragmented the most.

Collapsing it to a single `anyShift? caps? anyOption? command? anyControl` pattern
moved after maps 8 and 9 takes the file from 35 patterns to 17 and changes the
outcome of exactly one modifier state — every modifier held at once, which today
matches nothing and falls through to `defaultIndex=5`.

Not doing it anyway. That equivalence check is a proof about a reimplementation of
the matching rules, not about what macOS does; the current file came out of Apple's
own converter and works. There is no functional gain — `modifierMap` is untouched
when remapping keys — and the failure mode is invisible until a logout, in modifier
combinations nobody exercises deliberately.

**Rendering a diff against upstream.** Considered tinting keys that differ from
"Ukrainian - PC"; not wanted.

**Generating the `.keylayout` from a compact source.** A YAML/TSV of ~47 keys × 4
planes would be nicer to edit than 1070 lines of XML, but the generator would have
to reproduce the Latin ⌘-maps (0, 2, 8) and the control-character map (7) exactly,
and the file would stop opening in Ukelele. The XML stays canonical; only docs are
generated.

## Known deferrals

- The bundle is unsigned. Keyboard layout bundles are not subject to Gatekeeper the
  way apps are, so this is not currently a problem — revisit only if a `.pkg` ships.
- `scripts/validate.py` checks structure, not semantics. It cannot tell you a key
  produces the wrong letter; only that the file is well-formed and internally
  consistent. Semantic checking would mean a table of expected outputs per key code
  per modifier state — worth building if the mappings churn a lot.
