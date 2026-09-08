# -*- coding: utf-8 -*-
"""Biggest player value moves, v50.20 -> v50.21 (data through Aug 30 -> data through Sep 6).

Ranked on the DYNASTY DOLLAR, which is what a manager trades on, and reported at each build's
own RAW_PER_DOLLAR (497.64 then 497.17) so each figure is what the app actually showed that week.

Every move is decomposed against the engine identity  r = pc x pm x h  — Pure Ceiling times
pace multiplier times Hit% — so the mechanism is visible rather than asserted, and the
identity is re-checked on both sides of every row.
"""
import io, json, os, re, sys

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
OLD = YEAR + 'GordoNation_Calculator_v50.20/index.html'
NEW = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
N = 5


def find_literal(s, anchor, opener):
    i = s.index(anchor); j = s.index(opener, i)
    d = 0; ins = False; esc = False
    close = ']' if opener == '[' else '}'
    for k in range(j, len(s)):
        c = s[k]
        if esc: esc = False; continue
        if c == '\\': esc = True; continue
        if c == '"': ins = not ins; continue
        if ins: continue
        if c == opener: d += 1
        elif c == close:
            d -= 1
            if d == 0: return json.loads(s[j:k + 1])
    raise ValueError(anchor)


def load(p):
    s = io.open(p, encoding='utf-8').read()
    raw = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', s).group(1))
    return {q['n']: q for q in find_literal(s, 'const PLAYERS', '[')}, raw


O, RO = load(OLD)
Nw, RN = load(NEW)
print('v50.20  RAW %.2f   %d players' % (RO, len(O)))
print('v50.21  RAW %.2f   %d players' % (RN, len(Nw)))

# the identity must hold on both sides before any of this is trustworthy
bad = 0
for src in (O, Nw):
    for q in src.values():
        if q.get('pc') and q.get('pm') and q.get('h') is not None and q.get('r') is not None:
            if abs(q['r'] - round(q['pc'] * q['pm'] * q['h'])) > 1:
                bad += 1
print('identity r == round(pc x pm x h): %s' % ('holds on every record' if not bad else '%d VIOLATIONS' % bad))
if bad:
    sys.exit('refusing to attribute moves while the identity is broken')

TAG = re.compile(r'v50\.21|Sep\s?[67]|WK22', re.I)


def mechanism(new, old):
    """Name the engine step that moved him, from the notes the refresh wrote plus the deltas."""
    note = new.get('notes') or ''
    fresh = [x.strip() for x in note.split('|') if TAG.search(x)]
    txt = ' '.join(fresh).lower()
    bits = []
    if 'ratchet re-anchored' in txt or 'ratchet fired' in txt:
        bits.append('19.6 ratchet')
    if 'phase' in txt:
        bits.append('phase promotion')
    if 'import-pace' in txt:
        bits.append('20.15 import pace')
    opm, npm = old.get('pm') or 1.0, new.get('pm') or 1.0
    oil, nil_ = str(old.get('il') or 'ACTIVE'), str(new.get('il') or 'ACTIVE')
    if abs(npm - opm) > 1e-9:
        if npm == 1.0 and nil_ not in ('ACTIVE', 'DTD') and oil in ('ACTIVE', 'DTD'):
            bits.append('13 IL short-circuit, pace penalty retired')
        elif npm == 1.0:
            bits.append('pace multiplier retired to 1.00')
        else:
            bits.append('pace gate %.3f->%.3f' % (opm, npm))
    if abs((new.get('pc') or 0) - (old.get('pc') or 0)) > 0.5 and not bits:
        bits.append('Pure Ceiling re-anchored')
    if abs((new.get('h') or 0) - (old.get('h') or 0)) > 1e-6:
        bits.append('Hit%% %.3f->%.3f' % (old.get('h') or 0, new.get('h') or 0))
    return '; '.join(bits) or 'reprice only'


rows = []
for nm, new in Nw.items():
    old = O.get(nm)
    if old is None: continue
    if new.get('r') is None or old.get('r') is None: continue
    d_old = old.get('d') if old.get('d') is not None else old['r'] / RO
    d_new = new.get('d') if new.get('d') is not None else new['r'] / RN
    rows.append({
        'n': nm, 'org': str(new.get('o') or 'FA'), 'pos': new.get('p'), 't': new.get('t'),
        'r0': old['r'], 'r1': new['r'], 'dr': new['r'] - old['r'],
        'd0': d_old, 'd1': d_new, 'dd': d_new - d_old,
        'pc0': old.get('pc'), 'pc1': new.get('pc'),
        'pm0': old.get('pm'), 'pm1': new.get('pm'),
        'h0': old.get('h'), 'h1': new.get('h'),
        'il0': str(old.get('il') or 'ACTIVE'), 'il1': str(new.get('il') or 'ACTIVE'),
        'why': mechanism(new, old)})

moved = [r for r in rows if r['dr'] != 0]
print('%d records compared, %d moved (%d up, %d down)'
      % (len(rows), len(moved), sum(1 for r in moved if r['dr'] > 0),
         sum(1 for r in moved if r['dr'] < 0)))


def rostered(r):
    return not r['org'].startswith('FA')


def show(title, sel):
    print('\n' + title)
    print('  %-22s %-24s %-4s %11s %11s %9s' % ('player', 'organisation', 'pos', 'RA', '$', 'change'))
    for r in sel:
        print('  %-22s %-24s %-4s %5d->%-5d %5.2f->%-5.2f %+8.2f'
              % (r['n'][:22], r['org'][:24], r['pos'], r['r0'], r['r1'], r['d0'], r['d1'], r['dd']))
        print('  %-22s pc %s->%s   pm %.3f->%.3f   Hit%% %.3f->%.3f   %s%s'
              % ('', r['pc0'], r['pc1'], r['pm0'] or 1, r['pm1'] or 1, r['h0'] or 0, r['h1'] or 0,
                 ('IL %s->%s   ' % (r['il0'], r['il1'])) if r['il0'] != r['il1'] else '', r['why']))


up = sorted(moved, key=lambda r: -r['dd'])
dn = sorted(moved, key=lambda r: r['dd'])
show('TOP %d VALUE INCREASES — whole board' % N, up[:N])
show('TOP %d VALUE LOSSES — whole board' % N, dn[:N])
show('TOP %d INCREASES — rostered players only' % N, [r for r in up if rostered(r)][:N])
show('TOP %d LOSSES — rostered players only' % N, [r for r in dn if rostered(r)][:N])

print('\nCONTEXT')
print('  board RA %s -> %s' % (format(sum(r['r0'] for r in rows), ',d'),
                               format(sum(r['r1'] for r in rows), ',d')))
print('  biggest single riser is %s at %+.2f; biggest faller %s at %+.2f'
      % (up[0]['n'], up[0]['dd'], dn[0]['n'], dn[0]['dd']))
il_up = [r for r in up[:20] if r['il0'] in ('ACTIVE', 'DTD') and r['il1'] not in ('ACTIVE', 'DTD')]
print('  of the twenty biggest risers, %d went ONTO an injury designation this week' % len(il_up))
if il_up:
    print('    %s' % ', '.join('%s (%s)' % (r['n'], r['il1']) for r in il_up))
