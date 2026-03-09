from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'folios' / 'F001V_FINAL_DRAFT.md'

LINES = [
    ('P1.1', "kchs{&c'}y.chadaiin.ol.oltchey.char.cfhar.aj", "`kchs{&c'}y` contained volatile dissolved in active solution; `chadaiin` volatile earth-substance fixed through one full cycle; `ol` fluid medium; `oltchey` heated liquid carrying volatile essence; `char` rooted spirit capture; `cfhar` fire-seal at the root junction; `aj` uncertain terminal.", "Place the dangerous volatile material into active solution, complete the first fixation cycle, carry the volatile essence through heated fluid, capture it at the base, and lock the base connection with a fire seal.", 'initial sealed solution of dangerous volatile feedstock under fire-sealed base capture', 'uncertain', r'\mathsf F_{\texttt{cfhar}} \circ \mathsf C_{\texttt{char}} \circ \mathsf H_{\texttt{oltchey}} \circ \mathsf W_{\texttt{ol}} \circ \mathsf D_{\texttt{chadaiin}} \circ \mathsf S_{\texttt{kchs\{&c\'\}y}}'),
    ('P1.2', 'yteeay.char.orochy.dcho.lkody.okodar.chody', '`yteeay` active driven essence influx; `char` rooted volatile capture; `orochy` heated outlet volatile active; `dcho` fixed volatile body; `lkody` liquid contained and heat-fixed; `okodar` phase-shifted rooted fixation; `chody` volatile heated and fixed.', 'Drive the active essence from the rooted volatile source into the heated outlet path, phase-shift it within containment, and leave the volatile fraction heat-fixed.', 'move the captured volatile into a heated contained outlet path and stabilize it', 'mixed', r'\mathsf D_{\texttt{chody}} \circ \mathsf D_{\texttt{okodar}} \circ \mathsf S_{\texttt{lkody}} \circ \mathsf D_{\texttt{dcho}} \circ \mathsf G_{\texttt{orochy}} \circ \mathsf C_{\texttt{char}} \circ \mathsf H_{\texttt{yteeay}}'),
    ('P1.3', 'dao.ckhy.ckho.ckhy.shy.dksheey.cthy.kotchody.dal', '`dao` fixation under grounded heat; `ckhy.ckho.ckhy` valve active, valve heated, valve active again; `shy` forced transition flow; `dksheey` contained intensified essence fixed in motion; `cthy` active conduit; `kotchody` timed contained volatile heat product fixed; `dal` structural fixation.', 'Fix under heat, perform the three-step valve protocol, force flow through the active conduit, hold the timed volatile product inside containment, and lock it into structure.', 'execute the unique valve checkpoint and force the dangerous stream through the active conduit', 'mixed', r'\mathsf D_{\texttt{dal}} \circ \mathsf S_{\texttt{kotchody}} \circ \mathsf B_{\texttt{cthy}} \circ \mathsf D_{\texttt{dksheey}} \circ \mathsf H_{\texttt{shy}} \circ \mathsf V_{\texttt{ckhy}} \circ \mathsf H_{\texttt{ckho}} \circ \mathsf V_{\texttt{ckhy}} \circ \mathsf D_{\texttt{dao}}'),
    ('P1.4', 'dol.chokeo.dair.dam.sochey.chokody', '`dol` fixed liquid; `chokeo` volatile phase-shifted essence under heat; `dair` fixation through one breathing cycle; `dam` fix-union / coniunctio; `sochey` dissolved heated volatile essence active; `chokody` volatile phase-shifted, heated, and fixed.', 'Lock the liquid, move the volatile to phase-shifted heated essence, pass through one breathing fixation cycle, permanently reunite the separated principles, and leave the volatile in a phase-fixed heated state.', 'perform the chemical wedding that turns separated dangerous fractions into one fixed body', 'mixed', r'\mathsf D_{\texttt{chokody}} \circ \mathsf H_{\texttt{sochey}} \circ \mathsf U_{\texttt{dam}} \circ \mathsf D_{\texttt{dair}} \circ \mathsf R_{\texttt{chokeo}} \circ \mathsf D_{\texttt{dol}}'),
    ('P2.5', 'potoy.shol.dair.cphoal.dar.chey.tody.otoaiin.shoshy', '`potoy` pressed timed heat-active start; `shol` transition fluid; `dair` one-cycle fixation; `cphoal` pressure vessel in heated structural mode; `dar` rooted fixation; `chey` volatile essence active; `tody` driven heat-fix; `otoaiin` timed heated cycle complete; `shoshy` vigorous heated transition active.', 'Pressurize the transition fluid, take it through a one-cycle fixation in the heated vessel, root the active volatile essence, complete the timed heated cycle, and begin the vigorous heated transition that opens the reflux stage.', 'open the reflux stage inside the heated pressure vessel and root the active volatile fraction', 'mixed', r'\mathsf H_{\texttt{shoshy}} \circ \mathsf H_{\texttt{otoaiin}} \circ \mathsf D_{\texttt{tody}} \circ \mathsf C_{\texttt{chey}} \circ \mathsf D_{\texttt{dar}} \circ \mathsf P_{\texttt{cphoal}} \circ \mathsf D_{\texttt{dair}} \circ \mathsf H_{\texttt{shol}} \circ \mathsf P_{\texttt{potoy}}'),
    ('P2.6', 'choky.chol.ctholshol.okal.dolchey.chodo.lol.chy.cthy', '`choky` volatile phase-active; `chol` volatile fluid; `ctholshol` conduit fluid in transition; `okal` phase-contained body; `dolchey` fluid volatile essence fixed; `chodo` volatile heat-fix; `lol` liquid body; `chy` active volatile; `cthy` active conduit.', 'Move the volatile fluid through the conduit transition, hold it in phase containment, fix the fluid essence, refix the volatile under heat, return it to the liquid body, and keep the conduit actively carrying the stream.', 'stabilize the circulating volatile liquid while keeping the conduit fully active', 'mixed', r'\mathsf B_{\texttt{cthy}} \circ \mathsf C_{\texttt{chy}} \circ \mathsf W_{\texttt{lol}} \circ \mathsf D_{\texttt{chodo}} \circ \mathsf D_{\texttt{dolchey}} \circ \mathsf S_{\texttt{okal}} \circ \mathsf T_{\texttt{ctholshol}} \circ \mathsf C_{\texttt{chol}} \circ \mathsf C_{\texttt{choky}}'),
    ('P2.7', 'qo.olchoies.cheol.dol.cthey.ykol.dol.dolo.ykol.dolchieody', '`qo` circulate/extract command; `olchoies` fluid volatile essence cycling in flow; `cheol` spirit in liquid form; `dol` fixed liquid; `cthey` conduit essence active; `ykol` moist contained liquid; `dol` fixed liquid again; `dolo` heated fixed liquid; `ykol` moist contained liquid repeated; `dolchieody` fluid volatile heat-fixed through full cycle.', 'Begin the retort cycle, move the volatile spirit through the flowing liquid state, lock the liquid, return it through the energized conduit, wet-contain it, lock it again, heat-lock it, and repeat the return until the volatile liquid is permanently fixed.', 'run the central reflux loop until the volatile liquid converges to permanent fixation', 'mixed', r'\mathsf D_{\texttt{dolchieody}} \circ \mathsf S_{\texttt{ykol}} \circ \mathsf D_{\texttt{dolo}} \circ \mathsf D_{\texttt{dol}} \circ \mathsf S_{\texttt{ykol}} \circ \mathsf T_{\texttt{cthey}} \circ \mathsf D_{\texttt{dol}} \circ \mathsf C_{\texttt{cheol}} \circ \mathsf R_{\texttt{olchoies}} \circ \mathsf R_{\texttt{qo}}'),
    ('P2.8', 'okolshol.kolkechy.cholky.chol.cthol.chody.chol.daiin', '`okolshol` phase-contained transition fluid; `kolkechy` contained liquid volatile essence active; `cholky` volatile fluid under active containment; `chol` volatile fluid; `cthol` conduit fluid; `chody` volatile heat-fixed; `chol` volatile fluid; `daiin` cycle completion marker.', 'Narrow the reflux loop into a fully contained transition state, keep the volatile essence under liquid control, pass it through the conduit, heat-fix the volatile fluid, and mark the single completion checkpoint for the page.', 'tighten the reflux loop into a bounded completion state and register the page checkpoint', 'mixed', r'\mathsf Q_{\texttt{daiin}} \circ \mathsf C_{\texttt{chol}} \circ \mathsf D_{\texttt{chody}} \circ \mathsf T_{\texttt{cthol}} \circ \mathsf C_{\texttt{chol}} \circ \mathsf S_{\texttt{cholky}} \circ \mathsf S_{\texttt{kolkechy}} \circ \mathsf R_{\texttt{okolshol}}'),
    ('P2.9', 'shor.okol.chol.dol.ky.dar.shol.dchor.otcho.dar.shody', '`shor` flowing outlet transition; `okol` phase-contained liquid; `chol` volatile fluid; `dol` fixed liquid; `ky` active containment; `dar` rooted fixation; `shol` transition fluid; `dchor` fixed volatile outlet; `otcho` timed volatile drive; `dar` rooted fixation; `shody` heated transition fixed.', 'Drive the contained volatile liquid toward the outlet, lock the liquid and its containment, root the stream again, move it through one more transition phase, and leave the outlet path in a heat-fixed state.', 'route the converged product toward the outlet while maintaining rooted containment', 'mixed', r'\mathsf D_{\texttt{shody}} \circ \mathsf D_{\texttt{dar}} \circ \mathsf H_{\texttt{otcho}} \circ \mathsf G_{\texttt{dchor}} \circ \mathsf H_{\texttt{shol}} \circ \mathsf D_{\texttt{dar}} \circ \mathsf S_{\texttt{ky}} \circ \mathsf D_{\texttt{dol}} \circ \mathsf C_{\texttt{chol}} \circ \mathsf R_{\texttt{okol}} \circ \mathsf G_{\texttt{shor}}'),
    ('P2.10', 'taor.chotchey.dal.chody.schody.pol.chodar', '`taor` drive earth-substance to outlet; `chotchey` timed volatile essence active; `dal` structural fixation; `chody` volatile heat-fixed; `schody` dissolved volatile heat-fixed; `pol` pressed liquid; `chodar` volatile heated fixed and rooted.', 'Push the prepared substance to the outlet, structure the active timed volatile essence, fix the volatile twice through heated and dissolved states, press the liquid remainder, and finish with one rooted volatile product.', 'collect the single rooted narcotic product after the reflux has fully stabilized it', 'mixed', r'\mathsf D_{\texttt{chodar}} \circ \mathsf P_{\texttt{pol}} \circ \mathsf D_{\texttt{schody}} \circ \mathsf D_{\texttt{chody}} \circ \mathsf D_{\texttt{dal}} \circ \mathsf H_{\texttt{chotchey}} \circ \mathsf G_{\texttt{taor}}'),
]

FORMAL_LENSES = [('aqm', 'AQM'), ('cut', 'CUT'), ('liminal', 'Liminal'), ('aetheric', 'Aetheric'), ('chemistry', 'Chemistry'), ('physics', 'Physics'), ('quantum', 'Quantum Physics'), ('wave_mechanics', 'Wave Mechanics'), ('wave_math', 'Wave Math'), ('music', 'Music Theory and Music Math'), ('light', 'Color and Light'), ('geometry', 'Geometry'), ('number', 'Number Theory'), ('compression', 'Compression'), ('hacking', 'Hacking Theory'), ('game', 'Game Theory')]
MYTHIC = {
    'Tarot': {'P1.1': ('The Magician', 'charge the sealed cup', 'Agency enters only inside a controlled vessel.'), 'P1.2': ('The Chariot', 'route the force', 'The captured spirit is directed rather than merely held.'), 'P1.3': ('Justice', 'open heat reseal', 'The valve sequence is danger handled by lawful sequence.'), 'P1.4': ('The Lovers', 'chemical wedding', 'Separated principles are rejoined into one body.'), 'P2.5': ('Strength', 'raise pressure safely', 'The vessel meets force without rupture.'), 'P2.6': ('Temperance', 'pour back and forth', 'Circulation preserves potency through balance.'), 'P2.7': ('Wheel of Fortune', 'repeat the rise and return', 'The reflux loop turns until fixation holds.'), 'P2.8': ('The World', 'close the bounded loop', 'Completion is registered inside containment.'), 'P2.9': ('The Emperor', 'govern the outlet', 'Even release remains under rooted control.'), 'P2.10': ('The Sun', 'reveal the single medicine', 'The page ends in one stable visible product.')},
    'Juggling': {'P1.1': ('first ball enters', 'launch into sealed cascade', 'The pattern begins only after a safe receiving hand exists.'), 'P1.2': ('establish the lane', 'send the object down one path', 'The ball cannot wander.'), 'P1.3': ('three-beat check', 'catch pulse recast', 'The valve sequence is the rhythm proof.'), 'P1.4': ('merge streams', 'combine tosses into one pattern', 'Union stabilizes what was separate.'), 'P2.5': ('raise the arc', 'add height and pressure', 'Energy increases without losing timing.'), 'P2.6': ('hold the center', 'keep the middle alive', 'The loop survives by preserving the center lane.'), 'P2.7': ('sustain cascade', 'repeat rise return', 'The full cascade settles through repetition.'), 'P2.8': ('narrow the run', 'shorten to a finishable pattern', 'Completion comes from tighter spacing.'), 'P2.9': ('send to catch hand', 'route toward final receive', 'Exit still obeys safety timing.'), 'P2.10': ('clean final catch', 'press and collect', 'The run resolves in one held object.')},
    'Story Writing': {'P1.1': ('inciting setup', 'danger enters the apparatus', 'The premise is threat plus container.'), 'P1.2': ('directed escalation', 'give the threat a route', 'The plot gains vector.'), 'P1.3': ('checkpoint scene', 'pause at the valve decision', 'Competence is tested here.'), 'P1.4': ('act I climax', 'join the split strands', 'The first block closes in union.'), 'P2.5': ('act II launch', 'raise stakes in the vessel', 'The second movement commits to process.'), 'P2.6': ('maintenance sequence', 'keep the tension circulating', 'The story sustains pressure without resolving.'), 'P2.7': ('central set-piece', 'run the recursive ordeal', 'The folio\'s dramatic engine is the reflux loop.'), 'P2.8': ('narrowing corridor', 'reduce futures to one valid finish', 'The page stops branching.'), 'P2.9': ('exit vector', 'guide the transformed material outward', 'Return begins under control.'), 'P2.10': ('resolution object', 'end with one artifact', 'The climax becomes a single medicine.')},
    'Hero\'s Journey': {'P1.1': ('call to dangerous work', 'accept the substance only under seal', 'The call is disciplined admission into danger.'), 'P1.2': ('first threshold', 'enter the controlled route', 'The work moves from preparation to action.'), 'P1.3': ('tests and guards', 'meet the valve gate', 'This is the threshold guardian scene.'), 'P1.4': ('sacred marriage', 'win union after separation', 'The initiate gains the first talisman.'), 'P2.5': ('descent', 'go deeper into the vessel', 'Pressure marks entry into ordeal.'), 'P2.6': ('ordeal maintenance', 'keep the stream alive', 'Survival in the middle matters as much as entry.'), 'P2.7': ('abyss and return', 'repeat death and rebirth', 'The reflux loop is the page\'s abyss.'), 'P2.8': ('reward', 'seal the completion sign', 'Proof appears that the ordeal is working.'), 'P2.9': ('road back', 'carry the product toward use', 'Return starts but remains guarded.'), 'P2.10': ('return with the boon', 'bring home one rooted medicine', 'The boon is singular and earned.')},
}

LEGEND = {
    'aqm': '`rho^-` incoming hazardous state; `rho^+` outgoing line state; `Phi_line^(AQM)` source operator chain.',
    'cut': '`X=(kappa,varphi,ell,b)` with containment, phase, liquid flux, and boundary integrity.',
    'liminal': '`p(r)` regime mass, `lambda(e)` liminal-edge load, `f` fail-space mass.',
    'aetheric': '`g` compressed seed, `X` expanded state, `r_line` residual address.',
    'chemistry': '`x=[m_root,m_volatile,m_liquid,m_fixed]^T`; `K_line` conserves total material.',
    'physics': '`X^(phys)` tracks containment geometry, phase, flow, and seal integrity.',
    'quantum': '`rho^(qm)` is the line state on the total carrier with boundary sectors.',
    'wave_mechanics': '`u` is the wave profile; `U_line` is the contraction-compatible update.',
    'wave_math': '`mathcal U_line` is the semigroup block for the line.',
    'music': '`m in R^12` is the pitch-tension vector; `tau` is post-line tension.',
    'light': '`I(lambda)` is spectral intensity; `K_line(lambda,mu)` is the transport kernel.',
    'geometry': '`gamma` is the route through the folio manifold.',
    'number': '`a` counts active resources across channels; `A_line` is an integer update matrix.',
    'compression': '`g` is the replay seed and `rho` the expanded state.',
    'hacking': '`pi` is the route, `e_line` the next admissible edge, `B_line` the seal budget.',
    'game': '`y` is the strategy distribution; `R_line` is risk and `C` the control-cost.',
}


def slug(line_id: str) -> str:
    return line_id.replace('.', '_')


def eq(lens: str, line_id: str, op: str) -> str:
    s = slug(line_id)
    if lens == 'aqm':
        return f"\\[\\rho_{{\\mathrm{{{s}}}}}^+ = \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}}(\\rho_{{\\mathrm{{{s}}}}}^-), \\qquad \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} = {op}\\]"
    if lens == 'cut':
        return f"\\[X_{{\\mathrm{{{s}}}}}^+ = A_{{\\mathrm{{{s}}}}} X_{{\\mathrm{{{s}}}}}^-, \\qquad A_{{\\mathrm{{{s}}}}} = T_{{\\mathrm{{CUT}}}}^{{-1}} \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} T_{{\\mathrm{{CUT}}}}\\]"
    if lens == 'liminal':
        return f"\\[\\bigl(p_{{\\mathrm{{{s}}}}}^+, \\lambda_{{\\mathrm{{{s}}}}}^+, f_{{\\mathrm{{{s}}}}}^+\\bigr) = L_{{\\mathrm{{{s}}}}}\\bigl(p_{{\\mathrm{{{s}}}}}^-, \\lambda_{{\\mathrm{{{s}}}}}^-, f_{{\\mathrm{{{s}}}}}^-\\bigr), \\qquad f_{{\\mathrm{{{s}}}}}^+ = \\mathrm{{Tr}}(\\Pi_{{\\mathrm{{fail}}}}\\rho_{{\\mathrm{{{s}}}}}^+)\\]"
    if lens == 'aetheric':
        return f"\\[X_{{\\mathrm{{{s}}}}}^+ = \\mathrm{{Expand}}(g_{{\\mathrm{{{s}}}}}^-) \\oplus r_{{\\mathrm{{{s}}}}}, \\qquad g_{{\\mathrm{{{s}}}}}^+ = \\mathrm{{Coll}}(X_{{\\mathrm{{{s}}}}}^+)\\]"
    if lens == 'chemistry':
        return f"\\[x_{{\\mathrm{{{s}}}}}^{{+,\\mathrm{{chem}}}} = K_{{\\mathrm{{{s}}}}} x_{{\\mathrm{{{s}}}}}^{{-,\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_{{\\mathrm{{{s}}}}} = \\mathbf{{1}}^T\\]"
    if lens == 'physics':
        return f"\\[X_{{\\mathrm{{{s}}}}}^{{+,\\mathrm{{phys}}}} = P_{{\\mathrm{{{s}}}}} X_{{\\mathrm{{{s}}}}}^{{-,\\mathrm{{phys}}}}, \\qquad P_{{\\mathrm{{{s}}}}} = T_{{\\mathrm{{phys}}}}^{{-1}} \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} T_{{\\mathrm{{phys}}}}\\]"
    if lens == 'quantum':
        return f"\\[\\rho_{{\\mathrm{{{s}}}}}^{{+,\\mathrm{{qm}}}} = \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{tot}}}}(\\rho_{{\\mathrm{{{s}}}}}^{{-,\\mathrm{{qm}}}})\\]"
    if lens == 'wave_mechanics':
        return f"\\[u_{{\\mathrm{{{s}}}}}^+ = U_{{\\mathrm{{{s}}}}}u_{{\\mathrm{{{s}}}}}^-, \\qquad U_{{\\mathrm{{{s}}}}} = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} T_{{\\mathrm{{wave}}}}, \\qquad \\|U_{{\\mathrm{{{s}}}}}\\| \\le 1\\]"
    if lens == 'wave_math':
        return f"\\[\\mathcal{{U}}_{{\\mathrm{{{s}}}}} = T_{{\\mathrm{{wavemath}}}}^{{-1}} \\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}} T_{{\\mathrm{{wavemath}}}}\\]"
    if lens == 'music':
        return f"\\[m_{{\\mathrm{{{s}}}}}^+ = M_{{\\mathrm{{{s}}}}}m_{{\\mathrm{{{s}}}}}^-, \\qquad \\tau_{{\\mathrm{{{s}}}}} = \\|L m_{{\\mathrm{{{s}}}}}^+\\|_2\\]"
    if lens == 'light':
        return f"\\[I_{{\\mathrm{{{s}}}}}^+(\\lambda) = \\int K_{{\\mathrm{{{s}}}}}(\\lambda,\\mu) I_{{\\mathrm{{{s}}}}}^-(\\mu)\\, d\\mu\\]"
    if lens == 'geometry':
        return f"\\[\\gamma_{{\\mathrm{{{s}}}}}^+ = G_{{\\mathrm{{{s}}}}}(\\gamma_{{\\mathrm{{{s}}}}}^-)\\]"
    if lens == 'number':
        return f"\\[a_{{\\mathrm{{{s}}}}}^+ = A_{{\\mathrm{{{s}}}}} a_{{\\mathrm{{{s}}}}}^-, \\qquad A_{{\\mathrm{{{s}}}}} \\in M_k(\\mathbb{{Z}}_{{\\ge 0}})\\]"
    if lens == 'compression':
        return f"\\[g_{{\\mathrm{{{s}}}}}^+ = \\mathrm{{Coll}}\\!\\left(\\Phi_{{\\mathrm{{{s}}}}}^{{\\mathrm{{AQM}}}}(\\mathrm{{Expand}}(g_{{\\mathrm{{{s}}}}}^-))\\right)\\]"
    if lens == 'hacking':
        return f"\\[\\pi_{{\\mathrm{{{s}}}}}^+ = \\pi_{{\\mathrm{{{s}}}}}^- \\oplus e_{{\\mathrm{{{s}}}}}, \\qquad e_{{\\mathrm{{{s}}}}} \\in E_{{\\mathrm{{safe}}}} \\iff \\mathrm{{seal}}(e_{{\\mathrm{{{s}}}}})=1 \\land \\mathrm{{budget}}(e_{{\\mathrm{{{s}}}}})\\le B_{{\\mathrm{{{s}}}}}\\]"
    return f"\\[y_{{\\mathrm{{{s}}}}}^+ = \\operatorname*{{argmin}}_{{y \\in \\Delta(\\mathcal{{A}})}}\\{{R_{{\\mathrm{{{s}}}}}(y) + \\lambda_{{\\mathrm{{{s}}}}} C(y, y_{{\\mathrm{{{s}}}}}^-)\\}}\\]"

def direct_ledger() -> str:
    out = ['### Paragraph 1 - containment, valve protocol, and coniunctio', '']
    for line_id, eva, literal, operational, *_ in LINES[:4]:
        out += [f'- `{line_id}`', f'  EVA: `{eva}`', f'  Literal chain: {literal}', f'  Operational English: {operational}', '']
    out += ['### Paragraph 2 - reflux purification and product collection', '']
    for line_id, eva, literal, operational, *_ in LINES[4:]:
        out += [f'- `{line_id}`', f'  EVA: `{eva}`', f'  Literal chain: {literal}', f'  Operational English: {operational}', '']
    return '\n'.join(out).rstrip()


def formal_sections() -> str:
    out = []
    for lens, title in FORMAL_LENSES:
        out += [f'### {title}', '']
        for line_id, _eva, _literal, _oper, summary, confidence, op in LINES:
            out += [f'- `{line_id}`', '  Equation:', '', f'  {eq(lens, line_id, op)}', '', f'  Variable legend: {LEGEND[lens]}', f'  Reading: {summary}.', f'  Confidence: {confidence}', '']
    return '\n'.join(out).rstrip()


def mythic_sections() -> str:
    out = []
    for title, mapping in MYTHIC.items():
        out += [f'### {title}', '']
        for line_id, *_ in LINES:
            frame, movement, reading = mapping[line_id]
            confidence = next(line[5] for line in LINES if line[0] == line_id)
            out += [f'- `{line_id}`', f'  Frame: {frame}', f'  Movement: {movement}', f'  Reading: {reading}', f'  Confidence: {confidence}', '']
    return '\n'.join(out).rstrip()


def operator_matrix() -> str:
    out = []
    for line_id, *_prefix, op in LINES:
        out += [f'- `{line_id}`', '', f'\\[\\Phi_{{\\mathrm{{{slug(line_id)}}}}}^{{\\mathrm{{AQM}}}} = {op}\\]', '']
    return '\n'.join(out).rstrip()


def render() -> str:
    formal = formal_sections()
    mythic = mythic_sections()
    ops = operator_matrix()
    ledger = direct_ledger()
    return dedent(f'''# F001V Final Draft - Dense Multilens Translation Atlas

## Final Draft Status

- Status: `authoritative final-draft folio`
- Manuscript role: `opening verso / first dangerous illustrated execution / reflux threshold`
- Book: `Book I - Herbal / materia medica`
- Source baseline: `F001V.md`

## Purpose

`f001v` is the first live demonstration page. The apparatus implied by `f001r` is now used on dangerous material, and the folio resolves to a controlled low-heat spirit extraction with recombination, reflux, and one rooted terminal product.

## Source Stack

- `NEW/working/VML_RIGOROUS_RETRANSCRIPTION_QUIRES_ABCDEFG.md`
- `NEW/working/VML_RECIPE_CROSSREF.md`
- `NEW/working/VML_CONSISTENCY_PROOF.md`
- `NEW/SECTION I - BOOK I_ THE HERBAL _ MATERIA MEDICA.md`
- `NEW/working/THE VML ROSETTA STONE.md`
- `FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md`
- `FULL_TRANSLATION/framework/registry/math_kernel_registry.md`

## Reading Contract

- EVA and VML are the direct claim layer.
- Every requested lens appears line-by-line below.
- Formal math lenses use real equations, not prose placeholders.
- Derived renderers stay tethered to the AQM source operator chain.
- The strongest claim is process-specific: danger, containment, reflux, and single-product closure.

## Folio Zero Claim

`f1v` is a spirit-dominant dangerous extraction page: do not wash the poison away; capture it, stabilize it, reunite it, cycle it, and root it into one bounded medicine.

## Folio Identity

| Field | Value |
| --- | --- |
| Folio | `f1v` |
| Quire | `A` |
| Bifolio | `bA1 = f1 + f8` |
| Currier language | `A` |
| Currier hand | `1` |
| Illustration | one plant |
| Botanical candidate | belladonna-class / Solanaceae |
| Risk level | lethal / high-potency |
| Direct confidence | high on dangerous-extraction logic, moderate on exact species |

## Visual Grammar and Codicology

- `clawed root` = dangerous source material
- `parallel root lines` = internal channels and controlled pathways
- `drooping branches` = reflux / return-flow cycling
- `single dark flower` = one concentrated sealed output
- `sealed flower form` = terminal closure

## Full EVA

```text
P1.1: kchs{{&c'}}y.chadaiin.ol.oltchey.char.cfhar.aj-
P1.2: yteeay.char.orochy.dcho.lkody.okodar.chody-
P1.3: dao.ckhy.ckho.ckhy.shy.dksheey.cthy.kotchody.dal-
P1.4: dol.chokeo.dair.dam.sochey.chokody=

P2.5: potoy.shol.dair.cphoal.dar.chey.tody.otoaiin.shoshy-
P2.6: choky.chol.ctholshol.okal.dolchey.chodo.lol.chy.cthy-
P2.7: qo.olchoies.cheol.dol.cthey.ykol.dol.dolo.ykol.dolchieody-
P2.8: okolshol.kolkechy.cholky.chol.cthol.chody.chol.daiin-
P2.9: shor.okol.chol.dol.ky.dar.shol.dchor.otcho.dar.shody-
P2.10: taor.chotchey.dal.chody.schody.pol.chodar=
```

## Core VML Machinery Active On F1v

- `ckh` = valve clamp / seal checkpoint
- `cfh` = fire seal / danger-grade boundary
- `cph` = pressure vessel / heated chamber
- `cth` = conduit / throat / transport line
- `dam` = fix-union / coniunctio
- `dol` = liquid fixation
- `ykol` = wet contained liquid return
- `qo` = circulate / extract by loop
- `ch` = volatile spirit fraction
- `d` = fix / stabilize
- `o` = heat / activate
- `daiin` = completion checkpoint
- `chodar` = rooted terminal volatile product

## Direct Line-By-Line Literal Ledger

{ledger}

## Multilens Translation Atlas

{formal}

{mythic}

## Direct Operational Meaning

Paragraph 1 loads dangerous volatile feedstock into active solution, captures it under a fire seal, and pushes it through the unique `ckhy.ckho.ckhy` valve checkpoint before reaching `dam`, the union marker. Paragraph 2 opens the reflux stage in the heated pressure vessel, stabilizes the circulating volatile liquid, repeats the `dol ... ykol ... dol ... ykol ... dolchieody` return loop until convergence, and closes with one rooted product in `chodar`.

## Mathematical Extraction

Across the formal math lenses, `f1v` is a bounded hazardous controller with five regimes: containment, valve test, union, reflux convergence, and collection. The folio computes cyclic purification under a seal budget until the volatile fraction enters a fixed attractor.

## Mythic Extraction

Across the mythic lenses, `f1v` is an ordeal of disciplined danger: admit the force only inside the right vessel, test it at the gate, join what was split, survive the rise-and-return abyss, then bring home one boon.

## All-Lens Zero Point

`f1v` means: when the dangerous principle itself is the desired medicine, the work is to bound it, test it, join it, cycle it, and reduce it to one transmissible stable form.

## Dense One-Sentence Compression

Seal the dangerous spirit in solution, run the open-heat-reseal gate, perform the chemical wedding, then drive the reflux loop until one rooted medicine can be collected.

## Formal Mathematical Overlay For F1v

### Imported Kernel Equations

\\[\\mathcal H := L^2(\\widehat{{\\mathbb C}}, \\mu), \\qquad \\rho \\in \\mathcal T_1(\\mathcal H), \\qquad \\rho \\succeq 0, \\qquad \\mathrm{{Tr}}(\\rho)=1\\]

\\[\\mathcal H_{{\\mathrm{{tot}}}} = \\left(\\bigoplus_r \\mathcal H_r\\right) \\oplus \\left(\\bigoplus_e \\mathcal H_{{\\Lambda_e}}\\right) \\oplus \\mathcal H_{{\\mathrm{{fail}}}}\\]

\\[x_{{n+1}}^{{\\mathrm{{chem}}}} = K_n x_n^{{\\mathrm{{chem}}}}, \\qquad \\mathbf{{1}}^T K_n = \\mathbf{{1}}^T\\]

\\[g = \\mathrm{{Coll}}(X), \\qquad X = \\mathrm{{Expand}}(g) \\oplus r\\]

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

### Typed State Machine

\\[\\mathcal R_{{f1v}} = \\{{r_{{\\mathrm{{contain}}}}, r_{{\\mathrm{{valve}}}}, r_{{\\mathrm{{union}}}}, r_{{\\mathrm{{reflux}}}}, r_{{\\mathrm{{collect}}}}\\}}\\]

\\[\\mathcal E_\\Lambda = \\{{e_{{\\mathrm{{ckh}}}}, e_{{\\mathrm{{dam}}}}, e_{{\\mathrm{{reflux}}}}\\}}\\]

\\[\\delta(e_{{\\mathrm{{ckh}}}}): r_{{\\mathrm{{contain}}}} \\to r_{{\\mathrm{{valve}}}}, \\qquad \\delta(e_{{\\mathrm{{dam}}}}): r_{{\\mathrm{{valve}}}} \\to r_{{\\mathrm{{union}}}}, \\qquad \\delta(e_{{\\mathrm{{reflux}}}}): r_{{\\mathrm{{union}}}} \\to r_{{\\mathrm{{reflux}}}} \\to r_{{\\mathrm{{collect}}}}\\]

\\[\\rho_0 \\in \\mathcal H_{{r_{{\\mathrm{{contain}}}}}}, \\qquad x_0^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{root}}}}^0 \\\\ m_{{\\mathrm{{volatile}}}}^0 \\\\ m_{{\\mathrm{{liquid}}}}^0 \\\\ 0 \\end{{bmatrix}}, \\qquad g_0 = \\mathrm{{Coll}}(\\rho_0)\\]

### Canonical AQM Line Operators

{ops}

### Paragraph Compositions

\\[\\Phi_{{P1}}^{{\\mathrm{{tot}}}} = \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\Phi_{{P2}}^{{\\mathrm{{tot}}}} = \\Phi_{{\\mathrm{{P2_10}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_5}}}}^{{\\mathrm{{AQM}}}}\\]

\\[\\rho_{{P1}} = \\Phi_{{P1}}^{{\\mathrm{{tot}}}}(\\rho_0), \\qquad \\rho_* = \\Phi_{{P2}}^{{\\mathrm{{tot}}}}(\\rho_{{P1}})\\]

### Formal Safety Invariants

\\[\\mathrm{{Tr}}(\\rho_n)=1\\]

\\[f_n = \\mathrm{{Tr}}(\\Pi_{{\\mathrm{{fail}}}}\\rho_n)=0\\]

\\[C_{{\\mathrm{{reg}}}}(\\rho_n)=\\frac{{1}}{{2}}\\|\\rho_n-\\Delta_{{\\mathcal B}}(\\rho_n)\\|_1 \\le \\varepsilon_n\\]

\\[\\Phi_\\ell(n)=\\int_{{\\partial A_n}} J_\\ell^\\mu n_\\mu\\, d\\sigma_n \\le \\beta_{{\\mathrm{{seal}}}}\\]

\\[p_n(r_{{\\mathrm{{collect}}}})=1 \\implies \\lambda_n(e_{{\\mathrm{{reflux}}}})=0\\]

### Conjugacy Law

\\[\\Phi_j^{{(\\lambda)}} = T_\\lambda^{{-1}} \\circ \\Phi_j^{{(\\mathrm{{AQM}})}} \\circ T_\\lambda\\]

\\[K_j = T_{{\\mathrm{{chem}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{chem}}}}, \\qquad U_j = T_{{\\mathrm{{wave}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{wave}}}}, \\qquad A_j = T_{{\\mathrm{{num}}}}^{{-1}} \\Phi_j^{{(\\mathrm{{AQM}})}} T_{{\\mathrm{{num}}}}\\]

### Concrete Transport Targets

\\[x_n^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{root}}}}(n) \\\\ m_{{\\mathrm{{volatile}}}}(n) \\\\ m_{{\\mathrm{{liquid}}}}(n) \\\\ m_{{\\mathrm{{fixed}}}}(n) \\end{{bmatrix}}, \\qquad X_n^{{\\mathrm{{phys}}}}=(\\kappa_n,\\varphi_n,\\ell_n,b_n), \\qquad m_n \\in \\mathbb{{R}}^{{12}}, \\qquad g_n=\\mathrm{{Coll}}(\\rho_n)\\]

### Formal Folio Theorem

\\[\\rho_* = \\left(\\Phi_{{\\mathrm{{P2_10}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_9}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_8}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_7}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_6}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P2_5}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_4}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_3}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_2}}}}^{{\\mathrm{{AQM}}}} \\circ \\Phi_{{\\mathrm{{P1_1}}}}^{{\\mathrm{{AQM}}}}\\right)(\\rho_0)\\]

\\[\\Pi_{{r_{{\\mathrm{{collect}}}}}}\\rho_* = \\rho_*, \\qquad \\lambda_*(e_{{\\mathrm{{ckh}}}})=0, \\qquad \\lambda_*(e_{{\\mathrm{{reflux}}}})=0\\]

\\[x_*^{{\\mathrm{{chem}}}} = \\begin{{bmatrix}} m_{{\\mathrm{{root}}}}^* \\\\ m_{{\\mathrm{{volatile}}}}^* \\\\ 0 \\\\ m_{{\\mathrm{{fixed}}}}^* \\end{{bmatrix}}, \\qquad m_{{\\mathrm{{volatile}}}}^* > 0, \\qquad m_{{\\mathrm{{fixed}}}}^* > 0, \\qquad g_* = \\mathrm{{Coll}}(\\rho_*)\\]

The theorem says `f1v` computes a bounded hazardous reflux process whose unique valid terminal object is a rooted, sealed, volatile medicine.

## Final Draft Audit

- Every visible line has EVA, direct ledger, formal-math render, and mythic render.
- The gate tokens `ckhy.ckho.ckhy`, `dam`, `dol...ykol...`, `dolchey`, `schody`, and `chodar` remain explicit.
- Confidence is highest for the page-level claim `dangerous reflux extraction with one sealed product`.
- Confidence is lower for exact glosses of rare compounds and for exact species identity.

## Plant Crystal Contribution

- `Danger Demonstration` - first illustrated live test under lethal material
- `Valve Checkpoint` - explicit `ckhy.ckho.ckhy` safety interlock
- `Chemical Wedding` - `dam` as overt coniunctio
- `Reflux Loop` - clearest early rise-return cycle in Book I
- `Single Product Closure` - one dark-cored sealed output ending in `chodar`
''').strip() + '\n'


def main() -> None:
    OUTPUT.write_text(render(), encoding='utf-8')


if __name__ == '__main__':
    main()
