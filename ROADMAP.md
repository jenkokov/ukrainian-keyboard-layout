# Roadmap

Phase 1 is done: the repo builds a valid bundle from source and publishes it on a
tag. Everything below is deferred work, roughly in the order it makes sense to do.

## Phase 2 — the layout changes

The point of the fork. `src/Ukrainian - Mac PC.keylayout` is currently
byte-identical to upstream except the `<keyboard>` identity line.

- [ ] Apply the mapping changes
- [ ] Test each change locally (`./scripts/install-local.sh`, log out, log back in)
- [ ] Record what changed and why in `CHANGELOG.md` — for a keyboard layout the
      "why" is the part nobody can reconstruct from a diff of key codes
- [ ] Tag `v1.0.0` once the mappings settle

Worth deciding early: does this layout stay a strict superset of upstream
"Ukrainian - PC" (safe to switch to, nothing moves), or does it move existing keys?
That answer belongs at the top of the README, because it is the first thing anyone
evaluating the layout needs to know.

## Phase 3 — images

- [ ] Layout diagrams: one per modifier state that matters (base, shift, option,
      shift+option). Generate them from the `.keylayout` rather than drawing them,
      so they can never drift from the source — a script that walks the keyMaps and
      emits SVG, run in CI
- [ ] Wire diagram generation into `scripts/build.sh` and commit the output to
      `docs/images/`, so a mapping change and its picture land in the same commit
- [ ] A real `src/icon.icns` — currently inherited from upstream, so the layout is
      visually indistinguishable from it in the input menu. Needs to be a distinct
      1024×1024 source rendered through `iconutil`

## Phase 4 — docs

- [ ] README: rewrite around the diagrams, lead with what differs from upstream
- [ ] Install section: screenshots of the System Settings flow, which is the step
      people actually get stuck on
- [ ] Uninstall instructions (remove the bundle, log out; the input source also has
      to be removed in System Settings or it lingers as a ghost entry)
- [ ] Troubleshooting: layout not appearing after install is nearly always a missed
      logout, or two layouts sharing a bundle ID
- [ ] `CONTRIBUTING.md` if this goes beyond personal use

## Phase 5 — distribution, if it's ever worth it

Deliberately skipped for now; a zip that unpacks into `~/Library/Keyboard Layouts`
is the whole install.

- [ ] Homebrew cask — the natural next step, and it needs no Apple developer account
- [ ] `.pkg` installer — only worth it with a Developer ID certificate, since an
      unsigned pkg gets a worse Gatekeeper experience than the plain zip
- [ ] Ukrainian-language README

## Known deferrals

- The bundle is unsigned. Keyboard layout bundles are not subject to Gatekeeper the
  way apps are, so this is not currently a problem — revisit only if a `.pkg` ships.
- `scripts/validate.py` checks structure, not semantics. It cannot tell you a key
  produces the wrong letter; only that the file is well-formed and internally
  consistent. Semantic checking would mean a table of expected outputs per key code
  per modifier state — worth building if the mappings churn a lot.
