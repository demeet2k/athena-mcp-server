from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio

FT = Path(__file__).resolve().parents[2]
WS = FT.parent
BOOK = next(p for p in (WS / 'NEW').iterdir() if p.name.startswith('SECTION I') and p.suffix == '.md')
RIGID = WS / 'NEW' / 'working' / 'VML_RIGOROUS_RETRANSCRIPTION_QUIRES_ABCDEFG.md'

TAROT = [
    'The Magician','The High Priestess','The Empress','The Emperor','The Hierophant','The Lovers',
    'The Chariot','Strength','The Hermit','Wheel of Fortune','Justice','The Hanged Man',
    'Temperance','The Devil','The Tower','The Star','The Moon','The Sun','Judgment','The World',
]
SIG = [
    ('cfh','fire-seal'),('qotor','retort turn'),('qot','transmuted retort'),('otor','source-heating'),
    ('tor','heated outlet'),('okam','union vessel'),('dam','fixed union'),('am','union'),('ee','essence load'),
    ('aiin','completion checkpoint'),('aiir','completion checkpoint'),('daii','completion checkpoint'),
    ('dy','fixed state'),('dal','structural fixation'),('dar','root fixation'),('rod','root fixation'),
    ('dor','outlet fixation'),('cth','conduit binding'),('ckh','valve control'),('chol','fluid carrier'),
    ('eol','fluid carrier'),('tol','fluid carrier'),('dol','fluid carrier'),('chor','volatile outlet'),
    ('shor','transition outlet'),('cho','volatile heat'),('sar','salt charge'),('sor','salt charge'),
    ('saiin','salt completion'),('sh','transition phase'),('ok','contained body'),('y','moist drive'),
]

def tarot(n):
    return [TAROT[i % len(TAROT)] for i in range(n)]

def clean(t):
    t = t.replace('**', '').replace('`', '').replace('*', '').replace('\\=', '=').replace('\\-', '-')
    t = re.sub(r'\[(.*?)\]', r'\1', t)
    return re.sub(r'\s+', ' ', t).strip(' -')

def canon(raw):
    m = re.search(r'F(\d+)([RV])', raw.upper())
    return f"F{int(m.group(1)):03d}{m.group(2)}"

def disp(fid):
    m = re.match(r'F0*(\d+)([RV])', fid)
    return f"f{m.group(1)}{m.group(2).lower()}"

def sections(text, prefix):
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith(prefix):
            if cur:
                out[cur] = '\n'.join(buf).strip() + '\n'
            m = re.search(r'F(\d+[RV])', line)
            cur = canon('F' + m.group(1)) if m else None
            buf = [line]
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = '\n'.join(buf).strip() + '\n'
    return out

def blocks(section):
    out, cur, buf = {}, '__head__', []
    for line in section.splitlines():
        if line.startswith('## ') or line.startswith('### '):
            out[cur] = '\n'.join(buf).strip('\n')
            cur, buf = line.strip(), []
        else:
            buf.append(line)
    out[cur] = '\n'.join(buf).strip('\n')
    return out

def tables(block):
    out, lines, i = [], block.splitlines(), 0
    while i < len(lines):
        if lines[i].startswith('|') and '---' not in lines[i]:
            heads = [c.strip() for c in lines[i].strip('|').split('|')]
            if i + 1 < len(lines) and lines[i + 1].startswith('|') and '---' in lines[i + 1]:
                i += 2
                rows = []
                while i < len(lines) and lines[i].startswith('|'):
                    rows.append([c.strip() for c in lines[i].strip('|').split('|')])
                    i += 1
                out.append((heads, rows))
                continue
        i += 1
    return out

def pairmap(block):
    out = {}
    for _h, rows in tables(block):
        for row in rows:
            if len(row) >= 2:
                out[clean(row[0])] = clean(row[1])
            if len(row) >= 4:
                out[clean(row[2])] = clean(row[3])
    return out

def pick(blocks_, needle):
    for h, b in blocks_.items():
        if needle.lower() in h.lower():
            return b
    return ''

def first_head(blocks_, prefix):
    for h in blocks_:
        if h.startswith(prefix):
            return clean(h.replace('##', '').replace('###', ''))
    return ''

def evablock(block):
    out, code = [], False
    for raw in block.splitlines():
        line = raw.rstrip()
        if line.strip().startswith('```'):
            code = not code
            continue
        if code or re.match(r'^[A-Z]\.?[A-Z0-9.]*:\s*', line.strip()):
            out.append(line.strip())
    return '\n'.join(out).strip()

def norm_id(raw):
    return re.sub(r'^([A-Z])\.', r'\1', raw.strip().replace(' ', ''))

def evalines(block):
    out = []
    for raw in block.splitlines():
        m = re.match(r'^([A-Z][A-Z0-9.]*)\s*:\s*(.+?)\s*$', raw.strip())
        if m:
            out.append((norm_id(m.group(1)), m.group(2).strip()))
    return out

def tokmap(block):
    out, cur, buf = {}, None, []
    for raw in block.splitlines():
        line = raw.strip()
        m = re.match(r'^\*\*([A-Z][A-Z0-9.\s?-]*)\*\*:\s*(.*)$', line)
        if m:
            if cur:
                out[cur] = clean(' '.join(buf))
            mm = re.search(r'([A-Z]\.?(?:\d+)(?:\.\d+)?)', m.group(1))
            cur = norm_id(mm.group(1)) if mm else None
            buf = [m.group(2).strip()] if cur else []
        elif cur:
            if line.startswith('---'):
                out[cur] = clean(' '.join(buf))
                cur, buf = None, []
            else:
                buf.append(line)
    if cur:
        out[cur] = clean(' '.join(buf))
    return out

def cut(text, n=320):
    text = clean(text).replace('=', '')
    return text if len(text) <= n else text[:n].rsplit(' ', 1)[0] + '...'

def phr(text, n=6):
    words = re.findall(r'[A-Za-z0-9]+', clean(text).lower())
    return ' '.join(words[:n]) if words else 'folio process'

def toks(eva):
    return [p.strip() for p in re.split(r'[.\-=]+', eva) if p.strip()]

def feats(tok):
    t = tok.lower(); out = ['damaged witness'] if '*' in t else []
    for needle, label in SIG:
        if needle in t and label not in out:
            out.append(label)
    return out or ['opaque operator']

def gloss(tok):
    return ' / '.join(feats(tok)[:4])

def literal(eva, explicit):
    return explicit if explicit else ' | '.join(f'`{tok}` = {gloss(tok)}' for tok in toks(eva)[:6])

def optext(eva, hint, explicit):
    seen = []
    for tok in toks(eva):
        for f in feats(tok):
            if f != 'opaque operator' and f not in seen:
                seen.append(f)
    acts = []
    if 'fire-seal' in seen: acts.append('admit fire under seal')
    if 'retort turn' in seen or 'transmuted retort' in seen: acts.append('retort the route')
    if 'source-heating' in seen or 'heated outlet' in seen: acts.append('heat the source corridor')
    if 'conduit binding' in seen or 'valve control' in seen: acts.append('maintain conduit and valve control')
    if 'fluid carrier' in seen: acts.append('keep the material in fluid carriage')
    if 'union' in seen or 'union vessel' in seen or 'fixed union' in seen: acts.append('bring the materials into combination')
    if 'salt charge' in seen or 'salt completion' in seen: acts.append('salt the route')
    if 'essence load' in seen: acts.append('raise the essence density')
    if not acts: acts = ['carry the local operator chain forward']
    close = 'a fixed completed state'
    if 'union' in seen or 'union vessel' in seen or 'fixed union' in seen: close = 'a vesselized union state'
    elif 'salt completion' in seen: close = 'a salted completion'
    elif 'completion checkpoint' in seen and 'fixed state' not in seen: close = 'a completed checkpoint'
    s = ', then '.join(acts[:2]) if len(acts) > 1 else acts[0]
    if explicit: return f"{s.capitalize()}, preserving the local emphasis on {phr(explicit, 10)}, and resolve the line inside {close}."
    return f"{s.capitalize()} and keep it consistent with the folio's {phr(hint, 10)} until it resolves inside {close}."

def summary(eva, explicit):
    if explicit: return phr(explicit, 5) + ' line'
    seen = []
    for tok in toks(eva):
        for f in feats(tok):
            if f != 'opaque operator' and f not in seen:
                seen.append(f)
    return (' '.join(seen[:3]) if seen else 'opaque operator') + ' line'

def conf(eva, explicit):
    if '*' in eva: return 'mixed'
    return 'strong' if explicit or len(toks(eva)) >= 4 else 'mixed'

def groups(lines):
    out, cur, idx = [], [], 1
    for lid, eva in lines:
        if lid.startswith('T') and cur:
            out.append({'label': f'P{idx}', 'title': f'Paragraph {idx} - terminal close' if out else f'Paragraph {idx} - opening span', 'line_ids': cur[:]})
            idx += 1; cur = []
            out.append({'label': lid.replace('.', '_'), 'title': 'Title line - embedded naming event', 'line_ids': [lid]})
            continue
        cur.append(lid)
        if eva.endswith('='):
            out.append({'label': f'P{idx}', 'title': f'Paragraph {idx} - opening process span' if not out else f'Paragraph {idx} - terminal consolidation', 'line_ids': cur[:]})
            idx += 1; cur = []
    if cur:
        out.append({'label': f'P{idx}', 'title': f'Paragraph {idx} - terminal consolidation' if out else f'Paragraph {idx} - full visible route', 'line_ids': cur[:]})
    return out

def counts(lines):
    c = Counter()
    for _lid, eva in lines:
        e = eva.lower()
        c['completion'] += e.count('aiin') + e.count('aiir') + e.count('daii')
        c['fire'] += e.count('cfh'); c['union'] += e.count('am'); c['essence'] += e.count('ee')
        c['salt'] += e.count('sar') + e.count('sor') + e.count('saiin'); c['damage'] += 1 if '*' in e else 0; c['units'] += 1
    return c

def confsum(block, fallback):
    ts = tables(block)
    if not ts: return fallback
    claims = [clean(r[0]) for r in ts[0][1][:2] if r]
    return fallback if not claims else 'high on ' + '; '.join(claims)

def qb(book_pairs, rigid_pairs):
    src = book_pairs.get('Quire/Bifolio', '')
    if src:
        parts = src.split('/')
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else src
    bif = rigid_pairs.get('Bifolio', 'unknown')
    m = re.match(r'b([A-Z])', bif.split('=', 1)[0].strip())
    return (m.group(1) if m else rigid_pairs.get('Currier', '?').replace('Language ', '')), bif

def core(quant_rows):
    out = []
    for row in quant_rows[:5]:
        feat = clean(row[0]); ct = clean(row[1]) if len(row) > 1 else '?'; sig = clean(row[2]) if len(row) > 2 else 'dominant feature'
        out.append(f'`{feat}` = {sig} (`count {ct}`)')
    return out

def visual(sub, book_pairs, uniq, align):
    out = []
    qb_ = book_pairs.get('Quire/Bifolio', '')
    ill = book_pairs.get('Illustration', 'herbal witness')
    if qb_: out.append(f'`{sub}` is staged at `{qb_}` and should be read as a deliberate quire-positioned operator page.')
    out.append(f'`{ill}` keeps the folio inside the Herbal witness while the language carries the stronger process load.')
    if uniq: out.append(cut(uniq, 220))
    if align: out.append(cut(align, 220))
    return out[:4]

def crystal(sub, quant_rows, proc):
    out = [phr(sub.split('?', 1)[-1], 5) + ' station']
    for row, suf in zip(quant_rows[:3], ['line', 'threshold', 'corridor']):
        out.append(phr(row[2] if len(row) > 2 else row[0], 5) + ' ' + suf)
    out.append(phr(proc.split('?')[-1], 6) + ' close')
    return out[:5]

def zclaim(proc):
    return cut(re.sub(r'^F\d+[rvRV]\s+describes\s+', '', clean(proc)), 240)

def inv(fid, c):
    return f"\\[N_{{\\mathrm{{visible\\ units}}}}({fid})={c['units']}, \\qquad N_{{\\mathrm{{completion}}}}({fid})={c['completion']}, \\qquad N_{{\\mathrm{{essence}}}}({fid})={c['essence']}\\]\n\\[N_{{\\mathrm{{fire}}}}({fid})={c['fire']}, \\qquad N_{{\\mathrm{{union}}}}({fid})={c['union']}, \\qquad N_{{\\mathrm{{salt}}}}({fid})={c['salt']}, \\qquad N_{{\\mathrm{{damage\\ lines}}}}({fid})={c['damage']}\\]"

def tsm(fid, gs):
    labels = ', '.join(f"r_{{\\mathrm{{{g['label'].lower()}}}}}" for g in gs)
    first = gs[0]['label'].lower(); last = gs[-1]['label'].lower()
    return f"\\[\\mathcal R_{{{fid}}} = \\{{{labels}\\}}\\]\n\\[\\delta(e_{{\\mathrm{{open}}}}): r_{{\\mathrm{{{first}}}}} \\to \\cdots \\to r_{{\\mathrm{{{last}}}}}\\]\n\\[\\rho_* = \\Psi_{{{gs[-1]['label']}}}(\\cdots \\Psi_{{{gs[0]['label']}}}(\\rho_0)\\cdots)\\]"

def theorem(fid, proc, quant_rows, close_id):
    dom = clean(quant_rows[0][0]) if quant_rows else 'dominant feature'
    sup = clean(quant_rows[1][0]) if len(quant_rows) > 1 else 'supporting feature'
    return f"\\[\\rho_* = (\\Psi_{{P_n}} \\circ \\cdots \\circ \\Psi_{{P_1}})(\\rho_0)\\]\n\nThe formal theorem of `{fid.lower()}` is:\n\n1. the folio is governed by {cut(proc, 120)}\n2. `{dom}` is a dominant quantitative witness rather than a decorative aside\n3. `{sup}` helps stabilize the folio's mid-route logic\n4. the visible attractor is certified by the terminal line `{close_id}`"

def build(fid, bs, rs):
    bb, rb = blocks(bs), blocks(rs)
    sub = first_head(bb, '## ')
    bp = pairmap(bb.get(f'## **{sub}**', '')) if sub else {}
    if not bp:
        for h, b in bb.items():
            if h.startswith('## **'):
                bp = pairmap(b)
                if bp: break
    rp = pairmap(pick(rb, 'Identity & Botanical'))
    botp = pairmap(pick(bb, 'BOTANICAL IDENTIFICATION'))
    qtabs = tables(pick(rb, 'Quantitative Profile'))
    qrows = qtabs[0][1] if qtabs else []
    eva = evablock(pick(bb, 'EVA TRANSCRIPTION')) or evablock(pick(rb, 'EVA Transcription'))
    elines = evalines(eva)
    tm = tokmap(pick(bb, 'TOKEN-BY-TOKEN'))
    quire, bif = qb(bp, rp)
    plant = botp.get('Plant Name', bp.get('Plant ID', rp.get('Botanical', 'Uncertain botanical witness')))
    conc = botp.get('Sherwood / Consensus', '')
    botanical = plant if not conc else f'{plant}; {conc}'
    risk = bp.get('Risk Level', rp.get('Risk', 'MODERATE')).lower()
    cur = bp.get('Currier', rp.get('Currier', '?')).replace('Language ', '').replace('**', '')
    ill = bp.get('Illustration', 'Herbal witness')
    plain = pick(bb, 'PLAIN-ENGLISH')
    hist = pick(bb, 'HISTORICAL')
    confb = pick(bb, 'CONFIDENCE')
    uniq = pick(rb, 'What Makes')
    proc = pick(rb, 'Process Summary')
    am = re.search(r'Formula-Botanical Alignment:\s*(.+)', pick(bb, 'BOTANICAL IDENTIFICATION'), re.I | re.S)
    align = am.group(1).strip() if am else ''
    rows = []
    for lid, eva_line in elines:
        exp = tm.get(lid)
        rows.append((lid, eva_line, literal(eva_line, exp), optext(eva_line, proc or plain or sub, exp), summary(eva_line, exp), conf(eva_line, exp)))
    gs = groups(elines)
    c = counts(elines)
    fd = disp(fid)
    purpose = f'`{fd}` is rendered from the Book I manuscript witness plus the rigorous retranscription ledger. {cut(proc or sub, 240)} {cut(uniq, 260)} {cut(align or hist, 220)}'
    direct = cut(plain or proc, 320) or 'source-driven process summary'
    return make_folio(
        folio_id=fid, quire=quire, bifolio=bif,
        manuscript_role=clean(sub or proc or 'herbal process page').lower(),
        purpose=purpose, zero_claim=zclaim(proc or plain or sub), botanical=botanical, risk=risk,
        confidence=confsum(confb, 'medium on botanical certainty, high on process structure'),
        visual_grammar=visual(sub or proc, {**bp, 'Illustration': ill}, uniq, align or hist),
        full_eva=eva, core_vml=core(qrows), groups=gs, lines=rows, tarot_cards=tarot(len(rows)),
        movements=[r[4] for r in rows], direct=direct,
        math=f"Across the formal lenses, `{fd}` behaves as {phr(sub or proc, 10)}. The visible state carries {c['units']} line units, {c['completion']} completion markers, {c['essence']} essence loads, {c['union']} union markers, and {c['fire']} fire-seal markers. The attractor stays consistent with {cut(proc or plain, 180)}",
        mythic=f"Across the mythic lenses, `{fd}` is the herbal chapter of {phr(sub or plant, 8)}: the work moves from embodied plant witness into a disciplined operator tale and closes by proving {phr(proc or plain, 14)}.",
        compression=cut(proc or plain, 220), typed_state_machine=tsm(fd, gs), invariants=inv(fd, c), theorem=theorem(fid, proc or plain, qrows, rows[-1][0]),
        crystal_contribution=crystal(sub or proc, qrows, proc or plain),
        pointer_title=clean(sub or proc or 'Herbal Process Page'),
        pointer_position=f'the {fd} leaf in Book I\'s remaining plant section',
        pointer_page_type=f'{ill.lower()} with {c["units"]} visible operator units',
        pointer_conclusion=', '.join(clean(r[0]) for r in qrows[:4]) if qrows else cut(proc, 140),
        pointer_judgment=cut(direct or proc, 280), currier_language=cur, currier_hand='?',
        reading_contract=[
            'This final draft is compiled from the Book I herbal manuscript witness and the rigorous retranscription witness together.',
            'Quantitative signature rows are treated as structural evidence, not decoration.',
            'Damaged glyphs remain visible and are never silently normalized away.',
            'Every visible EVA line is preserved as its own operator event.',
        ],
    )

def main():
    bsec = sections(BOOK.read_text(encoding='utf-8-sig'), '# **FOLIO F')
    rsec = sections(RIGID.read_text(encoding='utf-8'), '# FOLIO F')
    ids = [x for n in range(28, 57) for x in (f'F{n:03d}R', f'F{n:03d}V')] + ['F057R']
    for fid in ids:
        fol = build(fid, bsec[fid], rsec[fid])
        (FOLIOS_DIR / f"{fol['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(fol), encoding='utf-8')
        (FOLIOS_DIR / f"{fol['folio_id']}.md").write_text(render_pointer(fol), encoding='utf-8')
    print(f'Rendered {len(ids)} plant folios through F057R.')

if __name__ == '__main__':
    main()
