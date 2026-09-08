# -*- coding: utf-8 -*-
"""FIX 2 — anchor the Ceiling-Fade release on the stored ceiling, not the notes log.

Edits the calculator's fadeAdjustedTj path in place. Two changes, both additive:

  1. blendInCeiling(player) replaces the bare prospectBlend(player) call as the source of `bd`.
     prospectBlend regex-scrapes the notes field for a "blend a/b/c" line. notes is an
     append-only log, so a blend line written before a later ceiling REBUILD survives it. The
     new function tests arithmetically whether the stored ceiling actually contains that blend
     (eng.tc x eng.matur x eng.sc, with and without it) and returns 1.0 when it does not.

  2. gnReleaseCap(player) clamps the release to max(pc, eng.tc x eng.sc) x pm. This is a guard,
     not the fix: it makes the invariant "a release never exceeds the ceiling a matured prospect
     is scouted to reach" true by construction, so no future stale note can breach it again.
     Every term is load-bearing — pc sits ABOVE eng.tc for 15 players whose 19.6 ratchet banked
     production past the scouting grade (releasing risk must not subtract value), and the x pm
     is required because tjp is stored pace-adjusted rather than as raw Pure.

The default risk-adjusted view is untouched: it reads the stored tj array and never enters this
function.

    python3 apply_fade_cap.py --calc path/to/index.html            # report only
    python3 apply_fade_cap.py --calc path/to/index.html --apply    # write it
    python3 apply_fade_cap.py --calc IN --out OUT --apply          # write elsewhere
"""
import argparse, io, os, re, shutil, sys

NEW_FUNCS = '''
// ---- v50.22 FIX 2: the ceiling is the authority on its own discounts -------
// prospectBlend() reads a "blend a/b/c" line out of the notes field. notes is an APPEND-ONLY
// log: a later GL REBUILD / DERISK pass replaces the ceiling outright but does not delete the
// earlier blend line, so the regex can still find a factor that is no longer in the ceiling.
// Dividing by it over-releases the player - up to 1.85x (Travis Sykora, whose released Pure
// reached 2866 against a true ceiling of 1548). eng.tc, eng.matur and eng.sc pin down what the
// ceiling really contains, so test it instead of trusting the prose.
function blendInCeiling(player) {
  const e = player.eng || {};
  const bd = prospectBlend(player);
  if (bd >= 0.999) return 1.0;                     // nothing to divide out
  const tc = e.tc;
  if (!tc || !player.pc) return bd;                // cannot test: keep prior behaviour
  const mat = (e.matur != null && e.matur < 1) ? e.matur : 1.0;
  const sc  = (e.sc != null) ? e.sc : 1.0;
  const tol = Math.max(1, 0.01 * player.pc);
  if (Math.abs(tc * mat * sc - player.pc)      <= tol) return 1.0;   // blend ABSENT
  if (Math.abs(tc * mat * sc * bd - player.pc) <= tol) return bd;    // blend PRESENT
  return bd;                                       // neither reconciles: prior behaviour
}

// The most a release may ever reach, in the units tjp is stored in:
//     max(pc, eng.tc x eng.sc) x pm
// eng.tc x eng.sc is the ceiling a fully matured prospect is scouted to reach. pc is a FLOOR on
// the cap, because it sits above eng.tc for 15 players whose 19.6 ratchet banked production past
// the scouting grade, and releasing risk must never subtract value. The x pm is required because
// tjp is stored pace-ADJUSTED rather than as raw Pure - on the v50.21 board max(tjp) == pc x pm
// for all 373 players carrying a multiplier off 1.00 - so the cap must live in the same units as
// the quantity it bounds. Returns null when eng.tc is absent, asserting no cap.
function gnReleaseCap(player) {
  const e = player.eng || {};
  const tc = e.tc;
  if (!tc || !player.pc) return null;
  const sc = (e.sc != null) ? e.sc : 1.0;
  const pm = player.pm ? player.pm : 1.0;
  return Math.max(player.pc, tc * sc) * pm;
}
'''

# the three edit sites, each matched on text that appears exactly once
ANCHOR_FUNCS = 'function fadeAdjustedTj(player, yearIdx) {'
OLD_BD = '  const bd  = prospectBlend(player);'
NEW_BD = '  const bd  = blendInCeiling(player);      // v50.22 FIX 2: was prospectBlend(player)'
OLD_RET = ('  const fadedPure = (player.tjp[yearIdx] / bd / mat) * bdFaded * matFaded;\n'
           '  return fadedPure * hit;')
NEW_RET = ('  let fadedPure = (player.tjp[yearIdx] / bd / mat) * bdFaded * matFaded;\n'
           '  const relCap = gnReleaseCap(player);   // v50.22 FIX 2: hard release cap\n'
           '  if (relCap != null && fadedPure > relCap) fadedPure = relCap;\n'
           '  return fadedPure * hit;')
MARK = 'v50.22 FIX 2'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--calc', required=True, help='calculator index.html to patch')
    ap.add_argument('--out', help='write here instead of in place')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    src = io.open(a.calc, encoding='utf-8').read()
    print('FIX 2 — ceiling-fade release cap')
    print('  source: %s  (%.1f MB)' % (a.calc, len(src) / 1048576.0))

    if MARK in src:
        sys.exit('  already patched (found the %r marker) — nothing to do' % MARK)

    problems = []
    for label, needle in (('fadeAdjustedTj definition', ANCHOR_FUNCS),
                          ('the prospectBlend call', OLD_BD),
                          ('the fadedPure return', OLD_RET)):
        n = src.count(needle)
        print('  %-28s found %d time(s)' % (label, n))
        if n != 1:
            problems.append('%s appears %d times, expected exactly 1' % (label, n))
    for fn in ('function prospectBlend', 'function healthyBaseJS', 'GN_LADDER'):
        if fn not in src:
            problems.append('missing prerequisite: %s' % fn)
    if problems:
        for p in problems: print('  BLOCKED: %s' % p)
        sys.exit(1)

    out = src.replace(ANCHOR_FUNCS, NEW_FUNCS.strip() + '\n\n' + ANCHOR_FUNCS, 1)
    out = out.replace(OLD_BD, NEW_BD, 1)
    out = out.replace(OLD_RET, NEW_RET, 1)

    for fn in ('function blendInCeiling', 'function gnReleaseCap',
               'blendInCeiling(player)', 'gnReleaseCap(player)'):
        assert fn in out, fn
    assert out.count('prospectBlend(player)') >= 1, 'prospectBlend must still be reachable'
    print('  edits staged: +%d bytes, 3 sites' % (len(out) - len(src)))

    dst = a.out or a.calc
    if not a.apply:
        print('\n  DRY RUN — nothing written. Re-run with --apply.')
        print('  would write: %s' % dst)
        return

    if dst == a.calc:
        bak = a.calc + '.pre-fix2'
        if not os.path.exists(bak):
            shutil.copy2(a.calc, bak)
            print('  backup: %s' % os.path.basename(bak))
    with io.open(dst, 'w', encoding='utf-8') as f:
        f.write(out)
    print('  wrote %s (%.1f MB)' % (dst, os.path.getsize(dst) / 1048576.0))
    print('\n  now run:  python3 verify/verify_fade_anchor.py')


if __name__ == '__main__':
    main()
