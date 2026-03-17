from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
FULL_TRANSLATION = ROOT / "FULL_TRANSLATION"
ROSETTA_ROOT = FULL_TRANSLATION / "rosetta_machine"
SCHEMAS_DIR = ROSETTA_ROOT / "schemas"
REGISTRIES_DIR = ROSETTA_ROOT / "registries"
BUILD_DIR = ROSETTA_ROOT / "build"
EXPORTS_DIR = BUILD_DIR / "exports"
CONSUMERS_DIR = BUILD_DIR / "consumers"
MIRRORS_DIR = ROSETTA_ROOT / "mirrors"
FRAMEWORK_DIR = FULL_TRANSLATION / "framework"
FOLIOS_DIR = FULL_TRANSLATION / "folios"
SECTIONS_DIR = FULL_TRANSLATION / "sections"
UNIFIED_DIR = FULL_TRANSLATION / "unified"
CRYSTALS_DIR = FULL_TRANSLATION / "crystals"
METRO_DIR = FULL_TRANSLATION / "metro"
NEURAL_DIR = FULL_TRANSLATION / "neural_network"
MANIFESTS_DIR = FULL_TRANSLATION / "manifests"
DOC_GATE_PATHS = [
    ROOT.parent / "self_actualize" / "live_docs_gate_status.md",
    FULL_TRANSLATION / "manifests" / "LIVE_DOCS_GATE_STATUS_ROSETTA_STONE.md",
]
DOC_GATE_REQUIRED_FILES = [
    ROOT.parent / "Trading Bot" / "credentials.json",
    ROOT.parent / "Trading Bot" / "token.json",
]
DOC_EXTS = {".md", ".txt", ".docx", ".json", ".py"}
MANUSCRIPT_COMPANION_PATH = UNIFIED_DIR / "VOYNICH_MASTER_MANUSCRIPT_ROSETTA_COMPANION.md"
CRYSTAL_COMPANION_PATH = CRYSTALS_DIR / "VOYNICH_FULL_CRYSTAL_ROSETTA_COMPANION.md"
METRO_COMPANION_PATH = METRO_DIR / "VOYNICH_METRO_MAP_ROSETTA_COMPANION.md"
NODE_BRIDGE_PATH = NEURAL_DIR / "ROSETTA_MACHINE_NODE_BRIDGE.md"
INTEGRATION_STATUS_PATH = MANIFESTS_DIR / "ROSETTA_MACHINE_INTEGRATION_STATUS.md"
CANONICAL_FULL_TRANSLATION_PATH = UNIFIED_DIR / "VOYNICH_FULL_TRANSLATION.md"
CANONICAL_MASTER_MANUSCRIPT_PATH = UNIFIED_DIR / "VOYNICH_MASTER_MANUSCRIPT.md"
CANONICAL_FULL_CRYSTAL_PATH = CRYSTALS_DIR / "VOYNICH_FULL_CRYSTAL.md"
CANONICAL_METRO_MAP_PATH = METRO_DIR / "VOYNICH_METRO_MAP_WORKING.md"
CANONICAL_NEURAL_MASTER_PATH = NEURAL_DIR / "MASTER_NEURAL_SYNTHESIS.md"
GIANT_MANUSCRIPT_PATH = UNIFIED_DIR / "VOYNICH_GIANT_MANUSCRIPT.md"
EMERGENT_METRO_PATH = NEURAL_DIR / "METRO_MAP_L2_EMERGENT.md"
CANONICAL_PROMOTION_MANIFEST_PATH = CONSUMERS_DIR / "canonical_promotion_manifest.json"
GIANT_MANUSCRIPT_MANIFEST_PATH = CONSUMERS_DIR / "giant_manuscript_manifest.json"
ARCHIVE_DIR = ROSETTA_ROOT / "archive"
REQUIRED_SPLIT_UNITS = {
    "F085R1",
    "F085R2",
    "F086V3",
    "F086V4",
    "F086V5",
    "F086V6",
    "F089R1",
    "F089R2",
    "F089V1",
    "F089V2",
}

SECTION_PACKAGE_FILES = [
    SECTIONS_DIR / "FULL_PLANT.md",
    SECTIONS_DIR / "FULL_ASTROLOGY.md",
    SECTIONS_DIR / "FULL_BATH.md",
    SECTIONS_DIR / "FULL_COSMOLOGY.md",
    SECTIONS_DIR / "PHARMACEUTICAL_1_FULL.md",
    SECTIONS_DIR / "PHARMACEUTICAL_1_SYNTHESIS.md",
    SECTIONS_DIR / "PHARMACEUTICAL_2_FULL.md",
    SECTIONS_DIR / "PHARMACEUTICAL_2_SYNTHESIS.md",
    SECTIONS_DIR / "PHARMACEUTICAL_1_2_SYNTHESIS.md",
]

CRYSTAL_PACKAGE_FILES = [
    CRYSTALS_DIR / "PLANT_CRYSTAL.md",
    CRYSTALS_DIR / "MASTER_PLANT_CRYSTAL.md",
    CRYSTALS_DIR / "ASTROLOGY_CRYSTAL.md",
    CRYSTALS_DIR / "MASTER_ASTROLOGY_CRYSTAL.md",
    CRYSTALS_DIR / "BATH_CRYSTAL.md",
    CRYSTALS_DIR / "MASTER_BATH_CRYSTAL.md",
    CRYSTALS_DIR / "COSMOLOGY_CRYSTAL.md",
    CRYSTALS_DIR / "MASTER_COSMOLOGY_CRYSTAL.md",
    CRYSTALS_DIR / "PHARMACEUTICAL_1_CRYSTAL.md",
    CRYSTALS_DIR / "MASTER_PHARMACEUTICAL_1_CRYSTAL.md",
    CRYSTALS_DIR / "PHARMACEUTICAL_2_CRYSTAL.md",
    CRYSTALS_DIR / "MASTER_PHARMACEUTICAL_2_CRYSTAL.md",
    CRYSTALS_DIR / "MASTER_PHARMACEUTICAL_CRYSTAL.md",
    CRYSTALS_DIR / "VOYNICH_FULL_CRYSTAL.md",
]

CANONICAL_OVERVIEW_PATHS = [
    CANONICAL_FULL_TRANSLATION_PATH,
    CANONICAL_FULL_CRYSTAL_PATH,
    CANONICAL_NEURAL_MASTER_PATH,
]

NODE_META: dict[str, dict[str, str]] = {
    "N01": {"name": "Root Canon", "bias": "Fire -> Air"},
    "N02": {"name": "NEW Research Corpus", "bias": "Air -> Earth"},
    "N03": {"name": "EVA Transcription Bedrock", "bias": "Earth -> Air"},
    "N04": {"name": "FRESH Meta-Manuscript Layer", "bias": "Water -> Air"},
    "N05": {"name": "Plant Folio Corpus", "bias": "Fire -> Water"},
    "N06": {"name": "Astrology Folio Corpus", "bias": "Air -> Water"},
    "N07": {"name": "Bath Folio Corpus", "bias": "Water -> Earth"},
    "N08": {"name": "Cosmology Folio Corpus", "bias": "Earth -> Air"},
    "N09": {"name": "Pharmaceutical Folio Corpus", "bias": "Fire -> Earth"},
    "N10": {"name": "Section Synthesis Layer", "bias": "Water -> Earth"},
    "N11": {"name": "Crystal Layer", "bias": "Earth -> Water"},
    "N12": {"name": "Unified Manuscript Layer", "bias": "Earth -> Fire"},
    "N13": {"name": "Framework Runtime", "bias": "Earth -> Air"},
    "N14": {"name": "Math Corpus", "bias": "Air -> Fire"},
    "N15": {"name": "Manifest and Autonomy Layer", "bias": "Earth -> Air"},
    "N16": {"name": "Meta-Engine and Synthesis Layer", "bias": "Air -> Earth"},
}

ATOM_ROWS = [
    ("C", "consonant", "core/contain", ["containment", "boundary", "substrate"], None, "Declare a bounded carrier."),
    ("H", "consonant", "spirit/breath", ["volatilization", "aeration", "motion"], None, "Introduce an active volatile phase."),
    ("D", "consonant", "fix/stabilize", ["fixation", "grounding", "closure"], None, "Lock a state into a stable form."),
    ("T", "consonant", "drive/propel", ["heat", "drive", "projection"], None, "Push the carrier through an active transition."),
    ("K", "consonant", "contain/hold", ["retention", "holding", "vessel"], None, "Hold the active state inside a bounded vessel."),
    ("S", "consonant", "flow/dissolve", ["dissolution", "wash", "transition"], None, "Dissolve or wash the current state."),
    ("Q", "consonant", "retort/cycle", ["recursion", "circulation", "cohobation"], None, "Repeat a cycling transform until a checkpoint is reached."),
    ("P", "consonant", "press/seal", ["pressure", "seal", "compression"], None, "Apply mechanical compression or a pressure seal."),
    ("L", "consonant", "layer/locate", ["location", "structure", "layer"], None, "Place the carrier in a structural position."),
    ("R", "consonant", "rotate/project", ["rotation", "projection", "outlet"], None, "Rotate or expose a carrier through an outlet."),
    ("M", "consonant", "unite/marry", ["conjunction", "merger", "coupling"], None, "Combine two previously distinct states."),
    ("N", "consonant", "close/seal", ["termination", "sealing", "completion"], None, "Terminate a transform and close the route."),
    ("F", "consonant", "form/vegetate", ["growth", "generation", "form"], None, "Generate or grow an organized form."),
    ("G", "consonant", "grade/measure", ["measurement", "gradation", "titration"], None, "Measure or grade the active state."),
    ("A", "vowel", "earth/body", ["body", "fixed matter", "substrate"], "Earth", "Bind work to a grounded substrate."),
    ("O", "vowel", "fire/heat", ["heat", "activation", "thermal energy"], "Fire", "Energize the transform through heat."),
    ("E", "vowel", "air/essence", ["essence", "volatility", "quintessence"], "Air", "Lift work into an essence-bearing carrier."),
    ("I", "vowel", "water/time-cycle", ["cycle", "duration", "timing"], "Water", "Advance the process by a timed cycle."),
    ("Y", "vowel", "quintessence/active", ["activation", "living principle", "receptivity"], "Quintessence", "Mark the state as live, active, or receptive."),
]

MORPHEME_ROWS = [
    ("d", "prefix", "fix or stabilize", ["operator_family:D"], "prefix"),
    ("s", "prefix", "dissolve or flow", ["operator_family:S"], "prefix"),
    ("o", "prefix", "heat or activate", ["operator_family:H"], "prefix"),
    ("qo", "prefix", "circulate or recurse", ["operator_family:Q"], "prefix"),
    ("ot", "prefix", "timed drive", ["operator_family:H", "operator_family:T"], "prefix"),
    ("ok", "prefix", "phase shift in containment", ["operator_family:R", "operator_family:S"], "prefix"),
    ("ch", "prefix", "channel spirit", ["operator_family:T"], "prefix"),
    ("sh", "prefix", "vigorous flow", ["operator_family:S"], "prefix"),
    ("y", "prefix", "receive or activate", ["operator_family:W"], "prefix"),
    ("che", "root", "mercury or volatile spirit", ["operator_family:C"], "root"),
    ("cho", "root", "sulphur or heated soul", ["operator_family:H"], "root"),
    ("cha", "root", "salt or fixed body", ["operator_family:D"], "root"),
    ("al", "root", "structure or matrix", ["operator_family:B"], "root"),
    ("ol", "root", "fluid medium", ["operator_family:S"], "root"),
    ("or", "root", "outlet or source", ["operator_family:G"], "root"),
    ("ar", "root", "root or base", ["operator_family:L"], "root"),
    ("ke", "root", "contained essence", ["operator_family:C", "operator_family:S"], "root"),
    ("te", "root", "driven tincture", ["operator_family:T"], "root"),
    ("cth", "apparatus", "conduit or throat", ["operator_family:T"], "apparatus"),
    ("ckh", "apparatus", "static valve or clamp", ["operator_family:S", "operator_family:V"], "apparatus"),
    ("kch", "apparatus", "rotating valve", ["operator_family:R", "operator_family:S"], "apparatus"),
    ("cph", "apparatus", "pressure vessel", ["operator_family:P"], "apparatus"),
    ("eos", "compound", "heat-saturated essence", ["operator_family:H"], "special"),
    ("ain", "suffix", "single time-step closure", ["operator_family:Q"], "special"),
    ("aiin", "suffix", "double cycle completion", ["operator_family:Q"], "special"),
    ("daiin", "suffix", "fixation checkpoint", ["operator_family:D", "operator_family:Q"], "special"),
    ("daiiin", "suffix", "extended checkpoint", ["operator_family:D", "operator_family:Q"], "special"),
    ("am", "suffix", "chemical union", ["operator_family:M"], "special"),
    ("sy", "compound", "active dissolve", ["operator_family:W", "operator_family:S"], "operator_family"),
    ("sair", "compound", "salt wash cycle", ["operator_family:W", "operator_family:S"], "operator_family"),
    ("yshey", "compound", "active essence transition", ["operator_family:W"], "operator_family"),
    ("dar", "compound", "fixed root", ["operator_family:D", "operator_family:L"], "operator_family"),
    ("chear", "compound", "spirit captured at root", ["operator_family:C", "operator_family:L"], "operator_family"),
    ("sho", "compound", "vigorous heat", ["operator_family:H", "operator_family:S"], "operator_family"),
    ("cthol", "compound", "conduit fluid transfer", ["operator_family:T"], "operator_family"),
    ("chor", "compound", "volatile outlet", ["operator_family:C", "operator_family:G"], "operator_family"),
    ("keey", "compound", "intensified essence", ["operator_family:C"], "operator_family"),
    ("kaiin", "compound", "contained cycle completion", ["operator_family:S", "operator_family:Q"], "operator_family"),
    ("cthar", "compound", "root conduit verification", ["operator_family:T", "operator_family:V"], "operator_family"),
    ("sckhey", "compound", "strong valve check", ["operator_family:S", "operator_family:V"], "operator_family"),
    ("ckhey", "compound", "valve check", ["operator_family:S", "operator_family:V"], "operator_family"),
    ("cthy", "compound", "conduit bind", ["operator_family:B"], "operator_family"),
    ("daicthy", "compound", "earth-conduit binding fix", ["operator_family:B", "operator_family:D"], "operator_family"),
    ("chod", "compound", "volatile bind-fix", ["operator_family:B", "operator_family:D"], "operator_family"),
    ("cfh", "compound", "fire seal", ["operator_family:F"], "operator_family"),
    ("far", "compound", "furnace closure at root", ["operator_family:F"], "operator_family"),
    ("cfhoaiin", "compound", "fire-sealed full cycle", ["operator_family:F", "operator_family:Q"], "operator_family"),
    ("okol", "compound", "contained fluid phase shift", ["operator_family:R", "operator_family:S"], "operator_family"),
    ("okchoy", "compound", "phase-shifted volatile heat", ["operator_family:R", "operator_family:S"], "operator_family"),
    ("dy", "suffix", "fixed active state", ["operator_family:D"], "suffix"),
    ("ey", "suffix", "energized essence state", ["operator_family:W"], "suffix"),
    ("eey", "suffix", "intensified essence state", ["operator_family:W"], "suffix"),
    ("eeey", "suffix", "maximum essence state", ["operator_family:W"], "suffix"),
    ("os", "suffix", "heat saturated state", ["operator_family:H"], "suffix"),
    ("an", "suffix", "terminal closure", ["operator_family:D"], "suffix"),
]

OPERATOR_FAMILY_ROWS = [
    ("W", "wet/prime", "moisten, activate, prime carrier", ["y", "sy", "sair", "yshey"], ["keeps a carrier live or receptive"]),
    ("L", "load substrate", "load base, root, or starting matter", ["ar", "dar", "chear"], ["roots the process in a substrate"]),
    ("H", "heat/drive", "energize, heat, propel transition", ["o", "ot", "sho"], ["raises activation energy"]),
    ("T", "throat transfer", "move through conduit or neck", ["cth", "cht", "cthol"], ["keeps the route explicit through a transfer channel"]),
    ("C", "capture", "catch, collect, retain a fraction", ["kor", "chor", "keey"], ["turns a passing fraction into a held product"]),
    ("S", "seal/contain", "close, hold, clamp, contain", ["k", "ckh", "kos", "kaiin"], ["prevents uncontrolled leakage"]),
    ("V", "verify", "check, repeat-check, validate", ["cthar", "sckhey", "ckhey"], ["adds a checkpoint without inventing a new transform"]),
    ("B", "bind conduit", "bind, ligature, connect and secure line", ["cthy", "daicthy", "chod"], ["locks a transfer path into a stable connection"]),
    ("P", "pressure secure", "place or stabilize in pressure vessel", ["cph", "psh", "cpho"], ["raises pressure without changing route order"]),
    ("F", "fire-seal secure", "hard seal under furnace or active heat", ["cfh", "far", "cfhoaiin"], ["stabilizes a high-heat boundary"]),
    ("R", "recirculate/phase-shift", "rotate, phase-shift, return through circuit", ["ok", "okol", "okchoy"], ["re-enters the route through a contained loop"]),
    ("D", "fix", "stabilize, lock, complete fixation", ["d", "dan", "dal", "shody"], ["ends a live phase in a stable state"]),
    ("Q", "checkpoint", "mark stage complete, certify passage", ["dain", "daiin", "daiiin"], ["explicitly certifies cycle completion"]),
    ("X", "triple-fix", "repeat or intensify fixation", ["dydyd"], ["raises fixation strength through repetition"]),
    ("G", "collect/output gate", "route to final output or discharge gate", ["chtor", "chor", "ro"], ["makes the terminal output legible"]),
    ("M", "conjunction", "join or marry separate carriers", ["am"], ["merges previously distinct states"]),
]

NOTATION_ROWS = [
    ("hybrid_legal_dsl", "legal", "lawful transform packet", "Hybrid legal-process DSL grounded in admissible transforms.", "canonical", None),
    ("json_schema", "code", "JSON Schema", "Machine-checkable schema view.", "canonical", None),
    ("python", "code", "Python function", "Python process sketch.", "canonical", None),
    ("typescript_javascript", "code", "TypeScript/JavaScript function", "Typed JavaScript process sketch.", "canonical", None),
    ("rust", "code", "Rust function", "Rust state transition sketch.", "canonical", None),
    ("c", "code", "C function", "C state transition sketch.", "canonical", None),
    ("cpp", "code", "C++ function", "C++ state transition sketch.", "canonical", None),
    ("java", "code", "Java method", "Java state transition sketch.", "canonical", None),
    ("html", "code", "HTML article", "HTML structural render.", "canonical", None),
    ("react_tsx", "code", "React TSX component", "React component render.", "canonical", None),
    ("pytorch", "code", "PyTorch module", "Tensorized transition view.", "canonical", None),
    ("math_ir", "code", "mathematical intermediate representation", "Normalized operator-chain IR.", "canonical", None),
    ("flow_dsl", "code", "flow graph DSL", "Flow-notation render of the algorithm.", "canonical", None),
    ("vml_ir", "domain", "VML operator packet", "Direct VML process IR.", "canonical", None),
    ("aqm", "domain", "AQM carrier", "AQM line or folio carrier.", "lens", "aqm"),
    ("cut", "domain", "CUT boundary-flow carrier", "CUT boundary-flow carrier.", "lens", "cut"),
    ("liminal", "domain", "liminal regime carrier", "Threshold and fail-space carrier.", "lens", "liminal"),
    ("chemistry", "domain", "chemical composition vector", "Chemistry-native renderer.", "lens", "chemistry"),
    ("biology", "domain", "biological process packet", "Biology-native renderer.", "canonical", None),
    ("physics", "domain", "physical field state", "Physics-native renderer.", "lens", "physics"),
    ("geometry", "domain", "geometric path", "Geometry-native renderer.", "lens", "geometry"),
    ("trigonometry", "domain", "trigonometric phase packet", "Trigonometric phase render.", "canonical", None),
    ("music", "domain", "musical cadence vector", "Music-native renderer.", "lens", "music_theory_math"),
    ("juggling", "domain", "siteswap-like carry pattern", "Juggling renderer.", "lens", "juggling"),
    ("astrology", "domain", "timing and house packet", "Astrological timing renderer.", "canonical", None),
]

MATH_KERNEL_ROWS = [
    ("kernel:aqm_source_space", "AQM Source Space", "rho in T_1(H)", ["H := L^2(C_hat, mu)", "rho in T_1(H), rho >= 0, Tr(rho) = 1", "Phi_f(tau) = Tr_latent(U_f tau U_f*)", "Phi_f^(tot) = Phi_f^(bulk) (+) Phi_f^(bdry)"], ["source formal lens", "line and folio dynamics"]),
    ("kernel:liminal_regime_space", "LM and AQM-Lambda Regime Space", "H_tot = sum(H_r) (+) sum(H_lambda_e) (+) H_fail", ["p(r) = Tr(Pi_r rho)", "ell(e) = Tr(Pi_lambda_e rho)", "f = Tr(Pi_fail rho)", "C_reg(rho) = 0.5 || rho - Delta_B(rho) ||_1"], ["liminal transitions", "boundary handling", "safety checks"]),
    ("kernel:cut_dynamics", "CUT Dynamics", "X_t = (kappa_t, varphi_t, ell_t, b_t)", ["Dkappa/Dt = -dH/dkappa + div(D_kappa grad kappa)", "Phi_kappa(t) = integral(boundary(A_t), J_kappa dot n d_sigma_t)", "Pi_A,f(X) = integral(A, f(K(x), varphi(x), ell(x), b(x)) dnu(x))"], ["routing", "boundary flow", "containment", "flux control"]),
    ("kernel:aetheric_compression", "Aetheric Compression and Addressing", "Expand/Coll over seed space Z*", ["X = Expand(g) (+) r", "g = Coll(X) in Z*", "Coll(Expand(g)) = g", "<dddd>_4 := base4(XX - 1)"], ["seed compression", "address routing", "corpus compression"]),
    ("kernel:conjugacy_transport", "Conjugacy Transport", "f^(T) = T^(-1) o f o T", ["f^(T) = T^(-1) o f o T", "Phi_j^(lambda) = T_lambda^(-1) o Phi_j^(AQM) o T_lambda"], ["cross-domain transport", "typed render conversion"]),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", text.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.lower() or "item"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, sort_keys=True, ensure_ascii=True) for record in records]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def strip_time_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: strip_time_fields(item) for key, item in value.items() if key not in {"generated_at", "exported_at", "validated_at"}}
    if isinstance(value, list):
        return [strip_time_fields(item) for item in value]
    return value


def normalized_sha256(value: Any) -> str:
    normalized = json.dumps(strip_time_fields(value), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def timestamp_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def markdown_cell(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value).strip())
    return text.replace("|", "\\|")


def first_sentence_excerpt(text: str, max_chars: int = 180) -> str:
    plain = re.sub(r"\s+", " ", text.replace("`", "").strip())
    if not plain:
        return ""
    sentence = re.split(r"(?<=[.!?])\s+", plain, maxsplit=1)[0]
    if len(sentence) <= max_chars:
        return sentence
    return sentence[: max_chars - 3].rstrip() + "..."


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    return parser.parse_args()


def load_docs_gate_status() -> dict[str, str]:
    patterns = [
        re.compile(r"Command status:\s*`?(BLOCKED|LIVE|UNKNOWN)`?", re.IGNORECASE),
        re.compile(r"-\s*Command status:\s*`?(BLOCKED|LIVE|UNKNOWN)`?", re.IGNORECASE),
    ]
    for path in DOC_GATE_PATHS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                return {"status": match.group(1).upper(), "path": str(path)}
    return {"status": "UNKNOWN", "path": ""}


def parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def parse_subsections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def parse_bullet_list(text: str) -> list[str]:
    return [raw.strip()[2:].strip() for raw in text.splitlines() if raw.strip().startswith("- ")]


def parse_bullet_key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in parse_bullet_list(text):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        values[key.strip()] = value.strip().strip("`")
    return values


def parse_markdown_table(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|") or line.startswith("| ---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) >= 2 and parts[0] != "Field":
            rows[parts[0]] = parts[1]
    return rows


def extract_first_code_block(text: str) -> str:
    match = re.search(r"```(?:[A-Za-z0-9_+-]*)\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def folio_number_from_name(name: str) -> int:
    match = re.match(r"F(\d{3})", name.upper())
    if not match:
        raise ValueError(f"Cannot parse folio number from {name}")
    return int(match.group(1))


def classify_book(name: str) -> str:
    number = folio_number_from_name(name)
    if number <= 57:
        return "Book I"
    if number <= 74:
        return "Book II"
    if number <= 84:
        return "Book III"
    if number <= 86:
        return "Book IV"
    return "Book V"


def classify_neural_node(rel_path: str) -> str:
    value = rel_path.replace("\\", "/").lower()
    if value.startswith("full_translation/rosetta_machine/"):
        return "N13"
    if value.startswith("full_translation/manuscripts/") or "chapter_11_" in value:
        return "N16"
    if value.startswith("full_translation/math/"):
        return "N14"
    if value.startswith("full_translation/framework/"):
        return "N13"
    if value.startswith("full_translation/manifests/"):
        return "N15"
    if value.startswith("full_translation/unified/"):
        return "N12"
    if value.startswith("full_translation/crystals/"):
        return "N11"
    if value.startswith("full_translation/sections/"):
        return "N10"
    if value.startswith("full_translation/folios/"):
        number = folio_number_from_name(Path(rel_path).name)
        if number <= 57:
            return "N05"
        if number <= 74:
            return "N06"
        if number <= 84:
            return "N07"
        if number <= 86:
            return "N08"
        return "N09"
    if value.startswith("fresh/"):
        return "N04"
    if value.startswith("eva/"):
        return "N03"
    if value.startswith("new/"):
        return "N02"
    return "N01"


def scan_source_documents() -> list[Path]:
    documents: list[Path] = []
    excluded = {
        "full_translation/rosetta_machine/build/",
        "full_translation/rosetta_machine/registries/",
        "full_translation/rosetta_machine/mirrors/",
        "full_translation/rosetta_machine/archive/",
    }
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in DOC_EXTS:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(rel.lower().startswith(prefix) for prefix in excluded):
            continue
        documents.append(path.relative_to(ROOT))
    return sorted(documents)


def build_shared_fields(*, record_id: str, kind: str, source_unit: str, evidence_class: str, confidence: float, docs_gate: str, inputs: list[Any], transform: dict[str, Any], outputs: list[Any], constraints: dict[str, Any], export_targets: list[str], source_refs: list[str]) -> dict[str, Any]:
    return {
        "id": record_id,
        "kind": kind,
        "source_unit": source_unit,
        "evidence_class": evidence_class,
        "confidence": round(confidence, 4),
        "docs_gate": docs_gate,
        "inputs": inputs,
        "transform": transform,
        "outputs": outputs,
        "constraints": constraints,
        "export_targets": export_targets,
        "source_refs": source_refs,
    }


def build_eva_atoms(docs_gate: str) -> list[dict[str, Any]]:
    source_ref = "NEW/working/THE VML ROSETTA STONE.md"
    records: list[dict[str, Any]] = []
    for symbol, atom_class, phoneme, semantic_roles, element, modern_process in ATOM_ROWS:
        records.append(
            {
                **build_shared_fields(
                    record_id=f"eva_atom:{symbol}",
                    kind="eva_atom",
                    source_unit=symbol,
                    evidence_class="direct",
                    confidence=0.96,
                    docs_gate=docs_gate,
                    inputs=[],
                    transform={"semantic_roles": semantic_roles},
                    outputs=[modern_process],
                    constraints={"atomic": True},
                    export_targets=[item[0] for item in NOTATION_ROWS],
                    source_refs=[source_ref],
                ),
                "symbol": symbol,
                "atom_class": atom_class,
                "phoneme": phoneme,
                "semantic_roles": semantic_roles,
                "element": element,
                "modern_process": modern_process,
            }
        )
    return records


def build_morphemes(docs_gate: str) -> list[dict[str, Any]]:
    source_refs = ["NEW/working/THE VML ROSETTA STONE.md", "FULL_TRANSLATION/framework/registry/vml_operator_registry.md"]
    records: list[dict[str, Any]] = []
    for surface, morpheme_class, meaning, operator_family_ids, source_ref_kind in MORPHEME_ROWS:
        records.append(
            {
                **build_shared_fields(
                    record_id=f"morpheme:{morpheme_class}:{surface}",
                    kind="morpheme",
                    source_unit=surface,
                    evidence_class="direct" if source_ref_kind in {"prefix", "root", "suffix", "apparatus", "special"} else "mixed",
                    confidence=0.88,
                    docs_gate=docs_gate,
                    inputs=list(surface),
                    transform={"operator_family_ids": operator_family_ids},
                    outputs=[meaning],
                    constraints={"morpheme_class": morpheme_class},
                    export_targets=[item[0] for item in NOTATION_ROWS],
                    source_refs=source_refs,
                ),
                "surface": surface,
                "morpheme_class": morpheme_class,
                "meaning": meaning,
                "operator_family_ids": operator_family_ids,
                "source_ref_kind": source_ref_kind,
            }
        )
    return records


def build_operator_families(docs_gate: str) -> list[dict[str, Any]]:
    source_ref = "FULL_TRANSLATION/framework/registry/vml_operator_registry.md"
    records: list[dict[str, Any]] = []
    for symbol, family, default_role, token_families, cycle_rules in OPERATOR_FAMILY_ROWS:
        records.append(
            {
                **build_shared_fields(
                    record_id=f"operator_family:{symbol}",
                    kind="operator_family",
                    source_unit=symbol,
                    evidence_class="direct",
                    confidence=0.94,
                    docs_gate=docs_gate,
                    inputs=token_families,
                    transform={"family": family},
                    outputs=[default_role],
                    constraints={"cycle_rules": cycle_rules},
                    export_targets=[item[0] for item in NOTATION_ROWS],
                    source_refs=[source_ref],
                ),
                "symbol": symbol,
                "family": family,
                "default_role": default_role,
                "token_families": token_families,
                "cycle_rules": cycle_rules,
            }
        )
    return records


def build_math_kernels_registry(docs_gate: str) -> list[dict[str, Any]]:
    source_ref = "FULL_TRANSLATION/framework/registry/math_kernel_registry.md"
    return [
        {
            "id": kernel_id,
            "kind": "math_kernel",
            "source_unit": title,
            "evidence_class": "direct",
            "confidence": 0.9,
            "docs_gate": docs_gate,
            "carrier": carrier,
            "equations": equations,
            "uses": uses,
            "source_refs": [source_ref],
        }
        for kernel_id, title, carrier, equations, uses in MATH_KERNEL_ROWS
    ]


def build_lens_carriers_registry(docs_gate: str, lens_registry: dict[str, Any]) -> list[dict[str, Any]]:
    source_refs = ["FULL_TRANSLATION/framework/registry/lenses.json", "FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md"]
    return [
        {
            "id": f"lens_carrier:{lens['id']}",
            "kind": "lens_carrier",
            "source_unit": lens["id"],
            "evidence_class": "direct",
            "confidence": 0.93,
            "docs_gate": docs_gate,
            "display_name": lens["display_name"],
            "class": lens["class"],
            "carrier": lens["carrier"],
            "update_law": lens["update_law"],
            "transport_symbol": lens["transport_symbol"],
            "entry_fields": lens["entry_fields"],
            "source_refs": source_refs,
        }
        for lens in lens_registry["lenses"]
    ]


def build_notation_families_registry(docs_gate: str) -> list[dict[str, Any]]:
    source_refs = [
        "FULL_TRANSLATION/manuscripts/MASTER_VOYNICH_SYNTHESIS_ROSETTA_STONE.md",
        "FULL_TRANSLATION/framework/registry/lenses.json",
        "NEW/working/THE VML ROSETTA STONE.md",
    ]
    return [
        {
            "id": f"notation_family:{notation_id}",
            "kind": "notation_family",
            "source_unit": notation_id,
            "evidence_class": "mixed",
            "confidence": 0.87,
            "docs_gate": docs_gate,
            "notation_id": notation_id,
            "notation_class": notation_class,
            "carrier": carrier,
            "description": description,
            "source_mode": source_mode,
            "lens_id": lens_id,
            "source_refs": source_refs,
        }
        for notation_id, notation_class, carrier, description, source_mode, lens_id in NOTATION_ROWS
    ]


def build_transport_registry(docs_gate: str, lens_registry: dict[str, Any]) -> list[dict[str, Any]]:
    lens_ids = {lens["id"] for lens in lens_registry["lenses"]}
    records: list[dict[str, Any]] = []
    for notation_id, notation_class, carrier, _, source_mode, lens_id in NOTATION_ROWS:
        source_carrier = "canonical_operator_chain"
        transport_law = "canonical packet to target notation"
        if source_mode == "lens" and lens_id in lens_ids:
            source_carrier = "aqm"
            transport_law = f"Phi^(target) = T_{notation_id}^(-1) o Phi^(AQM) o T_{notation_id}"
        records.append(
            {
                **build_shared_fields(
                    record_id=f"notation_transport:{notation_id}",
                    kind="notation_transport",
                    source_unit=notation_id,
                    evidence_class="mixed",
                    confidence=0.86,
                    docs_gate=docs_gate,
                    inputs=[source_carrier],
                    transform={"transport_law": transport_law},
                    outputs=[notation_id],
                    constraints={"no_invented_steps": True},
                    export_targets=[notation_id],
                    source_refs=[
                        "FULL_TRANSLATION/framework/registry/lenses.json",
                        "FULL_TRANSLATION/framework/registry/math_kernel_registry.md",
                        "FULL_TRANSLATION/manuscripts/MASTER_VOYNICH_SYNTHESIS_ROSETTA_STONE.md",
                    ],
                ),
                "notation_id": notation_id,
                "notation_class": notation_class,
                "source_carrier": source_carrier,
                "target_carrier": carrier,
                "transport_law": transport_law,
                "target_fields": [
                    "preconditions",
                    "carrier",
                    "allowed_transform",
                    "boundary_checks",
                    "checkpoint_rule",
                    "completion_rule",
                    "rollback_rule",
                ]
                if notation_id == "hybrid_legal_dsl"
                else ["program", "line_programs", "canonical_chain_digest"],
            }
        )
    return records


def build_neural_attachments_registry(docs_gate: str) -> list[dict[str, Any]]:
    source_refs = ["FULL_TRANSLATION/neural_network/DOCUMENT_NODE_REGISTRY_16.md", "FULL_TRANSLATION/neural_network/PERMUTATION_MATRIX_16X16.md"]
    return [
        {
            "id": f"neural_attachment:{node_id}",
            "kind": "neural_attachment",
            "source_unit": node_id,
            "evidence_class": "direct",
            "confidence": 0.92,
            "docs_gate": docs_gate,
            "node_id": node_id,
            "node_name": meta["name"],
            "bias": meta["bias"],
            "source_refs": source_refs,
        }
        for node_id, meta in NODE_META.items()
    ]


def normalize_eva_token(raw: str) -> str:
    value = raw.strip().strip("-=").strip()
    value = re.sub(r"\{[^}]*\}", "", value)
    value = value.replace("!", "").replace("*", "").replace("%", "")
    return value.lower()


def has_damage(raw: str) -> bool:
    return any(marker in raw for marker in ("*", "!", "{&", "%"))


def tokenize_eva(raw_eva: str) -> list[str]:
    values: list[str] = []
    for part in raw_eva.split("."):
        token = part.strip()
        if token:
            token = token.rstrip("-=")
            if token:
                values.append(token)
    return values


def build_morpheme_lookup(morphemes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["surface"]: item for item in morphemes}


def segment_token(raw_token: str, morpheme_lookup: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = normalize_eva_token(raw_token)
    if not normalized:
        return [{"surface": raw_token, "kind": "opaque_fragment", "known": False}]
    ordered = sorted(morpheme_lookup.keys(), key=len, reverse=True)
    segments: list[dict[str, Any]] = []
    index = 0
    while index < len(normalized):
        match_surface = next((surface for surface in ordered if normalized.startswith(surface, index)), None)
        if match_surface is None:
            segments.append({"surface": normalized[index], "kind": "opaque_fragment", "known": False})
            index += 1
            continue
        morpheme = morpheme_lookup[match_surface]
        segments.append(
            {
                "surface": match_surface,
                "kind": morpheme["morpheme_class"],
                "known": True,
                "morpheme_id": morpheme["id"],
                "operator_family_ids": morpheme["operator_family_ids"],
            }
        )
        index += len(match_surface)
    return segments


def parse_eva_block(section_text: str) -> dict[str, str]:
    block = extract_first_code_block(section_text)
    lines: dict[str, str] = {}
    for raw in block.splitlines():
        line = raw.strip()
        if ":" in line:
            line_id, content = line.split(":", 1)
            lines[line_id.strip()] = content.strip()
    return lines


def parse_direct_ledger(section_text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current_zone = ""
    current: dict[str, Any] | None = None
    for raw in section_text.splitlines():
        line = raw.rstrip()
        if line.startswith("### "):
            current_zone = line[4:].strip()
            continue
        bullet = re.match(r"- `([^`]+)`", line.strip())
        if bullet:
            if current is not None:
                entries.append(current)
            current = {"line_id": bullet.group(1), "zone": current_zone, "eva": "", "literal_chain": "", "operational_english": ""}
            continue
        if current is None:
            continue
        field = re.match(r"\s{2}([A-Za-z -]+):\s*(.*)", line)
        if field:
            key = field.group(1).strip().lower().replace("-", "_").replace(" ", "_")
            if key in current:
                current[key] = field.group(2).strip()
    if current is not None:
        entries.append(current)
    return entries


def parse_lens_entries(section_text: str) -> dict[str, dict[str, dict[str, str]]]:
    results: dict[str, dict[str, dict[str, str]]] = {}
    for lens_name, body in parse_subsections(section_text).items():
        line_map: dict[str, dict[str, str]] = {}
        current_id = ""
        current_fields: dict[str, str] = {}
        current_field = ""
        buffer: list[str] = []
        for raw in body.splitlines():
            line = raw.rstrip("\n")
            bullet = re.match(r"- `([^`]+)`", line.strip())
            if bullet:
                if current_id:
                    if current_field:
                        current_fields[current_field] = "\n".join(buffer).strip()
                    line_map[current_id] = current_fields
                current_id = bullet.group(1)
                current_fields = {}
                current_field = ""
                buffer = []
                continue
            field = re.match(r"\s{2}([A-Za-z /-]+):\s*(.*)", line)
            if field:
                if current_field:
                    current_fields[current_field] = "\n".join(buffer).strip()
                current_field = slugify(field.group(1))
                initial = field.group(2).strip()
                buffer = [initial] if initial else []
                continue
            if current_field:
                trimmed = line[2:] if line.startswith("  ") else line
                buffer.append(trimmed)
        if current_id:
            if current_field:
                current_fields[current_field] = "\n".join(buffer).strip()
            line_map[current_id] = current_fields
        results[lens_name] = line_map
    return results


def resolve_docs_gate() -> dict[str, Any]:
    status = load_docs_gate_status()
    required_files = {path.relative_to(ROOT.parent).as_posix(): path.exists() for path in DOC_GATE_REQUIRED_FILES}
    if status["status"] == "LIVE" and all(required_files.values()):
        effective = "LIVE"
    elif not all(required_files.values()) or status["status"] == "BLOCKED":
        effective = "BLOCKED"
    else:
        effective = status["status"]
    return {
        "status": effective,
        "path": status["path"],
        "required_files": required_files,
    }


def infer_evidence_class(
    *,
    raw_value: str = "",
    literal_chain: str = "",
    operational_english: str = "",
    damaged: bool = False,
    lens_entries: dict[str, dict[str, str]] | None = None,
) -> str:
    texts = [raw_value, literal_chain, operational_english]
    if lens_entries:
        for entry in lens_entries.values():
            texts.extend(str(value) for value in entry.values())
    lowered = " ".join(texts).lower()
    if damaged or "damaged" in lowered or "uncertain" in lowered:
        return "uncertain"
    has_direct = bool(raw_value or literal_chain)
    has_derived = bool(operational_english or lens_entries)
    if has_direct and has_derived:
        return "mixed"
    if has_direct:
        return "direct"
    if has_derived:
        return "derived"
    return "uncertain"


def infer_confidence(
    evidence_class: str,
    *,
    damaged: bool = False,
    literal_chain: str = "",
    operational_english: str = "",
    lens_entries: dict[str, dict[str, str]] | None = None,
) -> float:
    base = {
        "direct": 0.9,
        "mixed": 0.82,
        "derived": 0.72,
        "uncertain": 0.48,
    }.get(evidence_class, 0.5)
    if literal_chain:
        base += 0.03
    if operational_english:
        base += 0.02
    labels: list[str] = []
    if lens_entries:
        for entry in lens_entries.values():
            confidence = entry.get("confidence", "")
            if confidence:
                labels.append(confidence.lower())
    if any("strong" in item for item in labels):
        base += 0.07
    elif any("moderate-high" in item for item in labels):
        base += 0.04
    elif any("moderate" in item for item in labels):
        base += 0.02
    if any("uncertain" in item for item in labels):
        base -= 0.1
    if damaged:
        base -= 0.15
    return round(max(0.05, min(0.99, base)), 4)


def canonical_chain_digest(steps: list[dict[str, Any]]) -> str:
    return normalized_sha256({"canonical_chain": steps})


def build_token_records(
    *,
    folio_id: str,
    line_id: str,
    raw_eva: str,
    morpheme_lookup: dict[str, dict[str, Any]],
    docs_gate: str,
    source_refs: list[str],
    book_id: str,
    neural_node_id: str,
) -> list[dict[str, Any]]:
    export_targets = [item[0] for item in NOTATION_ROWS]
    records: list[dict[str, Any]] = []
    for index, raw_token in enumerate(tokenize_eva(raw_eva), start=1):
        normalized = normalize_eva_token(raw_token)
        damaged = has_damage(raw_token)
        segments = segment_token(raw_token, morpheme_lookup)
        operator_family_ids = sorted({family for segment in segments for family in segment.get("operator_family_ids", [])})
        evidence_class = infer_evidence_class(raw_value=raw_token, damaged=damaged)
        confidence = infer_confidence(evidence_class, damaged=damaged)
        canonical_step = {
            "token": normalized or raw_token.lower(),
            "raw_token": raw_token,
            "operator_family_ids": operator_family_ids,
            "segments": [segment["surface"] for segment in segments],
            "damaged": damaged,
        }
        gloss_parts = ["/".join(step for step in operator_family_ids) or "opaque"]
        if any(segment.get("known") for segment in segments):
            gloss_parts.append(", ".join(segment["surface"] for segment in segments))
        records.append(
            {
                **build_shared_fields(
                    record_id=f"token_instance:{folio_id}:{line_id}:{index}",
                    kind="token_instance",
                    source_unit=f"{folio_id}:{line_id}:{index}",
                    evidence_class=evidence_class,
                    confidence=confidence,
                    docs_gate=docs_gate,
                    inputs=[raw_token],
                    transform={
                        "segments": segments,
                        "operator_family_ids": operator_family_ids,
                    },
                    outputs=[normalized],
                    constraints={
                        "damaged_glyphs_preserved": damaged,
                        "no_invented_steps": True,
                    },
                    export_targets=export_targets,
                    source_refs=source_refs,
                ),
                "folio_id": folio_id,
                "line_id": line_id,
                "book_id": book_id,
                "neural_node_id": neural_node_id,
                "token_index": index,
                "raw_token": raw_token,
                "normalized_token": normalized,
                "damaged": damaged,
                "segments": segments,
                "operator_family_ids": operator_family_ids,
                "canonical_step": canonical_step,
                "process_gloss": " | ".join(gloss_parts),
            }
        )
    return records


def lens_name_to_id(lens_name: str, lens_registry: dict[str, Any]) -> str:
    normalized = slugify(lens_name.replace("'", ""))
    aliases: dict[str, str] = {
        "color_and_light": "color_light",
        "hero_s_journey": "heros_journey",
        "heros_journey": "heros_journey",
    }
    for lens in lens_registry["lenses"]:
        candidates = {
            slugify(lens["id"]),
            slugify(lens["display_name"]),
            slugify(lens["display_name"].replace("'", "")),
        }
        if normalized in candidates:
            return lens["id"]
    return aliases.get(normalized, normalized)


def parse_final_draft(
    path: Path,
    *,
    morphemes: list[dict[str, Any]],
    docs_gate: str,
    lens_registry: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    sections = parse_sections(text)
    folio_id = path.stem.replace("_FINAL_DRAFT", "").upper()
    rel_path = path.relative_to(ROOT).as_posix()
    final_status = parse_bullet_key_values(sections.get("Final Draft Status", ""))
    identity = parse_markdown_table(sections.get("Folio Identity", ""))
    if not identity:
        identity = {
            "Folio": f"`{folio_id.lower()}`",
            "Book": final_status.get("Book", classify_book(folio_id)),
            "Manuscript role": final_status.get("Manuscript role", ""),
        }
    source_stack = parse_bullet_list(sections.get("Source Stack", ""))
    source_refs = [rel_path] + [item for item in source_stack if "/" in item or "\\" in item]
    purpose = sections.get("Purpose", "").strip()
    zero_claim = sections.get("Folio Zero Claim", "").strip()
    visual_grammar = parse_bullet_list(sections.get("Visual Grammar and Codicology", ""))
    core_vml = parse_bullet_list(sections.get(f"Core VML Machinery Active On {folio_id.title()}", "")) or parse_bullet_list(sections.get("Core VML Machinery Active On F1r", "")) or parse_bullet_list(sections.get("Core VML Machinery Active On F2r", ""))
    eva_lines = parse_eva_block(sections.get("Full EVA", ""))
    ledger_entries = {entry["line_id"]: entry for entry in parse_direct_ledger(sections.get("Direct Line-By-Line Literal Ledger", ""))}
    raw_lenses = parse_lens_entries(sections.get("Multilens Translation Atlas", ""))
    neural_node_id = classify_neural_node(rel_path)
    book_id = classify_book(folio_id)
    book_label = final_status.get("Book", identity.get("Book", book_id)).strip("`")
    morpheme_lookup = build_morpheme_lookup(morphemes)
    line_records: list[dict[str, Any]] = []
    token_records: list[dict[str, Any]] = []
    export_targets = [item[0] for item in NOTATION_ROWS]
    operator_counter: Counter[str] = Counter()

    for order, (line_id, raw_eva) in enumerate(eva_lines.items(), start=1):
        ledger = ledger_entries.get(line_id, {})
        literal_chain = ledger.get("literal_chain", "").strip()
        operational_english = ledger.get("operational_english", "").strip()
        zone = ledger.get("zone", "").strip()
        line_lenses: dict[str, dict[str, str]] = {}
        for lens_name, lines in raw_lenses.items():
            if line_id in lines:
                line_lenses[lens_name_to_id(lens_name, lens_registry)] = {
                    "display_name": lens_name,
                    **lines[line_id],
                }
        if not operational_english:
            for entry in line_lenses.values():
                reading = entry.get("reading", "").strip()
                if reading:
                    operational_english = reading
                    break
        line_token_records = build_token_records(
            folio_id=folio_id,
            line_id=line_id,
            raw_eva=raw_eva,
            morpheme_lookup=morpheme_lookup,
            docs_gate=docs_gate,
            source_refs=source_refs,
            book_id=book_id,
            neural_node_id=neural_node_id,
        )
        token_records.extend(line_token_records)
        canonical_chain = [record["canonical_step"] for record in line_token_records]
        operator_family_ids = sorted({family for record in line_token_records for family in record["operator_family_ids"]})
        operator_counter.update(operator_family_ids)
        damaged = has_damage(raw_eva) or "damaged" in literal_chain.lower() or "damaged" in operational_english.lower()
        evidence_class = infer_evidence_class(
            raw_value=raw_eva,
            literal_chain=literal_chain,
            operational_english=operational_english,
            damaged=damaged,
            lens_entries=line_lenses,
        )
        confidence = infer_confidence(
            evidence_class,
            damaged=damaged,
            literal_chain=literal_chain,
            operational_english=operational_english,
            lens_entries=line_lenses,
        )
        line_records.append(
            {
                **build_shared_fields(
                    record_id=f"line_operator_chain:{folio_id}:{line_id}",
                    kind="line_operator_chain",
                    source_unit=f"{folio_id}:{line_id}",
                    evidence_class=evidence_class,
                    confidence=confidence,
                    docs_gate=docs_gate,
                    inputs=[{"carrier": "eva_line", "value": raw_eva}],
                    transform={
                        "canonical_chain_digest": canonical_chain_digest(canonical_chain),
                        "literal_chain": literal_chain,
                        "operational_english": operational_english,
                    },
                    outputs=[operational_english or literal_chain or raw_eva],
                    constraints={
                        "damaged_glyphs_preserved": damaged,
                        "special_case_f001r": folio_id == "F001R",
                        "no_invented_steps": True,
                    },
                    export_targets=export_targets,
                    source_refs=source_refs,
                ),
                "folio_id": folio_id,
                "book_id": book_id,
                "book": book_label,
                "neural_node_id": neural_node_id,
                "line_id": line_id,
                "line_order": order,
                "line_kind": "title" if line_id.startswith("T") else "paragraph",
                "zone": zone,
                "raw_eva": raw_eva,
                "token_count": len(line_token_records),
                "canonical_chain": canonical_chain,
                "canonical_chain_digest": canonical_chain_digest(canonical_chain),
                "operator_family_ids": operator_family_ids,
                "literal_chain": literal_chain,
                "operational_english": operational_english,
                "lenses": line_lenses,
            }
        )

    split_unit = bool(re.match(r"F\d{3}[RV]\d+$", folio_id))
    folio_evidence = "mixed" if line_records else "uncertain"
    if line_records and all(record["evidence_class"] == "direct" for record in line_records):
        folio_evidence = "direct"
    if any(record["evidence_class"] == "uncertain" for record in line_records):
        folio_evidence = "mixed"
    folio_confidence = round(sum(record["confidence"] for record in line_records) / max(1, len(line_records)), 4)
    folio_record = {
        **build_shared_fields(
            record_id=f"folio_algorithm:{folio_id}",
            kind="folio_algorithm",
            source_unit=folio_id,
            evidence_class=folio_evidence,
            confidence=folio_confidence,
            docs_gate=docs_gate,
            inputs=[rel_path],
            transform={
                "zero_claim": zero_claim,
                "line_operator_chain_ids": [record["id"] for record in line_records],
                "operator_family_summary": dict(sorted(operator_counter.items())),
            },
            outputs=[sections.get("Direct Operational Meaning", "").strip() or zero_claim],
            constraints={
                "split_unit_preserved": split_unit,
                "special_case_f001r": folio_id == "F001R",
                "line_count": len(line_records),
            },
            export_targets=export_targets,
            source_refs=source_refs,
        ),
        "folio_id": folio_id,
        "book_id": book_id,
        "book": book_label,
        "neural_node_id": neural_node_id,
        "neural_node_name": NODE_META[neural_node_id]["name"],
        "file_path": rel_path,
        "source_baseline": final_status.get("Source baseline", "").strip("`"),
        "manuscript_role": final_status.get("Manuscript role", "").strip("`"),
        "purpose": purpose,
        "folio_zero_claim": zero_claim,
        "folio_identity": identity,
        "visual_grammar": visual_grammar,
        "core_vml_machinery": core_vml,
        "direct_operational_meaning": sections.get("Direct Operational Meaning", "").strip(),
        "mathematical_extraction": sections.get("Mathematical Extraction", "").strip(),
        "mythic_extraction": sections.get("Mythic Extraction", "").strip(),
        "all_lens_zero_point": sections.get("All-Lens Zero Point", "").strip(),
        "dense_one_sentence_compression": sections.get("Dense One-Sentence Compression", "").strip(),
        "line_ids": [record["line_id"] for record in line_records],
        "line_count": len(line_records),
        "token_count": len(token_records),
        "split_unit": split_unit,
        "source_stack": source_stack,
        "final_draft_status": final_status,
    }
    return folio_record, line_records, token_records


def build_book_algorithms(folio_records: list[dict[str, Any]], docs_gate: str) -> list[dict[str, Any]]:
    order = {"Book I": 1, "Book II": 2, "Book III": 3, "Book IV": 4, "Book V": 5}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for folio in folio_records:
        grouped[folio["book_id"]].append(folio)
    records: list[dict[str, Any]] = []
    export_targets = [item[0] for item in NOTATION_ROWS]
    for book_id in sorted(grouped, key=lambda value: order.get(value, 99)):
        items = sorted(grouped[book_id], key=lambda record: (folio_number_from_name(record["folio_id"]), record["folio_id"]))
        confidence = round(sum(item["confidence"] for item in items) / len(items), 4)
        neural_counts = Counter(item["neural_node_id"] for item in items)
        records.append(
            {
                **build_shared_fields(
                    record_id=f"book_algorithm:{book_id.replace(' ', '_')}",
                    kind="book_algorithm",
                    source_unit=book_id,
                    evidence_class="mixed",
                    confidence=confidence,
                    docs_gate=docs_gate,
                    inputs=[item["folio_id"] for item in items],
                    transform={
                        "ordered_folios": [item["folio_id"] for item in items],
                        "zero_claims": [item["folio_zero_claim"] for item in items if item["folio_zero_claim"]],
                    },
                    outputs=[items[0]["book"]],
                    constraints={"preserve_manuscript_order": True},
                    export_targets=export_targets,
                    source_refs=[item["file_path"] for item in items],
                ),
                "book_id": book_id,
                "book": items[0]["book"],
                "folio_ids": [item["folio_id"] for item in items],
                "folio_count": len(items),
                "line_count": sum(item["line_count"] for item in items),
                "token_count": sum(item["token_count"] for item in items),
                "split_units": [item["folio_id"] for item in items if item["split_unit"]],
                "neural_node_counts": dict(sorted(neural_counts.items())),
            }
        )
    return records


def build_corpus_index(
    *,
    docs_gate_info: dict[str, Any],
    folio_records: list[dict[str, Any]],
    line_records: list[dict[str, Any]],
    token_records: list[dict[str, Any]],
    book_records: list[dict[str, Any]],
    registry_counts: dict[str, int],
) -> dict[str, Any]:
    source_documents = scan_source_documents()
    source_entries: list[dict[str, Any]] = []
    source_node_counts: Counter[str] = Counter()
    for path in source_documents:
        rel_path = path.as_posix()
        node_id = classify_neural_node(rel_path)
        source_node_counts[node_id] += 1
        source_entries.append(
            {
                "path": rel_path,
                "suffix": Path(rel_path).suffix.lower(),
                "node_id": node_id,
                "node_name": NODE_META[node_id]["name"],
            }
        )
    return {
        **build_shared_fields(
            record_id="corpus_index:voynich_rosetta_machine",
            kind="corpus_index",
            source_unit="Voynich Corpus",
            evidence_class="mixed",
            confidence=0.95,
            docs_gate=docs_gate_info["status"],
            inputs=[len(source_entries)],
            transform={"compiled_from": "local corpus only"},
            outputs=[len(folio_records)],
            constraints={"docs_gate_honesty": True},
            export_targets=[item[0] for item in NOTATION_ROWS],
            source_refs=[
                "FULL_TRANSLATION/manifests/CORPUS_BUILD_STATUS.md",
                docs_gate_info["path"],
            ]
            if docs_gate_info["path"]
            else ["FULL_TRANSLATION/manifests/CORPUS_BUILD_STATUS.md"],
        ),
        "source_document_count": len(source_entries),
        "source_documents": source_entries,
        "final_draft_folio_count": len(folio_records),
        "line_operator_chain_count": len(line_records),
        "token_instance_count": len(token_records),
        "book_algorithm_count": len(book_records),
        "split_units": [record["folio_id"] for record in folio_records if record["split_unit"]],
        "book_counts": {record["book_id"]: record["folio_count"] for record in book_records},
        "neural_node_counts": {
            node_id: {
                "name": NODE_META[node_id]["name"],
                "source_documents": source_node_counts.get(node_id, 0),
                "folio_algorithms": sum(1 for record in folio_records if record["neural_node_id"] == node_id),
            }
            for node_id in NODE_META
        },
        "registry_counts": registry_counts,
        "docs_gate_path": docs_gate_info["path"],
        "docs_gate_required_files": docs_gate_info["required_files"],
    }


def render_rosetta_index(
    *,
    manifest: dict[str, Any],
    corpus_index: dict[str, Any],
    book_records: list[dict[str, Any]],
    registry_counts: dict[str, int],
) -> str:
    lines = [
        "# Rosetta Machine Index",
        "",
        f"- Generated: `{manifest['generated_at']}`",
        f"- Docs gate: `{manifest['docs_gate']}`",
        f"- Final-draft folios parsed: `{corpus_index['final_draft_folio_count']}`",
        f"- Line operator chains: `{corpus_index['line_operator_chain_count']}`",
        f"- Token instances: `{corpus_index['token_instance_count']}`",
        f"- Source documents scanned: `{corpus_index['source_document_count']}`",
        "",
        "## Book Algorithms",
        "",
        "| Book | Folios | Lines | Tokens | Split Units |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for record in book_records:
        lines.append(
            f"| `{record['book_id']}` | {record['folio_count']} | {record['line_count']} | {record['token_count']} | {len(record['split_units'])} |"
        )
    lines.extend(
        [
            "",
            "## Registry Counts",
            "",
        ]
    )
    for key, value in sorted(registry_counts.items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Neural Node Coverage",
            "",
            "| Node | Name | Source Docs | Folio Algorithms |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for node_id, data in corpus_index["neural_node_counts"].items():
        lines.append(f"| `{node_id}` | {data['name']} | {data['source_documents']} | {data['folio_algorithms']} |")
    return "\n".join(lines) + "\n"


def render_folio_catalog(folio_records: list[dict[str, Any]]) -> str:
    lines = [
        "# Folio Algorithm Catalog",
        "",
        "| Folio | Book | Lines | Tokens | Node | Confidence | Split Unit |",
        "| --- | --- | ---: | ---: | --- | ---: | --- |",
    ]
    for record in sorted(folio_records, key=lambda item: (folio_number_from_name(item["folio_id"]), item["folio_id"])):
        lines.append(
            f"| `{record['folio_id']}` | {record['book']} | {record['line_count']} | {record['token_count']} | `{record['neural_node_id']}` | {record['confidence']:.2f} | `{record['split_unit']}` |"
        )
    return "\n".join(lines) + "\n"


def schema_paths() -> dict[str, Path]:
    return {
        "eva_atom": SCHEMAS_DIR / "eva_atom.schema.json",
        "morpheme": SCHEMAS_DIR / "morpheme.schema.json",
        "operator_family": SCHEMAS_DIR / "operator_family.schema.json",
        "folio_algorithm": SCHEMAS_DIR / "folio_algorithm.schema.json",
        "notation_export": SCHEMAS_DIR / "notation_export.schema.json",
        "transport_registry": SCHEMAS_DIR / "transport_registry.schema.json",
        "corpus_index": SCHEMAS_DIR / "corpus_index.schema.json",
    }


def build_manifest(name: str, docs_gate_info: dict[str, Any], outputs: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = {
        "name": name,
        "generated_at": now_iso(),
        "docs_gate": docs_gate_info["status"],
        "docs_gate_path": docs_gate_info["path"],
        "docs_gate_required_files": docs_gate_info["required_files"],
        "hashes": {},
        "counts": {},
    }
    for key, value in outputs.items():
        manifest["hashes"][key] = normalized_sha256(value)
        if isinstance(value, list):
            manifest["counts"][key] = len(value)
        else:
            manifest["counts"][key] = 1
    if extra:
        manifest.update(extra)
    return manifest


def load_lens_registry() -> dict[str, Any]:
    return read_json(FRAMEWORK_DIR / "registry" / "lenses.json")


def build_rosetta_machine() -> dict[str, Any]:
    REGISTRIES_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    MIRRORS_DIR.mkdir(parents=True, exist_ok=True)

    docs_gate_info = resolve_docs_gate()
    docs_gate = docs_gate_info["status"]
    lens_registry = load_lens_registry()
    eva_atoms = build_eva_atoms(docs_gate)
    morphemes = build_morphemes(docs_gate)
    operator_families = build_operator_families(docs_gate)
    math_kernels = build_math_kernels_registry(docs_gate)
    lens_carriers = build_lens_carriers_registry(docs_gate, lens_registry)
    notation_families = build_notation_families_registry(docs_gate)
    transport_registry = build_transport_registry(docs_gate, lens_registry)
    neural_attachments = build_neural_attachments_registry(docs_gate)

    folio_paths = sorted(FOLIOS_DIR.glob("*_FINAL_DRAFT.md"), key=lambda path: (folio_number_from_name(path.stem), path.name))
    folio_records: list[dict[str, Any]] = []
    line_records: list[dict[str, Any]] = []
    token_records: list[dict[str, Any]] = []
    for path in folio_paths:
        folio_record, folio_lines, folio_tokens = parse_final_draft(
            path,
            morphemes=morphemes,
            docs_gate=docs_gate,
            lens_registry=lens_registry,
        )
        folio_records.append(folio_record)
        line_records.extend(folio_lines)
        token_records.extend(folio_tokens)

    book_records = build_book_algorithms(folio_records, docs_gate)
    registry_counts = {
        "eva_atoms": len(eva_atoms),
        "morphemes": len(morphemes),
        "operator_families": len(operator_families),
        "math_kernels": len(math_kernels),
        "lens_carriers": len(lens_carriers),
        "notation_families": len(notation_families),
        "transport_registry": len(transport_registry),
        "neural_attachments": len(neural_attachments),
    }
    corpus_index = build_corpus_index(
        docs_gate_info=docs_gate_info,
        folio_records=folio_records,
        line_records=line_records,
        token_records=token_records,
        book_records=book_records,
        registry_counts=registry_counts,
    )

    write_json(REGISTRIES_DIR / "eva_atoms.json", eva_atoms)
    write_json(REGISTRIES_DIR / "morphemes.json", morphemes)
    write_json(REGISTRIES_DIR / "operator_families.json", operator_families)
    write_json(REGISTRIES_DIR / "math_kernels.json", math_kernels)
    write_json(REGISTRIES_DIR / "lens_carriers.json", lens_carriers)
    write_json(REGISTRIES_DIR / "notation_families.json", notation_families)
    write_json(REGISTRIES_DIR / "transport_registry.json", transport_registry)
    write_json(REGISTRIES_DIR / "neural_attachments.json", neural_attachments)
    write_jsonl(BUILD_DIR / "token_instances.jsonl", token_records)
    write_jsonl(BUILD_DIR / "line_operator_chains.jsonl", line_records)
    write_jsonl(BUILD_DIR / "folio_algorithms.jsonl", folio_records)
    write_json(BUILD_DIR / "book_algorithms.json", book_records)
    write_json(BUILD_DIR / "corpus_index.json", corpus_index)

    manifest = build_manifest(
        "rosetta_machine_build",
        docs_gate_info,
        {
            "eva_atoms": eva_atoms,
            "morphemes": morphemes,
            "operator_families": operator_families,
            "math_kernels": math_kernels,
            "lens_carriers": lens_carriers,
            "notation_families": notation_families,
            "transport_registry": transport_registry,
            "neural_attachments": neural_attachments,
            "token_instances": token_records,
            "line_operator_chains": line_records,
            "folio_algorithms": folio_records,
            "book_algorithms": book_records,
            "corpus_index": corpus_index,
        },
        extra={
            "final_draft_folios": len(folio_records),
            "line_operator_chains": len(line_records),
            "token_instances": len(token_records),
            "split_units": [record["folio_id"] for record in folio_records if record["split_unit"]],
            "schema_files": {name: path.relative_to(ROOT).as_posix() for name, path in schema_paths().items()},
        },
    )
    write_json(BUILD_DIR / "rosetta_manifest.json", manifest)
    (MIRRORS_DIR / "ROSETTA_MACHINE_INDEX.md").write_text(
        render_rosetta_index(
            manifest=manifest,
            corpus_index=corpus_index,
            book_records=book_records,
            registry_counts=registry_counts,
        ),
        encoding="utf-8",
    )
    (MIRRORS_DIR / "FOLIO_ALGORITHM_CATALOG.md").write_text(render_folio_catalog(folio_records), encoding="utf-8")
    return {
        "docs_gate": docs_gate,
        "docs_gate_info": docs_gate_info,
        "registry_counts": registry_counts,
        "folio_records": folio_records,
        "line_records": line_records,
        "token_records": token_records,
        "book_records": book_records,
        "corpus_index": corpus_index,
        "manifest": manifest,
    }


def load_core_machine_outputs() -> dict[str, Any]:
    required = {
        "eva_atoms": REGISTRIES_DIR / "eva_atoms.json",
        "morphemes": REGISTRIES_DIR / "morphemes.json",
        "operator_families": REGISTRIES_DIR / "operator_families.json",
        "transport_registry": REGISTRIES_DIR / "transport_registry.json",
        "token_records": BUILD_DIR / "token_instances.jsonl",
        "line_records": BUILD_DIR / "line_operator_chains.jsonl",
        "folio_records": BUILD_DIR / "folio_algorithms.jsonl",
        "book_records": BUILD_DIR / "book_algorithms.json",
        "corpus_index": BUILD_DIR / "corpus_index.json",
        "manifest": BUILD_DIR / "rosetta_manifest.json",
    }
    missing = [path.relative_to(ROOT).as_posix() for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing machine outputs: {', '.join(missing)}")
    return {
        "eva_atoms": read_json(required["eva_atoms"]),
        "morphemes": read_json(required["morphemes"]),
        "operator_families": read_json(required["operator_families"]),
        "transport_registry": read_json(required["transport_registry"]),
        "token_records": read_jsonl(required["token_records"]),
        "line_records": read_jsonl(required["line_records"]),
        "folio_records": read_jsonl(required["folio_records"]),
        "book_records": read_json(required["book_records"]),
        "corpus_index": read_json(required["corpus_index"]),
        "manifest": read_json(required["manifest"]),
    }


def load_machine_outputs() -> dict[str, Any]:
    outputs = load_core_machine_outputs()
    export_manifest_path = BUILD_DIR / "export_manifest.json"
    if not export_manifest_path.exists():
        raise FileNotFoundError(f"Missing machine outputs: {export_manifest_path.relative_to(ROOT).as_posix()}")
    return {
        **outputs,
        "export_manifest": read_json(export_manifest_path),
    }


def compact_line_step(record: dict[str, Any]) -> dict[str, Any]:
    if "canonical_step" in record:
        return record["canonical_step"]
    return {
        "token": record.get("normalized_token", ""),
        "raw_token": record.get("raw_token", ""),
        "operator_family_ids": record.get("operator_family_ids", []),
        "segments": [segment.get("surface", "") for segment in record.get("segments", [])],
        "damaged": record.get("damaged", False),
    }


def render_program(notation_id: str, packet: dict[str, Any]) -> Any:
    source_unit = packet["source_unit"]
    steps = packet["canonical_chain"]
    tokens = [step["token"] for step in steps]
    operators = ["/".join(step["operator_family_ids"]) or "opaque" for step in steps]
    token_chain = " -> ".join(tokens)
    reading = packet.get("operational_english") or packet.get("literal_chain") or token_chain
    func_name = slugify(source_unit)
    damaged = any(step.get("damaged") for step in steps)
    checkpoint_tokens = [token for token in tokens if any(marker in token for marker in ("aiin", "dain", "saiin", "dy", "an"))]

    if notation_id == "hybrid_legal_dsl":
        return {
            "preconditions": f"Admit local-corpus packet {source_unit} with glyph damage preserved={damaged}.",
            "carrier": "canonical_operator_chain",
            "allowed_transform": [f"{token}:{operator}" for token, operator in zip(tokens, operators)],
            "boundary_checks": [
                "do not invent unrecorded steps",
                "preserve witness damage markers",
                "respect recorded token order",
            ],
            "checkpoint_rule": ", ".join(checkpoint_tokens) if checkpoint_tokens else "no explicit checkpoint morpheme recorded",
            "completion_rule": reading,
            "rollback_rule": "revert to the last direct token boundary and keep contradictions visible",
            "provenance": packet["provenance"],
        }
    if notation_id == "vml_ir":
        return {
            "source_unit": source_unit,
            "chain": steps,
            "literal_chain": packet.get("literal_chain", ""),
            "operational_english": packet.get("operational_english", ""),
            "canonical_chain_digest": packet["canonical_chain_digest"],
        }
    if notation_id == "json_schema":
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": source_unit,
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "token": {"type": "string"},
                            "operator_family_ids": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["token", "operator_family_ids"],
                    },
                },
                "reading": {"type": "string"},
                "provenance": {"type": "object"},
            },
            "required": ["steps", "reading", "provenance"],
            "examples": [{"steps": steps, "reading": reading, "provenance": packet["provenance"]}],
        }
    if notation_id == "python":
        return "\n".join(
            [
                f"def {func_name}(state):",
                f"    steps = {json.dumps(tokens, ensure_ascii=True)}",
                f"    return {{'source_unit': {source_unit!r}, 'steps': steps, 'reading': {reading!r}, 'state': state}}",
            ]
        )
    if notation_id == "typescript_javascript":
        return "\n".join(
            [
                f"export function {func_name}(state) {{",
                f"  const steps = {json.dumps(tokens, ensure_ascii=True)};",
                f"  return {{ sourceUnit: {source_unit!r}, steps, reading: {reading!r}, state }};",
                "}",
            ]
        )
    if notation_id == "rust":
        return "\n".join(
            [
                f"fn {func_name}() -> Vec<&'static str> {{",
                f"    vec!{json.dumps(tokens, ensure_ascii=True).replace('[', '[').replace(']', ']')}",
                "}",
            ]
        )
    if notation_id == "c":
        return "\n".join(
            [
                f"const char* {func_name}_steps[] = {json.dumps(tokens, ensure_ascii=True).replace('[', '{').replace(']', '}')};",
                f"const char* {func_name}_reading = {reading!r};",
            ]
        )
    if notation_id == "cpp":
        return "\n".join(
            [
                f"std::vector<std::string> {func_name}() {{",
                f"  return {json.dumps(tokens, ensure_ascii=True)};",
                "}",
            ]
        )
    if notation_id == "java":
        return "\n".join(
            [
                f"List<String> {func_name}() {{",
                f"    return List.of({', '.join(repr(token) for token in tokens)});",
                "}",
            ]
        )
    if notation_id == "html":
        items = "".join(f"<li data-op='{operator}'>{token}</li>" for token, operator in zip(tokens, operators))
        return f"<article data-source='{source_unit}'><h1>{source_unit}</h1><p>{reading}</p><ol>{items}</ol></article>"
    if notation_id == "react_tsx":
        return "\n".join(
            [
                f"export function {func_name.title().replace('_', '')}() {{",
                f"  const steps = {json.dumps(tokens, ensure_ascii=True)};",
                f"  return <section data-source={source_unit!r}><h2>{source_unit}</h2><p>{reading}</p><pre>{{JSON.stringify(steps, null, 2)}}</pre></section>;",
                "}",
            ]
        )
    if notation_id == "pytorch":
        return "\n".join(
            [
                f"class {func_name.title().replace('_', '')}(torch.nn.Module):",
                "    def forward(self, state):",
                f"        steps = {json.dumps(tokens, ensure_ascii=True)}",
                f"        return {{'source_unit': {source_unit!r}, 'steps': steps, 'reading': {reading!r}, 'state': state}}",
            ]
        )
    if notation_id == "math_ir":
        return {
            "carrier": "canonical_operator_chain",
            "source_unit": source_unit,
            "operators": operators,
            "tokens": tokens,
            "digest": packet["canonical_chain_digest"],
        }
    if notation_id == "flow_dsl":
        return f'flow "{source_unit}" {{ "{token_chain}" }}'
    if notation_id in packet.get("lenses", {}):
        return packet["lenses"][notation_id]
    if notation_id == "biology":
        return {"carrier": "biological_process_packet", "stages": tokens, "reading": reading}
    if notation_id == "trigonometry":
        return {"carrier": "phase_packet", "phases": [{"token": token, "phase_index": index + 1} for index, token in enumerate(tokens)]}
    if notation_id == "astrology":
        return {"carrier": "timing_house_packet", "houses": [{"token": token, "house": (index % 12) + 1} for index, token in enumerate(tokens)]}
    return {
        "carrier": notation_id,
        "source_unit": source_unit,
        "tokens": tokens,
        "reading": reading,
        "transport": "derived from canonical operator chain",
    }


def build_notation_export_record(source_record: dict[str, Any], notation_info: tuple[str, str, str, str, str, str | None]) -> dict[str, Any]:
    notation_id, notation_class, carrier, description, _, _ = notation_info
    if "canonical_chain" in source_record:
        canonical_chain = source_record["canonical_chain"]
        source_unit = source_record["source_unit"]
        literal_chain = source_record.get("literal_chain", "")
        operational_english = source_record.get("operational_english", "")
        lenses = source_record.get("lenses", {})
        digest = source_record["canonical_chain_digest"]
    else:
        canonical_chain = [compact_line_step(source_record)]
        source_unit = source_record["source_unit"]
        literal_chain = source_record.get("raw_token", "")
        operational_english = source_record.get("process_gloss", "")
        lenses = {}
        digest = canonical_chain_digest(canonical_chain)
    packet = {
        "source_unit": source_unit,
        "canonical_chain": canonical_chain,
        "canonical_chain_digest": digest,
        "literal_chain": literal_chain,
        "operational_english": operational_english,
        "lenses": lenses,
        "provenance": {
            "evidence_class": source_record["evidence_class"],
            "confidence": source_record["confidence"],
            "docs_gate": source_record["docs_gate"],
            "source_refs": source_record["source_refs"],
        },
    }
    program = render_program(notation_id, packet)
    return {
        **build_shared_fields(
            record_id=f"notation_export:{notation_id}:{slugify(source_unit)}",
            kind="notation_export",
            source_unit=source_unit,
            evidence_class=source_record["evidence_class"],
            confidence=source_record["confidence"],
            docs_gate=source_record["docs_gate"],
            inputs=[source_record["id"]],
            transform={"canonical_chain_digest": digest},
            outputs=[notation_id],
            constraints={"no_invented_steps": True},
            export_targets=[notation_id],
            source_refs=source_record["source_refs"],
        ),
        "notation_id": notation_id,
        "notation_class": notation_class,
        "target_carrier": carrier,
        "description": description,
        "source_record_id": source_record["id"],
        "canonical_chain_digest": digest,
        "program": program,
        "provenance": packet["provenance"],
    }


def load_line_records_grouped() -> dict[str, list[dict[str, Any]]]:
    outputs = load_machine_outputs()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in outputs["line_records"]:
        grouped[record["folio_id"]].append(record)
    return dict(grouped)


def build_roundtrip_examples(token_records: list[dict[str, Any]], line_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required_notations = ["vml_ir", "hybrid_legal_dsl", "json_schema", "python", "rust"]
    samples: list[tuple[str, dict[str, Any]]] = []
    selectors = [
        ("qo_prefix", next(record for record in token_records if record["normalized_token"].startswith("qo"))),
        ("dy_suffix", next(record for record in token_records if record["normalized_token"].endswith("dy"))),
        ("aiin_cycle", next(record for record in token_records if "aiin" in record["normalized_token"])),
        ("damaged_token", next(record for record in token_records if record["damaged"])),
        ("full_line_chain", next(record for record in line_records if not record["constraints"]["damaged_glyphs_preserved"] and len(record["canonical_chain"]) >= 5)),
    ]
    samples.extend(selectors)
    examples: list[dict[str, Any]] = []
    notation_lookup = {item[0]: item for item in NOTATION_ROWS}
    for sample_id, source_record in samples:
        notations = {
            notation_id: build_notation_export_record(source_record, notation_lookup[notation_id])["program"]
            for notation_id in required_notations
        }
        examples.append(
            {
                "sample_id": sample_id,
                "source_record_id": source_record["id"],
                "surface": source_record.get("raw_token", source_record.get("raw_eva", "")),
                "notations": notations,
            }
        )
    return examples


def render_export_summary(exports: list[dict[str, Any]], roundtrip_examples: list[dict[str, Any]], manifest: dict[str, Any]) -> str:
    by_notation = Counter(record["notation_id"] for record in exports)
    lines = [
        "# Notation Export Summary",
        "",
        f"- Generated: `{manifest['generated_at']}`",
        f"- Docs gate: `{manifest['docs_gate']}`",
        f"- Export records: `{len(exports)}`",
        f"- Roundtrip examples: `{len(roundtrip_examples)}`",
        "",
        "## Export Counts",
        "",
    ]
    for notation_id, count in sorted(by_notation.items()):
        lines.append(f"- `{notation_id}`: `{count}`")
    lines.extend(["", "## Roundtrip Samples", ""])
    for example in roundtrip_examples:
        lines.append(f"- `{example['sample_id']}` from `{example['source_record_id']}`")
    return "\n".join(lines) + "\n"


def export_rosetta_notations() -> dict[str, Any]:
    try:
        machine = load_core_machine_outputs()
    except FileNotFoundError:
        build_rosetta_machine()
        machine = load_core_machine_outputs()
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MIRRORS_DIR.mkdir(parents=True, exist_ok=True)
    docs_gate_info = resolve_docs_gate()
    exports = [build_notation_export_record(line_record, notation_info) for line_record in machine["line_records"] for notation_info in NOTATION_ROWS]
    roundtrip_examples = build_roundtrip_examples(machine["token_records"], machine["line_records"])
    write_jsonl(EXPORTS_DIR / "notation_exports.jsonl", exports)
    write_json(EXPORTS_DIR / "roundtrip_examples.json", roundtrip_examples)
    manifest = build_manifest(
        "rosetta_notation_exports",
        docs_gate_info,
        {
            "notation_exports": exports,
            "roundtrip_examples": roundtrip_examples,
        },
        extra={"source_lines": len(machine["line_records"])},
    )
    write_json(BUILD_DIR / "export_manifest.json", manifest)
    (MIRRORS_DIR / "NOTATION_EXPORT_SUMMARY.md").write_text(
        render_export_summary(exports, roundtrip_examples, manifest),
        encoding="utf-8",
    )
    return {
        "exports": exports,
        "roundtrip_examples": roundtrip_examples,
        "manifest": manifest,
    }


def ensure_rosetta_pipeline_outputs() -> dict[str, Any]:
    try:
        load_core_machine_outputs()
    except FileNotFoundError:
        build_rosetta_machine()
    export_paths = [
        BUILD_DIR / "export_manifest.json",
        EXPORTS_DIR / "notation_exports.jsonl",
        EXPORTS_DIR / "roundtrip_examples.json",
    ]
    if not all(path.exists() for path in export_paths):
        export_rosetta_notations()
    return load_machine_outputs()


def build_operator_family_lookup(operator_families: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in operator_families}


def build_manuscript_order_rollup(folio_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, folio in enumerate(sorted(folio_records, key=lambda item: (folio_number_from_name(item["folio_id"]), item["folio_id"])), start=1):
        records.append(
            {
                "manuscript_order": index,
                "folio_id": folio["folio_id"],
                "book_id": folio["book_id"],
                "book": folio["book"],
                "neural_node_id": folio["neural_node_id"],
                "neural_node_name": folio["neural_node_name"],
                "zero_claim": folio["folio_zero_claim"],
                "line_count": folio["line_count"],
                "token_count": folio["token_count"],
                "split_unit": folio["split_unit"],
                "source_file": folio["file_path"],
            }
        )
    return records


def dominant_operator_rows(
    *,
    token_records: list[dict[str, Any]],
    operator_lookup: dict[str, dict[str, Any]],
    limit: int = 8,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    counts: Counter[str] = Counter()
    for token in token_records:
        counts.update(token["operator_family_ids"])
    dominant: list[dict[str, Any]] = []
    for operator_id, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]:
        operator = operator_lookup.get(operator_id, {})
        dominant.append(
            {
                "operator_family_id": operator_id,
                "symbol": operator.get("symbol", operator_id.split(":")[-1]),
                "family": operator.get("family", operator_id),
                "count": count,
            }
        )
    return dominant, dict(sorted(counts.items()))


def build_book_operator_rollup(
    *,
    book_records: list[dict[str, Any]],
    token_records: list[dict[str, Any]],
    operator_families: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    operator_lookup = build_operator_family_lookup(operator_families)
    grouped_tokens: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for token in token_records:
        grouped_tokens[token["book_id"]].append(token)
    records: list[dict[str, Any]] = []
    for book in book_records:
        book_tokens = grouped_tokens.get(book["book_id"], [])
        dominant, counts = dominant_operator_rows(token_records=book_tokens, operator_lookup=operator_lookup)
        records.append(
            {
                "book_id": book["book_id"],
                "book": book["book"],
                "folio_count": book["folio_count"],
                "line_count": book["line_count"],
                "token_count": book["token_count"],
                "split_unit_count": len(book["split_units"]),
                "split_units": book["split_units"],
                "dominant_operator_families": dominant,
                "operator_family_counts": counts,
            }
        )
    dominant, counts = dominant_operator_rows(token_records=token_records, operator_lookup=operator_lookup)
    records.append(
        {
            "book_id": "Corpus",
            "book": "Whole Corpus",
            "folio_count": sum(record["folio_count"] for record in book_records),
            "line_count": sum(record["line_count"] for record in book_records),
            "token_count": sum(record["token_count"] for record in book_records),
            "split_unit_count": sum(len(record["split_units"]) for record in book_records),
            "split_units": [split for record in book_records for split in record["split_units"]],
            "dominant_operator_families": dominant,
            "operator_family_counts": counts,
        }
    )
    return records


def build_neural_node_rollup(
    *,
    folio_records: list[dict[str, Any]],
    line_records: list[dict[str, Any]],
    token_records: list[dict[str, Any]],
    corpus_index: dict[str, Any],
) -> list[dict[str, Any]]:
    folios_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
    lines_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
    tokens_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in folio_records:
        folios_by_node[record["neural_node_id"]].append(record)
    for record in line_records:
        lines_by_node[record["neural_node_id"]].append(record)
    for record in token_records:
        tokens_by_node[record["neural_node_id"]].append(record)
    records: list[dict[str, Any]] = []
    for node_id, data in corpus_index["neural_node_counts"].items():
        node_folios = folios_by_node.get(node_id, [])
        node_lines = lines_by_node.get(node_id, [])
        node_tokens = tokens_by_node.get(node_id, [])
        records.append(
            {
                "node_id": node_id,
                "node_name": data["name"],
                "source_document_count": data["source_documents"],
                "folio_count": len(node_folios),
                "book_coverage": sorted({record["book_id"] for record in node_folios}),
                "rosetta_attachment_counts": {
                    "folios": len(node_folios),
                    "lines": len(node_lines),
                    "tokens": len(node_tokens),
                },
                "split_unit_count": sum(1 for record in node_folios if record["split_unit"]),
                "split_units": [record["folio_id"] for record in node_folios if record["split_unit"]],
            }
        )
    return records


def build_metro_edge_rollup(
    *,
    manuscript_rollup: list[dict[str, Any]],
    transport_registry: list[dict[str, Any]],
    docs_gate: str,
) -> list[dict[str, Any]]:
    transport_by_notation = {record["notation_id"]: record for record in transport_registry}
    records: list[dict[str, Any]] = []
    for row in manuscript_rollup:
        records.append(
            {
                "source_folio": row["folio_id"],
                "source_book": row["book_id"],
                "source_neural_node": row["neural_node_id"],
                "target_kind": "node",
                "target_id": row["neural_node_id"],
                "target_label": row["neural_node_name"],
                "edge_type": "folio_to_node",
                "weight": row["line_count"],
                "count": row["line_count"],
                "provenance": {
                    "derived_from": ["line_operator_chains", "folio_algorithms"],
                    "line_count": row["line_count"],
                    "docs_gate": docs_gate,
                },
            }
        )
        for notation_id, transport in sorted(transport_by_notation.items()):
            records.append(
                {
                    "source_folio": row["folio_id"],
                    "source_book": row["book_id"],
                    "source_neural_node": row["neural_node_id"],
                    "target_kind": "notation",
                    "target_id": notation_id,
                    "target_label": notation_id,
                    "edge_type": "folio_to_notation",
                    "weight": row["line_count"],
                    "count": row["line_count"],
                    "provenance": {
                        "derived_from": ["line_operator_chains", "transport_registry"],
                        "line_count": row["line_count"],
                        "transport_record_id": transport["id"],
                        "docs_gate": transport["docs_gate"],
                    },
                }
            )
    return records


def rel_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_required_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required package input: {rel_path(path)}")
    return path.read_text(encoding="utf-8")


def extract_lead_text(text: str, max_chars: int = 260) -> str:
    for block in re.split(r"\n\s*\n", text.strip()):
        stripped = block.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("- "):
            continue
        return first_sentence_excerpt(stripped, max_chars=max_chars)
    return ""


def build_inline_marker(kind: str, path: Path, phase: str) -> str:
    return f"<!-- {phase} INLINE {kind}: {rel_path(path)} -->"


def render_inlined_markdown_block(kind: str, path: Path, text: str) -> list[str]:
    return [
        build_inline_marker(kind, path, "BEGIN"),
        text.rstrip(),
        build_inline_marker(kind, path, "END"),
        "",
    ]


def extract_inline_sequence(text: str, kind: str) -> list[str]:
    pattern = re.compile(rf"^<!-- BEGIN INLINE {re.escape(kind)}: ([^>]+) -->$", re.MULTILINE)
    return pattern.findall(text)


def build_giant_manuscript_paths() -> dict[str, Path]:
    return {
        "giant_manuscript": GIANT_MANUSCRIPT_PATH,
    }


def build_companion_markdown_paths() -> dict[str, Path]:
    return {
        "master_manuscript_companion": MANUSCRIPT_COMPANION_PATH,
        "crystal_companion": CRYSTAL_COMPANION_PATH,
        "metro_companion": METRO_COMPANION_PATH,
        "node_bridge": NODE_BRIDGE_PATH,
        "integration_status": INTEGRATION_STATUS_PATH,
    }


def render_master_manuscript_companion(
    *,
    manuscript_rollup: list[dict[str, Any]],
    book_rollup: list[dict[str, Any]],
    docs_gate: str,
) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in manuscript_rollup:
        grouped[row["book_id"]].append(row)
    lines = [
        "# Voynich Master Manuscript Rosetta Companion",
        "",
        f"- Docs gate: `{docs_gate}`",
        f"- Folio packets: `{len(manuscript_rollup)}`",
        "",
    ]
    for book_id in ("Book I", "Book II", "Book III", "Book IV", "Book V"):
        rows = grouped.get(book_id, [])
        if not rows:
            continue
        lines.extend(
            [
                f"## {book_id}",
                "",
                "| Folio | Node | Lines | Tokens | Split Unit | Zero Claim |",
                "| --- | --- | ---: | ---: | --- | --- |",
            ]
        )
        for row in rows:
            lines.append(
                f"| `{row['folio_id']}` | `{row['neural_node_id']}` | {row['line_count']} | {row['token_count']} | `{row['split_unit']}` | {row['zero_claim']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Book Machine Summary",
            "",
            "| Book | Folios | Lines | Tokens | Split Units |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        lines.append(
            f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} |"
        )
    return "\n".join(lines) + "\n"


def render_crystal_companion(
    *,
    book_rollup: list[dict[str, Any]],
    manuscript_rollup: list[dict[str, Any]],
    docs_gate: str,
) -> str:
    corpus_row = next(row for row in book_rollup if row["book_id"] == "Corpus")
    split_rows = [row for row in manuscript_rollup if row["split_unit"]]
    dominant = ", ".join(
        f"{item['symbol']}({item['count']})" for item in corpus_row["dominant_operator_families"][:5]
    )
    lines = [
        "# Voynich Full Crystal Rosetta Companion",
        "",
        f"- Docs gate: `{docs_gate}`",
        f"- Whole-corpus zero point: `{corpus_row['folio_count']} folios / {corpus_row['line_count']} lines / {corpus_row['token_count']} tokens`, with dominant operator families `{dominant}`.",
        "",
        "## Book Density",
        "",
        "| Book | Folios | Lines | Tokens | Split Units | Dominant Operators |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        dominant_text = ", ".join(f"{item['symbol']}({item['count']})" for item in row["dominant_operator_families"][:4])
        lines.append(
            f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} | {dominant_text} |"
        )
    lines.extend(
        [
            "",
            "## Whole Corpus Operator Density",
            "",
            "| Operator | Family | Count |",
            "| --- | --- | ---: |",
        ]
    )
    for item in corpus_row["dominant_operator_families"]:
        lines.append(f"| `{item['symbol']}` | {item['family']} | {item['count']} |")
    lines.extend(
        [
            "",
            "## Split Unit Distribution",
            "",
            "| Folio | Book | Node | Lines | Tokens |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in split_rows:
        lines.append(
            f"| `{row['folio_id']}` | `{row['book_id']}` | `{row['neural_node_id']}` | {row['line_count']} | {row['token_count']} |"
        )
    return "\n".join(lines) + "\n"


def render_metro_companion(
    *,
    metro_edges: list[dict[str, Any]],
    docs_gate: str,
) -> str:
    notation_book: Counter[tuple[str, str]] = Counter()
    node_book: Counter[tuple[str, str]] = Counter()
    for edge in metro_edges:
        key = (edge["source_book"], edge["target_id"])
        if edge["target_kind"] == "notation":
            notation_book[key] += edge["weight"]
        else:
            node_book[key] += edge["weight"]
    top_notation = sorted(notation_book.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))[:10]
    top_node = sorted(node_book.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))[:10]
    bottlenecks = sorted(notation_book.items(), key=lambda item: (item[1], item[0][0], item[0][1]))[:10]
    lines = [
        "# Voynich Metro Map Rosetta Companion",
        "",
        f"- Docs gate: `{docs_gate}`",
        f"- Edge packets: `{len(metro_edges)}`",
        "",
        "## Top Book -> Notation Corridors",
        "",
        "| Source Book | Target Notation | Weight |",
        "| --- | --- | ---: |",
    ]
    for (book_id, notation_id), weight in top_notation:
        lines.append(f"| `{book_id}` | `{notation_id}` | {weight} |")
    lines.extend(
        [
            "",
            "## Top Book -> Node Corridors",
            "",
            "| Source Book | Target Node | Weight |",
            "| --- | --- | ---: |",
        ]
    )
    for (book_id, node_id), weight in top_node:
        lines.append(f"| `{book_id}` | `{node_id}` | {weight} |")
    lines.extend(
        [
            "",
            "## Bottlenecks",
            "",
            "| Source Book | Target Notation | Weight |",
            "| --- | --- | ---: |",
        ]
    )
    for (book_id, notation_id), weight in bottlenecks:
        lines.append(f"| `{book_id}` | `{notation_id}` | {weight} |")
    return "\n".join(lines) + "\n"


def render_node_bridge(
    *,
    neural_rollup: list[dict[str, Any]],
    docs_gate: str,
) -> str:
    lines = [
        "# Rosetta Machine Node Bridge",
        "",
        f"- Docs gate: `{docs_gate}`",
        "",
        "| Node | Name | Source Docs | Folios | Lines | Tokens | Books | Split Units |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in neural_rollup:
        books = ", ".join(f"`{book}`" for book in row["book_coverage"]) if row["book_coverage"] else "-"
        lines.append(
            f"| `{row['node_id']}` | {row['node_name']} | {row['source_document_count']} | {row['folio_count']} | {row['rosetta_attachment_counts']['lines']} | {row['rosetta_attachment_counts']['tokens']} | {books} | {row['split_unit_count']} |"
        )
    return "\n".join(lines) + "\n"


def render_integration_status(
    *,
    machine_manifest: dict[str, Any],
    export_manifest: dict[str, Any],
    integration_manifest: dict[str, Any],
    companion_paths: dict[str, Path],
) -> str:
    lines = [
        "# Rosetta Machine Integration Status",
        "",
        f"- Docs gate: `{integration_manifest['docs_gate']}`",
        f"- Core machine manifest hash count: `{len(machine_manifest['hashes'])}`",
        f"- Export manifest hash count: `{len(export_manifest['hashes'])}`",
        f"- Integration manifest hash count: `{len(integration_manifest['hashes'])}`",
        "",
        "## Current Build Counts",
        "",
    ]
    for key, value in sorted(machine_manifest["counts"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Companion Output Inventory",
            "",
        ]
    )
    for key, path in companion_paths.items():
        lines.append(f"- `{key}`: `{rel_path(path)}`")
    lines.extend(
        [
            "",
            "## Last Known Hashes",
            "",
        ]
    )
    for key, digest in sorted(integration_manifest["hashes"].items()):
        lines.append(f"- `{key}`: `{digest}`")
    return "\n".join(lines) + "\n"


def load_companion_outputs() -> dict[str, Any]:
    rollup_paths = {
        "manuscript_order_rollup": CONSUMERS_DIR / "manuscript_order_rollup.json",
        "book_operator_rollup": CONSUMERS_DIR / "book_operator_rollup.json",
        "neural_node_rollup": CONSUMERS_DIR / "neural_node_rollup.json",
        "metro_edge_rollup": CONSUMERS_DIR / "metro_edge_rollup.json",
        "integration_manifest": CONSUMERS_DIR / "integration_manifest.json",
    }
    companion_paths = build_companion_markdown_paths()
    missing = [rel_path(path) for path in [*rollup_paths.values(), *companion_paths.values()] if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing companion outputs: {', '.join(missing)}")
    return {
        "manuscript_order_rollup": read_json(rollup_paths["manuscript_order_rollup"]),
        "book_operator_rollup": read_json(rollup_paths["book_operator_rollup"]),
        "neural_node_rollup": read_json(rollup_paths["neural_node_rollup"]),
        "metro_edge_rollup": read_json(rollup_paths["metro_edge_rollup"]),
        "integration_manifest": read_json(rollup_paths["integration_manifest"]),
        "markdown": {key: path.read_text(encoding="utf-8") for key, path in companion_paths.items()},
        "paths": {**rollup_paths, **companion_paths},
    }


def build_rosetta_companions() -> dict[str, Any]:
    machine = ensure_rosetta_pipeline_outputs()
    CONSUMERS_DIR.mkdir(parents=True, exist_ok=True)
    companion_paths = build_companion_markdown_paths()

    manuscript_rollup = build_manuscript_order_rollup(machine["folio_records"])
    book_rollup = build_book_operator_rollup(
        book_records=machine["book_records"],
        token_records=machine["token_records"],
        operator_families=machine["operator_families"],
    )
    neural_rollup = build_neural_node_rollup(
        folio_records=machine["folio_records"],
        line_records=machine["line_records"],
        token_records=machine["token_records"],
        corpus_index=machine["corpus_index"],
    )
    metro_rollup = build_metro_edge_rollup(
        manuscript_rollup=manuscript_rollup,
        transport_registry=machine["transport_registry"],
        docs_gate=machine["manifest"]["docs_gate"],
    )

    manuscript_md = render_master_manuscript_companion(
        manuscript_rollup=manuscript_rollup,
        book_rollup=book_rollup,
        docs_gate=machine["manifest"]["docs_gate"],
    )
    crystal_md = render_crystal_companion(
        book_rollup=book_rollup,
        manuscript_rollup=manuscript_rollup,
        docs_gate=machine["manifest"]["docs_gate"],
    )
    metro_md = render_metro_companion(
        metro_edges=metro_rollup,
        docs_gate=machine["manifest"]["docs_gate"],
    )
    node_bridge_md = render_node_bridge(
        neural_rollup=neural_rollup,
        docs_gate=machine["manifest"]["docs_gate"],
    )

    write_json(CONSUMERS_DIR / "manuscript_order_rollup.json", manuscript_rollup)
    write_json(CONSUMERS_DIR / "book_operator_rollup.json", book_rollup)
    write_json(CONSUMERS_DIR / "neural_node_rollup.json", neural_rollup)
    write_json(CONSUMERS_DIR / "metro_edge_rollup.json", metro_rollup)
    MANUSCRIPT_COMPANION_PATH.write_text(manuscript_md, encoding="utf-8")
    CRYSTAL_COMPANION_PATH.write_text(crystal_md, encoding="utf-8")
    METRO_COMPANION_PATH.write_text(metro_md, encoding="utf-8")
    NODE_BRIDGE_PATH.write_text(node_bridge_md, encoding="utf-8")

    integration_manifest = build_manifest(
        "rosetta_machine_integration_companions",
        resolve_docs_gate(),
        {
            "manuscript_order_rollup": manuscript_rollup,
            "book_operator_rollup": book_rollup,
            "neural_node_rollup": neural_rollup,
            "metro_edge_rollup": metro_rollup,
            "master_manuscript_companion": manuscript_md,
            "crystal_companion": crystal_md,
            "metro_companion": metro_md,
            "node_bridge": node_bridge_md,
        },
        extra={
            "companion_output_inventory": {key: rel_path(path) for key, path in companion_paths.items()},
        },
    )
    status_md = render_integration_status(
        machine_manifest=machine["manifest"],
        export_manifest=machine["export_manifest"],
        integration_manifest=integration_manifest,
        companion_paths=companion_paths,
    )
    integration_manifest["companion_output_inventory"]["integration_status"] = rel_path(INTEGRATION_STATUS_PATH)
    integration_manifest["hashes"]["integration_status"] = normalized_sha256(status_md)
    integration_manifest["counts"]["integration_status"] = 1
    write_json(CONSUMERS_DIR / "integration_manifest.json", integration_manifest)
    INTEGRATION_STATUS_PATH.write_text(status_md, encoding="utf-8")
    return {
        "manuscript_order_rollup": manuscript_rollup,
        "book_operator_rollup": book_rollup,
        "neural_node_rollup": neural_rollup,
        "metro_edge_rollup": metro_rollup,
        "integration_manifest": integration_manifest,
        "companion_paths": companion_paths,
    }


def build_canonical_promotion_paths() -> dict[str, Path]:
    return {
        "voynich_full_translation": CANONICAL_FULL_TRANSLATION_PATH,
        "voynich_master_manuscript": CANONICAL_MASTER_MANUSCRIPT_PATH,
        "voynich_full_crystal": CANONICAL_FULL_CRYSTAL_PATH,
        "voynich_metro_map_working": CANONICAL_METRO_MAP_PATH,
        "master_neural_synthesis": CANONICAL_NEURAL_MASTER_PATH,
    }


def group_manuscript_rollup_by_book(manuscript_rollup: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in manuscript_rollup:
        grouped[row["book_id"]].append(row)
    return dict(grouped)


def format_dominant_operator_text(items: list[dict[str, Any]], limit: int = 5) -> str:
    return ", ".join(f"{item['symbol']}({item['count']})" for item in items[:limit]) or "-"


def summarize_metro_corridors(
    *,
    metro_edges: list[dict[str, Any]],
    transport_registry: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    notation_book: Counter[tuple[str, str]] = Counter()
    node_book: Counter[tuple[str, str, str]] = Counter()
    transport_lookup = {record["notation_id"]: record for record in transport_registry}
    for edge in metro_edges:
        if edge["target_kind"] == "notation":
            notation_book[(edge["source_book"], edge["target_id"])] += edge["weight"]
        else:
            node_book[(edge["source_book"], edge["target_id"], edge["target_label"])] += edge["weight"]
    top_notation = [
        {
            "source_book": book_id,
            "target_notation": notation_id,
            "notation_class": transport_lookup[notation_id]["notation_class"],
            "target_carrier": transport_lookup[notation_id]["target_carrier"],
            "weight": weight,
        }
        for (book_id, notation_id), weight in sorted(notation_book.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))[:10]
    ]
    top_node = [
        {
            "source_book": book_id,
            "target_node": node_id,
            "target_label": label,
            "weight": weight,
        }
        for (book_id, node_id, label), weight in sorted(node_book.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))[:10]
    ]
    bottlenecks = [
        {
            "source_book": book_id,
            "target_notation": notation_id,
            "notation_class": transport_lookup[notation_id]["notation_class"],
            "target_carrier": transport_lookup[notation_id]["target_carrier"],
            "weight": weight,
        }
        for (book_id, notation_id), weight in sorted(notation_book.items(), key=lambda item: (item[1], item[0][0], item[0][1]))[:10]
    ]
    return {
        "top_notation": top_notation,
        "top_node": top_node,
        "bottlenecks": bottlenecks,
    }


def render_canonical_full_translation(
    *,
    manuscript_rollup: list[dict[str, Any]],
    book_rollup: list[dict[str, Any]],
    machine_manifest: dict[str, Any],
    export_manifest: dict[str, Any],
    docs_gate: str,
) -> str:
    grouped = group_manuscript_rollup_by_book(manuscript_rollup)
    corpus_row = next(row for row in book_rollup if row["book_id"] == "Corpus")
    lines = [
        "# Voynich Full Translation",
        "",
        "This canonical surface is now machine-backed. It packages the full corpus in manuscript order without inlining full folio bodies, while preserving the final-draft folios as the detailed witness layer.",
        "",
        f"- Docs gate: `{docs_gate}`",
        f"- Final-draft folios: `{len(manuscript_rollup)}`",
        f"- Line operator chains: `{machine_manifest['line_operator_chains']}`",
        f"- Token instances: `{machine_manifest['token_instances']}`",
        f"- Notation exports: `{export_manifest['counts']['notation_exports']}`",
        f"- Companion witness: `{rel_path(MANUSCRIPT_COMPANION_PATH)}`",
        "",
        "## Renderer Legend",
        "",
        "- `final-draft folio`: authoritative local witness with direct EVA, line ledgers, and full zero-claim prose.",
        "- `machine atlas`: manuscript-order index generated from compiled folio, line, token, and book records.",
        "- `notation export`: deterministic transport of the canonical operator chain into legal, code, math, and domain carriers.",
        "- `docs gate`: still `BLOCKED`, so this promotion remains local-corpus-grounded rather than live-Google-Docs-grounded.",
        "",
        "## Corpus Book Totals",
        "",
        "| Book | Folios | Lines | Tokens | Split Units | Dominant Operators |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        lines.append(
            f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} | {markdown_cell(format_dominant_operator_text(row['dominant_operator_families'], 4))} |"
        )
    lines.extend(
        [
            "",
            f"The whole-corpus atlas currently resolves to `{corpus_row['folio_count']}` folios, `{corpus_row['line_count']}` lines, and `{corpus_row['token_count']}` tokens, with the strongest operator pressure in `{format_dominant_operator_text(corpus_row['dominant_operator_families'], 5)}`.",
            "",
        ]
    )
    for book_id in ("Book I", "Book II", "Book III", "Book IV", "Book V"):
        rows = grouped.get(book_id, [])
        if not rows:
            continue
        lines.extend(
            [
                f"## {markdown_cell(rows[0]['book'])}",
                "",
                "| Folio | Order | Node | Lines | Tokens | Split Unit | Final Draft | Atlas Claim |",
                "| --- | ---: | --- | ---: | ---: | --- | --- | --- |",
            ]
        )
        for row in rows:
            lines.append(
                f"| `{row['folio_id']}` | {row['manuscript_order']} | `{row['neural_node_id']}` | {row['line_count']} | {row['token_count']} | `{row['split_unit']}` | `{row['source_file']}` | {markdown_cell(first_sentence_excerpt(row['zero_claim']))} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Evidence Layers",
            "",
            f"- Companion manuscript packets: `{rel_path(MANUSCRIPT_COMPANION_PATH)}`",
            f"- Crystal companion: `{rel_path(CRYSTAL_COMPANION_PATH)}`",
            f"- Metro companion: `{rel_path(METRO_COMPANION_PATH)}`",
            f"- Neural bridge: `{rel_path(NODE_BRIDGE_PATH)}`",
            f"- Integration status: `{rel_path(INTEGRATION_STATUS_PATH)}`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_canonical_master_manuscript(
    *,
    manuscript_rollup: list[dict[str, Any]],
    book_rollup: list[dict[str, Any]],
    docs_gate: str,
) -> str:
    grouped = group_manuscript_rollup_by_book(manuscript_rollup)
    corpus_row = next(row for row in book_rollup if row["book_id"] == "Corpus")
    lines = [
        "# Voynich Master Manuscript",
        "",
        "Packaging rule: this canonical master packages the local final-draft folios in manuscript order, keeps split folio units first-class, and refuses to invent prose beyond the compiled zero-claim surface already present in the Rosetta machine.",
        "",
        f"- Docs gate: `{docs_gate}`",
        f"- Folio packets: `{len(manuscript_rollup)}`",
        f"- Whole-corpus machine zero point: `{corpus_row['folio_count']} folios / {corpus_row['line_count']} lines / {corpus_row['token_count']} tokens`",
        f"- Lower-level witness: `{rel_path(MANUSCRIPT_COMPANION_PATH)}`",
        "",
        "## Whole-Corpus Machine Summary",
        "",
        "| Book | Folios | Lines | Tokens | Split Units | Dominant Operators |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in book_rollup:
        lines.append(
            f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} | {markdown_cell(format_dominant_operator_text(row['dominant_operator_families'], 5))} |"
        )
    lines.append("")
    for book_id in ("Book I", "Book II", "Book III", "Book IV", "Book V"):
        rows = grouped.get(book_id, [])
        if not rows:
            continue
        book_row = next(row for row in book_rollup if row["book_id"] == book_id)
        lines.extend(
            [
                f"## {markdown_cell(rows[0]['book'])}",
                "",
                f"{book_id} currently packages `{book_row['folio_count']}` folios, `{book_row['line_count']}` lines, and `{book_row['token_count']}` tokens. Its strongest operator density is `{format_dominant_operator_text(book_row['dominant_operator_families'], 5)}`.",
                "",
                "| Folio | Order | Node | Lines | Tokens | Split Unit | Final Draft | Zero Claim |",
                "| --- | ---: | --- | ---: | ---: | --- | --- | --- |",
            ]
        )
        for row in rows:
            lines.append(
                f"| `{row['folio_id']}` | {row['manuscript_order']} | `{row['neural_node_id']}` | {row['line_count']} | {row['token_count']} | `{row['split_unit']}` | `{row['source_file']}` | {markdown_cell(row['zero_claim'])} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Witness Layers",
            "",
            f"- Machine companion packets remain published at `{rel_path(MANUSCRIPT_COMPANION_PATH)}`.",
            f"- Final-draft folio files remain the detailed line-by-line authorities under `FULL_TRANSLATION/folios/`.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_canonical_full_crystal(
    *,
    manuscript_rollup: list[dict[str, Any]],
    book_rollup: list[dict[str, Any]],
    operator_families: list[dict[str, Any]],
    docs_gate: str,
) -> str:
    operator_lookup = build_operator_family_lookup(operator_families)
    corpus_row = next(row for row in book_rollup if row["book_id"] == "Corpus")
    split_rows = [row for row in manuscript_rollup if row["split_unit"]]
    strongest_book = max((row for row in book_rollup if row["book_id"] != "Corpus"), key=lambda item: item["line_count"])
    operator_rows = sorted(corpus_row["operator_family_counts"].items(), key=lambda item: (-item[1], item[0]))
    lines = [
        "# Voynich Full Crystal",
        "",
        "Six-job framing: state the corpus zero point, measure the book densities, expose the operator field, preserve split-unit geometry, compress the whole-corpus attractor, and restate the evidence surfaces that keep the crystal honest.",
        "",
        "## Job 1: Corpus State",
        "",
        f"The machine-promoted crystal is grounded in `{corpus_row['folio_count']}` folios, `{corpus_row['line_count']}` lines, and `{corpus_row['token_count']}` tokens. Docs gate remains `{docs_gate}`, so the crystal is still local-corpus-grounded.",
        "",
        "## Job 2: Book Density Ledger",
        "",
        "| Book | Folios | Lines | Tokens | Split Units | Dominant Operators |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        lines.append(
            f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} | {markdown_cell(format_dominant_operator_text(row['dominant_operator_families'], 5))} |"
        )
    lines.extend(
        [
            "",
            "## Job 3: Whole-Corpus Operator Density",
            "",
            "| Operator | Family | Count |",
            "| --- | --- | ---: |",
        ]
    )
    for operator_id, count in operator_rows:
        operator = operator_lookup.get(operator_id, {})
        lines.append(f"| `{operator.get('symbol', operator_id.split(':')[-1])}` | {markdown_cell(operator.get('family', operator_id))} | {count} |")
    lines.extend(
        [
            "",
            "## Job 4: Split-Unit Distribution",
            "",
            "| Folio | Book | Node | Lines | Tokens |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in split_rows:
        lines.append(
            f"| `{row['folio_id']}` | `{row['book_id']}` | `{row['neural_node_id']}` | {row['line_count']} | {row['token_count']} |"
        )
    lines.extend(
        [
            "",
            "## Job 5: Whole-Corpus Zero Point",
            "",
            f"The present attractor is not abstract. The heaviest line-density book is `{strongest_book['book_id']}` with `{strongest_book['line_count']}` lines, while the whole corpus resolves first through `{format_dominant_operator_text(corpus_row['dominant_operator_families'], 5)}` and preserves `{corpus_row['split_unit_count']}` split folio units as non-mergeable structure.",
            "",
            "## Job 6: Evidence Surfaces",
            "",
            f"- Companion crystal witness: `{rel_path(CRYSTAL_COMPANION_PATH)}`",
            f"- Master manuscript companion: `{rel_path(MANUSCRIPT_COMPANION_PATH)}`",
            f"- Integration status: `{rel_path(INTEGRATION_STATUS_PATH)}`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_canonical_metro_map(
    *,
    metro_edges: list[dict[str, Any]],
    transport_registry: list[dict[str, Any]],
    docs_gate: str,
) -> str:
    summary = summarize_metro_corridors(metro_edges=metro_edges, transport_registry=transport_registry)
    lines = [
        "# Voynich Metro Map Working",
        "",
        "This working metro surface is now machine-current. Every corridor shown below is derived only from recorded line operator chains plus the transport registry; no corridor is hand-invented.",
        "",
        f"- Docs gate: `{docs_gate}`",
        f"- Edge packets: `{len(metro_edges)}`",
        f"- Companion witness: `{rel_path(METRO_COMPANION_PATH)}`",
        "",
        "## Metro Principles",
        "",
        "- Corridor weights come from recorded line counts, not from hand-ranked symbolism.",
        "- Notation routes are lawful fan-outs through the transport registry, so ties within a book are expected.",
        "- Node routes are the manuscript-to-neural attachments already recorded by the Rosetta machine.",
        "",
        "## Top Book -> Notation Corridors",
        "",
        "| Source Book | Target Notation | Class | Carrier | Weight |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for row in summary["top_notation"]:
        lines.append(
            f"| `{row['source_book']}` | `{row['target_notation']}` | `{row['notation_class']}` | {markdown_cell(row['target_carrier'])} | {row['weight']} |"
        )
    lines.extend(
        [
            "",
            "## Top Book -> Node Corridors",
            "",
            "| Source Book | Target Node | Node Label | Weight |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for row in summary["top_node"]:
        lines.append(
            f"| `{row['source_book']}` | `{row['target_node']}` | {markdown_cell(row['target_label'])} | {row['weight']} |"
        )
    lines.extend(
        [
            "",
            "## Bottlenecks",
            "",
            "| Source Book | Target Notation | Class | Carrier | Weight |",
            "| --- | --- | --- | --- | ---: |",
        ]
    )
    for row in summary["bottlenecks"]:
        lines.append(
            f"| `{row['source_book']}` | `{row['target_notation']}` | `{row['notation_class']}` | {markdown_cell(row['target_carrier'])} | {row['weight']} |"
        )
    lines.extend(
        [
            "",
            "## Corridor Notes",
            "",
            "Because the current transport layer exports each recorded line-chain into every notation family, notation corridors tie at the source-book line total. This is not a bug in the metro: it is the current lawful transport geometry of the Rosetta compiler.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_canonical_neural_master(
    *,
    neural_rollup: list[dict[str, Any]],
    corpus_index: dict[str, Any],
    docs_gate: str,
) -> str:
    active_nodes = [row for row in neural_rollup if row["folio_count"] > 0]
    dormant_nodes = [row for row in neural_rollup if row["folio_count"] == 0]
    lines = [
        "# Master Neural Synthesis",
        "",
        "The Voynich neural field stays organized as a 16-node lattice, but this canonical surface is now pinned to machine counts instead of hand-maintained totals.",
        "",
        f"- Docs gate: `{docs_gate}`",
        f"- Source documents scanned: `{corpus_index['source_document_count']}`",
        f"- Final-draft folios attached: `{corpus_index['final_draft_folio_count']}`",
        f"- Line operator chains attached: `{corpus_index['line_operator_chain_count']}`",
        f"- Token instances attached: `{corpus_index['token_instance_count']}`",
        f"- Lower-level node bridge: `{rel_path(NODE_BRIDGE_PATH)}`",
        "",
        "## 16-Node Field",
        "",
        "| Node | Name | Source Docs | Folios | Lines | Tokens | Books | Split Units |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in neural_rollup:
        books = ", ".join(f"`{book}`" for book in row["book_coverage"]) if row["book_coverage"] else "-"
        lines.append(
            f"| `{row['node_id']}` | {markdown_cell(row['node_name'])} | {row['source_document_count']} | {row['folio_count']} | {row['rosetta_attachment_counts']['lines']} | {row['rosetta_attachment_counts']['tokens']} | {books} | {row['split_unit_count']} |"
        )
    lines.extend(
        [
            "",
            "## Active Rosetta Frontier",
            "",
            f"The live folio field currently occupies `{len(active_nodes)}` nodes: "
            + ", ".join(
                f"`{row['node_id']}` ({row['folio_count']} folios / {row['rosetta_attachment_counts']['lines']} lines)"
                for row in active_nodes
            )
            + ".",
            "",
            "## Support and Runtime Layer",
            "",
            f"The remaining `{len(dormant_nodes)}` nodes currently act as support, registry, crystal, unified, manifest, math, and meta-engine layers. They still matter to the field because they carry `{sum(row['source_document_count'] for row in dormant_nodes)}` local documents even when they attach zero folio algorithms directly.",
            "",
            "## Current Frontier",
            "",
            "N05 through N09 remain the direct folio-bearing band of the lattice, while N01 through N04 and N10 through N16 remain upstream and downstream support surfaces. The docs gate is still blocked, so this frontier is an honest local-corpus synthesis rather than a live Google Docs merge.",
        ]
    )
    return "\n".join(lines) + "\n"


def load_canonical_promotion_outputs() -> dict[str, Any]:
    canonical_paths = build_canonical_promotion_paths()
    required_paths = {**canonical_paths, "canonical_promotion_manifest": CANONICAL_PROMOTION_MANIFEST_PATH}
    missing = [rel_path(path) for path in required_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing canonical promotion outputs: {', '.join(missing)}")
    return {
        "manifest": read_json(CANONICAL_PROMOTION_MANIFEST_PATH),
        "markdown": {key: path.read_text(encoding="utf-8") for key, path in canonical_paths.items()},
        "paths": canonical_paths,
    }


def build_promotion_snapshot_manifest(
    *,
    snapshot_dir: Path,
    canonical_paths: dict[str, Path],
    docs_gate_info: dict[str, Any],
) -> dict[str, Any]:
    archived_files: list[dict[str, Any]] = []
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for key, path in canonical_paths.items():
        archive_path = snapshot_dir / path.relative_to(FULL_TRANSLATION)
        exists = path.exists()
        content = path.read_text(encoding="utf-8") if exists else ""
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(content, encoding="utf-8")
        archived_files.append(
            {
                "target_key": key,
                "target_path": rel_path(path),
                "archived_path": rel_path(archive_path),
                "pre_overwrite_exists": exists,
                "pre_overwrite_sha256": sha256_text(content),
                "pre_overwrite_bytes": len(content.encode("utf-8")),
            }
        )
    snapshot_manifest = {
        "name": "rosetta_machine_promotion_snapshot",
        "generated_at": now_iso(),
        "docs_gate": docs_gate_info["status"],
        "docs_gate_path": docs_gate_info["path"],
        "docs_gate_required_files": docs_gate_info["required_files"],
        "archive_root": rel_path(snapshot_dir),
        "archived_files": archived_files,
    }
    write_json(snapshot_dir / "promotion_snapshot_manifest.json", snapshot_manifest)
    return snapshot_manifest


def build_rosetta_canonical_promotion() -> dict[str, Any]:
    machine = ensure_rosetta_pipeline_outputs()
    try:
        companions = load_companion_outputs()
    except FileNotFoundError:
        build_rosetta_companions()
        companions = load_companion_outputs()

    canonical_paths = build_canonical_promotion_paths()
    docs_gate_info = resolve_docs_gate()
    markdown_outputs = {
        "voynich_full_translation": render_canonical_full_translation(
            manuscript_rollup=companions["manuscript_order_rollup"],
            book_rollup=companions["book_operator_rollup"],
            machine_manifest=machine["manifest"],
            export_manifest=machine["export_manifest"],
            docs_gate=machine["manifest"]["docs_gate"],
        ),
        "voynich_master_manuscript": render_canonical_master_manuscript(
            manuscript_rollup=companions["manuscript_order_rollup"],
            book_rollup=companions["book_operator_rollup"],
            docs_gate=machine["manifest"]["docs_gate"],
        ),
        "voynich_full_crystal": render_canonical_full_crystal(
            manuscript_rollup=companions["manuscript_order_rollup"],
            book_rollup=companions["book_operator_rollup"],
            operator_families=machine["operator_families"],
            docs_gate=machine["manifest"]["docs_gate"],
        ),
        "voynich_metro_map_working": render_canonical_metro_map(
            metro_edges=companions["metro_edge_rollup"],
            transport_registry=machine["transport_registry"],
            docs_gate=machine["manifest"]["docs_gate"],
        ),
        "master_neural_synthesis": render_canonical_neural_master(
            neural_rollup=companions["neural_node_rollup"],
            corpus_index=machine["corpus_index"],
            docs_gate=machine["manifest"]["docs_gate"],
        ),
    }

    existing_manifest = read_json(CANONICAL_PROMOTION_MANIFEST_PATH) if CANONICAL_PROMOTION_MANIFEST_PATH.exists() else None
    current_texts = {key: read_text_if_exists(path) for key, path in canonical_paths.items()}
    changed_keys = [key for key, text in markdown_outputs.items() if current_texts.get(key, "") != text]
    snapshot_manifest = None
    archive_snapshot_path = existing_manifest.get("archive_snapshot_path") if existing_manifest else None
    archive_snapshot_manifest = existing_manifest.get("archive_snapshot_manifest") if existing_manifest else None

    if changed_keys:
        snapshot_dir = ARCHIVE_DIR / timestamp_z()
        snapshot_manifest = build_promotion_snapshot_manifest(
            snapshot_dir=snapshot_dir,
            canonical_paths=canonical_paths,
            docs_gate_info=docs_gate_info,
        )
        archive_snapshot_path = rel_path(snapshot_dir)
        archive_snapshot_manifest = rel_path(snapshot_dir / "promotion_snapshot_manifest.json")
        for key, path in canonical_paths.items():
            path.write_text(markdown_outputs[key], encoding="utf-8")

    manifest = build_manifest(
        "rosetta_machine_canonical_promotion",
        docs_gate_info,
        markdown_outputs,
        extra={
            "canonical_output_inventory": {key: rel_path(path) for key, path in canonical_paths.items()},
            "archive_snapshot_path": archive_snapshot_path,
            "archive_snapshot_manifest": archive_snapshot_manifest,
        },
    )
    write_json(CANONICAL_PROMOTION_MANIFEST_PATH, manifest)
    return {
        "manifest": manifest,
        "markdown": markdown_outputs,
        "paths": canonical_paths,
        "archive_snapshot_path": archive_snapshot_path,
        "archive_snapshot_manifest": archive_snapshot_manifest,
        "snapshot_created": snapshot_manifest is not None,
    }


def load_giant_manuscript_outputs() -> dict[str, Any]:
    giant_paths = build_giant_manuscript_paths()
    required_paths = {**giant_paths, "giant_manuscript_manifest": GIANT_MANUSCRIPT_MANIFEST_PATH}
    missing = [rel_path(path) for path in required_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing giant manuscript outputs: {', '.join(missing)}")
    return {
        "manifest": read_json(GIANT_MANUSCRIPT_MANIFEST_PATH),
        "markdown": {key: path.read_text(encoding="utf-8") for key, path in giant_paths.items()},
        "paths": giant_paths,
    }


def build_giant_manuscript_snapshot_manifest(
    *,
    snapshot_dir: Path,
    giant_paths: dict[str, Path],
    docs_gate_info: dict[str, Any],
) -> dict[str, Any]:
    archived_files: list[dict[str, Any]] = []
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for key, path in giant_paths.items():
        archive_path = snapshot_dir / path.relative_to(FULL_TRANSLATION)
        exists = path.exists()
        content = path.read_text(encoding="utf-8") if exists else ""
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(content, encoding="utf-8")
        archived_files.append(
            {
                "target_key": key,
                "target_path": rel_path(path),
                "archived_path": rel_path(archive_path),
                "pre_overwrite_exists": exists,
                "pre_overwrite_sha256": sha256_text(content),
                "pre_overwrite_bytes": len(content.encode("utf-8")),
            }
        )
    snapshot_manifest = {
        "name": "rosetta_machine_giant_manuscript_snapshot",
        "generated_at": now_iso(),
        "docs_gate": docs_gate_info["status"],
        "docs_gate_path": docs_gate_info["path"],
        "docs_gate_required_files": docs_gate_info["required_files"],
        "archive_root": rel_path(snapshot_dir),
        "archived_files": archived_files,
    }
    write_json(snapshot_dir / "giant_manuscript_snapshot_manifest.json", snapshot_manifest)
    return snapshot_manifest


def render_giant_manuscript(
    *,
    machine: dict[str, Any],
    companions: dict[str, Any],
    promotion: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    manuscript_rollup = companions["manuscript_order_rollup"]
    book_rollup = companions["book_operator_rollup"]
    giant_paths = build_giant_manuscript_paths()
    giant_path = giant_paths["giant_manuscript"]

    overview_items = [
        {
            "key": "voynich_full_translation",
            "label": "Unified Atlas",
            "path": CANONICAL_FULL_TRANSLATION_PATH,
            "text": promotion["markdown"]["voynich_full_translation"],
        },
        {
            "key": "voynich_full_crystal",
            "label": "Full Crystal",
            "path": CANONICAL_FULL_CRYSTAL_PATH,
            "text": promotion["markdown"]["voynich_full_crystal"],
        },
        {
            "key": "master_neural_synthesis",
            "label": "Neural Master",
            "path": CANONICAL_NEURAL_MASTER_PATH,
            "text": promotion["markdown"]["master_neural_synthesis"],
        },
    ]
    folio_items = [
        {
            "folio_id": row["folio_id"],
            "path": ROOT / row["source_file"],
            "text": read_required_text(ROOT / row["source_file"]),
        }
        for row in manuscript_rollup
    ]
    section_items = [{"path": path, "text": read_required_text(path)} for path in SECTION_PACKAGE_FILES]
    crystal_items = [{"path": path, "text": read_required_text(path)} for path in CRYSTAL_PACKAGE_FILES]
    explicit_metro = {"path": CANONICAL_METRO_MAP_PATH, "text": read_required_text(CANONICAL_METRO_MAP_PATH)}
    emergent_metro = {"path": EMERGENT_METRO_PATH, "text": read_required_text(EMERGENT_METRO_PATH)}
    f116r_text = next(item["text"] for item in folio_items if item["path"].name == "F116R_FINAL_DRAFT.md")
    f116v_text = next(item["text"] for item in folio_items if item["path"].name == "F116V_FINAL_DRAFT.md")
    f116r_sections = parse_sections(f116r_text)
    f116v_sections = parse_sections(f116v_text)
    f116r_claim = first_sentence_excerpt(f116r_sections.get("Folio Zero Claim", ""))
    f116v_claim = first_sentence_excerpt(f116v_sections.get("Folio Zero Claim", ""))
    corpus_row = next(row for row in book_rollup if row["book_id"] == "Corpus")

    lines = [
        "# Voynich Giant Manuscript",
        "",
        "This file is now the deterministic machine-built whole-manuscript package for the local Voynich corpus. It absorbs the promoted canonical overview, all authoritative final-draft folios, the section synthesis layer, the crystal stack, and the locked metro pair into one inline artifact.",
        "",
        "## Package Status",
        "",
        f"- Docs gate: `{machine['manifest']['docs_gate']}`",
        "- Package mode: `machine-built whole-manuscript package`",
        "- Closure state: `BLOCKED_MISSING_WITNESS`",
        f"- Final-draft folios inlined: `{len(folio_items)}`",
        f"- Section synthesis files inlined: `{len(section_items)}`",
        f"- Crystal files inlined: `{len(crystal_items)}`",
        "- Metro layers inlined: `2`",
        f"- Giant manifest: `{rel_path(GIANT_MANUSCRIPT_MANIFEST_PATH)}`",
        f"- Promotion manifest: `{rel_path(CANONICAL_PROMOTION_MANIFEST_PATH)}`",
        "",
        "## Canonical Corpus Overview",
        "",
        "This overview is sourced from the promoted unified, crystal, and neural master surfaces that were already regenerated from the Rosetta machine.",
        "",
        f"The current local corpus resolves to `{corpus_row['folio_count']}` folios, `{corpus_row['line_count']}` lines, and `{corpus_row['token_count']}` tokens. The docs gate remains `BLOCKED`, so this package is intentionally local-corpus-grounded.",
        "",
        "| Surface | Path | SHA256 | Lead |",
        "| --- | --- | --- | --- |",
    ]
    for item in overview_items:
        lines.append(
            f"| {item['label']} | `{rel_path(item['path'])}` | `{sha256_text(item['text'])}` | {markdown_cell(extract_lead_text(item['text']))} |"
        )
    lines.extend(
        [
            "",
            "### Book Totals",
            "",
            "| Book | Folios | Lines | Tokens | Split Units | Dominant Operators |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        lines.append(
            f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} | {markdown_cell(format_dominant_operator_text(row['dominant_operator_families'], 5))} |"
        )

    lines.extend(
        [
            "",
            "## Inlined Final-Draft Folio Corpus",
            "",
            "The authoritative folio witness layer appears below in manuscript order as full inline source text.",
            "",
        ]
    )
    for item in folio_items:
        lines.extend(render_inlined_markdown_block("FOLIO", item["path"], item["text"]))

    lines.extend(
        [
            "## Inlined Section Synthesis Layer",
            "",
            "The section synthesis layer is inlined below in the fixed Rosetta packaging order.",
            "",
        ]
    )
    for item in section_items:
        lines.extend(render_inlined_markdown_block("SECTION", item["path"], item["text"]))

    lines.extend(
        [
            "## Inlined Crystal Stack",
            "",
            "The crystal stack is inlined below in the fixed Rosetta packaging order, ending with the whole-corpus crystal.",
            "",
        ]
    )
    for item in crystal_items:
        lines.extend(render_inlined_markdown_block("CRYSTAL", item["path"], item["text"]))

    lines.extend(
        [
            "## Final Explicit Metro Layer",
            "",
            "The explicit metro layer is locked to the canonical working metro surface.",
            "",
        ]
    )
    lines.extend(render_inlined_markdown_block("METRO_EXPLICIT", explicit_metro["path"], explicit_metro["text"]))

    lines.extend(
        [
            "## Final Emergent Metro Layer",
            "",
            "The emergent metro layer is locked to the neural-network L2 emergent metro witness.",
            "",
        ]
    )
    lines.extend(render_inlined_markdown_block("METRO_EMERGENT", emergent_metro["path"], emergent_metro["text"]))

    lines.extend(
        [
            "## Closure-Witness Status",
            "",
            "No dedicated local post-`116r` authorial-line witness was found.",
            "",
            f"- Available terminal witness 1: `{rel_path(FOLIOS_DIR / 'F116R_FINAL_DRAFT.md')}` carries the available `f116r` closing text witness. {f116r_claim or 'This is the available closing instruction witness inside the local corpus.'}",
            f"- Available terminal witness 2: `{rel_path(FOLIOS_DIR / 'F116V_FINAL_DRAFT.md')}` carries the available `f116v` colophon witness. {f116v_claim or 'This is the available terminal colophon witness inside the local corpus.'}",
            "- The dedicated authorial line therefore remains `BLOCKED/MISSING` until a local or live-docs source exists.",
            "- This package does not invent a post-`116r` authorial final line beyond the available witnesses.",
            "",
        ]
    )

    markdown = "\n".join(lines) + "\n"
    metadata = {
        "giant_path": rel_path(giant_path),
        "inventory_counts": {
            "overview_sources": len(overview_items),
            "folios": len(folio_items),
            "sections": len(section_items),
            "crystals": len(crystal_items),
            "metros": 2,
        },
        "overview_sources": [{"label": item["label"], "path": rel_path(item["path"])} for item in overview_items],
        "ordered_inputs": (
            [rel_path(item["path"]) for item in overview_items]
            + [rel_path(item["path"]) for item in folio_items]
            + [rel_path(item["path"]) for item in section_items]
            + [rel_path(item["path"]) for item in crystal_items]
            + [rel_path(explicit_metro["path"]), rel_path(emergent_metro["path"])]
        ),
        "package_order": {
            "overview_sources": [rel_path(item["path"]) for item in overview_items],
            "folios": [rel_path(item["path"]) for item in folio_items],
            "sections": [rel_path(item["path"]) for item in section_items],
            "crystals": [rel_path(item["path"]) for item in crystal_items],
            "metros": [rel_path(explicit_metro["path"]), rel_path(emergent_metro["path"])],
        },
        "closure_state": "BLOCKED_MISSING_WITNESS",
        "closure_witnesses": [
            {
                "path": rel_path(FOLIOS_DIR / "F116R_FINAL_DRAFT.md"),
                "role": "closing_text",
                "claim_excerpt": f116r_claim,
            },
            {
                "path": rel_path(FOLIOS_DIR / "F116V_FINAL_DRAFT.md"),
                "role": "colophon",
                "claim_excerpt": f116v_claim,
            },
        ],
        "giant_manuscript_content_sha256": sha256_text(markdown),
    }
    return markdown, metadata


def build_giant_manuscript() -> dict[str, Any]:
    machine = ensure_rosetta_pipeline_outputs()
    try:
        companions = load_companion_outputs()
    except FileNotFoundError:
        build_rosetta_companions()
        companions = load_companion_outputs()
    try:
        promotion = load_canonical_promotion_outputs()
    except FileNotFoundError:
        build_rosetta_canonical_promotion()
        promotion = load_canonical_promotion_outputs()

    giant_paths = build_giant_manuscript_paths()
    docs_gate_info = resolve_docs_gate()
    giant_markdown, metadata = render_giant_manuscript(
        machine=machine,
        companions=companions,
        promotion=promotion,
    )

    existing_manifest = read_json(GIANT_MANUSCRIPT_MANIFEST_PATH) if GIANT_MANUSCRIPT_MANIFEST_PATH.exists() else None
    current_texts = {key: read_text_if_exists(path) for key, path in giant_paths.items()}
    changed_keys = [key for key, text in {"giant_manuscript": giant_markdown}.items() if current_texts.get(key, "") != text]
    snapshot_manifest = None
    archive_snapshot_path = existing_manifest.get("archive_snapshot_path") if existing_manifest else None
    archive_snapshot_manifest = existing_manifest.get("archive_snapshot_manifest") if existing_manifest else None

    if changed_keys:
        snapshot_dir = ARCHIVE_DIR / timestamp_z()
        snapshot_manifest = build_giant_manuscript_snapshot_manifest(
            snapshot_dir=snapshot_dir,
            giant_paths=giant_paths,
            docs_gate_info=docs_gate_info,
        )
        archive_snapshot_path = rel_path(snapshot_dir)
        archive_snapshot_manifest = rel_path(snapshot_dir / "giant_manuscript_snapshot_manifest.json")
        giant_paths["giant_manuscript"].write_text(giant_markdown, encoding="utf-8")

    manifest = build_manifest(
        "rosetta_machine_giant_manuscript",
        docs_gate_info,
        {"giant_manuscript": giant_markdown},
        extra={
            "package_inventory_counts": metadata["inventory_counts"],
            "ordered_inputs": metadata["ordered_inputs"],
            "package_order": metadata["package_order"],
            "overview_sources": metadata["overview_sources"],
            "closure_state": metadata["closure_state"],
            "closure_witnesses": metadata["closure_witnesses"],
            "giant_manuscript_content_sha256": metadata["giant_manuscript_content_sha256"],
            "archive_snapshot_path": archive_snapshot_path,
            "archive_snapshot_manifest": archive_snapshot_manifest,
        },
    )
    write_json(GIANT_MANUSCRIPT_MANIFEST_PATH, manifest)
    return {
        "manifest": manifest,
        "markdown": {"giant_manuscript": giant_markdown},
        "paths": giant_paths,
        "archive_snapshot_path": archive_snapshot_path,
        "archive_snapshot_manifest": archive_snapshot_manifest,
        "snapshot_created": snapshot_manifest is not None,
    }


def count_markdown_rows(text: str, prefix: str) -> int:
    return sum(1 for line in text.splitlines() if line.startswith(prefix))


def extract_markdown_folio_sequence(text: str) -> list[str]:
    folios: list[str] = []
    pattern = re.compile(r"^\|\s*`(F[0-9]{3}[RV](?:[0-9])?)`\s*\|")
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if match:
            folios.append(match.group(1))
    return folios


def validate_companion_outputs(machine: dict[str, Any], companions: dict[str, Any]) -> None:
    manuscript_rollup = companions["manuscript_order_rollup"]
    book_rollup = companions["book_operator_rollup"]
    neural_rollup = companions["neural_node_rollup"]
    metro_rollup = companions["metro_edge_rollup"]
    integration_manifest = companions["integration_manifest"]
    markdown = companions["markdown"]

    if len(manuscript_rollup) != machine["manifest"]["final_draft_folios"]:
        raise ValueError("Manuscript companion rollup count does not match final draft folio count.")
    if sum(row["line_count"] for row in manuscript_rollup) != len(machine["line_records"]):
        raise ValueError("Manuscript companion rollup line total does not match core machine.")
    if sum(row["token_count"] for row in manuscript_rollup) != len(machine["token_records"]):
        raise ValueError("Manuscript companion rollup token total does not match core machine.")

    book_lookup = {record["book_id"]: record for record in machine["book_records"]}
    if {row["book_id"] for row in book_rollup} != {"Book I", "Book II", "Book III", "Book IV", "Book V", "Corpus"}:
        raise ValueError("Book operator rollup is missing required book rows.")
    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        book = book_lookup[row["book_id"]]
        if row["folio_count"] != book["folio_count"] or row["line_count"] != book["line_count"] or row["token_count"] != book["token_count"]:
            raise ValueError(f"Book operator rollup mismatch for {row['book_id']}")

    neural_lookup = {row["node_id"]: row for row in neural_rollup}
    if set(neural_lookup) != set(NODE_META):
        raise ValueError("Neural node rollup does not cover all 16 nodes.")
    if sum(row["rosetta_attachment_counts"]["folios"] for row in neural_rollup) != len(machine["folio_records"]):
        raise ValueError("Neural node rollup folio total does not match core machine.")
    if sum(row["rosetta_attachment_counts"]["lines"] for row in neural_rollup) != len(machine["line_records"]):
        raise ValueError("Neural node rollup line total does not match core machine.")
    if sum(row["rosetta_attachment_counts"]["tokens"] for row in neural_rollup) != len(machine["token_records"]):
        raise ValueError("Neural node rollup token total does not match core machine.")
    for node_id, data in machine["corpus_index"]["neural_node_counts"].items():
        row = neural_lookup[node_id]
        if row["source_document_count"] != data["source_documents"]:
            raise ValueError(f"Neural source-document count mismatch for {node_id}")

    expected_edges = len(manuscript_rollup) * (len(machine["transport_registry"]) + 1)
    if len(metro_rollup) != expected_edges:
        raise ValueError("Metro edge rollup size does not match expected folio-to-node and folio-to-notation fanout.")

    companion_hash_expectations = {
        "manuscript_order_rollup": normalized_sha256(manuscript_rollup),
        "book_operator_rollup": normalized_sha256(book_rollup),
        "neural_node_rollup": normalized_sha256(neural_rollup),
        "metro_edge_rollup": normalized_sha256(metro_rollup),
        "master_manuscript_companion": normalized_sha256(markdown["master_manuscript_companion"]),
        "crystal_companion": normalized_sha256(markdown["crystal_companion"]),
        "metro_companion": normalized_sha256(markdown["metro_companion"]),
        "node_bridge": normalized_sha256(markdown["node_bridge"]),
        "integration_status": normalized_sha256(markdown["integration_status"]),
    }
    for key, digest in companion_hash_expectations.items():
        if integration_manifest["hashes"].get(key) != digest:
            raise ValueError(f"Integration manifest hash mismatch for {key}")

    if count_markdown_rows(markdown["master_manuscript_companion"], "| `F") != len(manuscript_rollup):
        raise ValueError("Master manuscript companion does not contain the expected folio packet count.")
    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        book_row_prefix = f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} |"
        if book_row_prefix not in markdown["master_manuscript_companion"]:
            raise ValueError(f"Master manuscript companion missing book totals for {row['book_id']}")
        if book_row_prefix not in markdown["crystal_companion"]:
            raise ValueError(f"Crystal companion missing book totals for {row['book_id']}")

    for row in neural_rollup:
        node_prefix = (
            f"| `{row['node_id']}` | {row['node_name']} | {row['source_document_count']} | "
            f"{row['folio_count']} | {row['rosetta_attachment_counts']['lines']} | {row['rosetta_attachment_counts']['tokens']} |"
        )
        if node_prefix not in markdown["node_bridge"]:
            raise ValueError(f"Node bridge markdown missing counts for {row['node_id']}")

    manuscript_split_units = {row["folio_id"] for row in manuscript_rollup if row["split_unit"]}
    book_split_units = {split for row in book_rollup for split in row["split_units"]}
    neural_split_units = {split for row in neural_rollup for split in row["split_units"]}
    metro_split_units = {row["source_folio"] for row in metro_rollup}
    if not REQUIRED_SPLIT_UNITS.issubset(manuscript_split_units):
        raise ValueError("Required split units missing from manuscript rollup.")
    if not REQUIRED_SPLIT_UNITS.issubset(book_split_units):
        raise ValueError("Required split units missing from book rollup.")
    if not REQUIRED_SPLIT_UNITS.issubset(neural_split_units):
        raise ValueError("Required split units missing from neural rollup.")
    if not REQUIRED_SPLIT_UNITS.issubset(metro_split_units):
        raise ValueError("Required split units missing from metro rollup.")
    for folio_id in REQUIRED_SPLIT_UNITS:
        if f"`{folio_id}`" not in markdown["master_manuscript_companion"]:
            raise ValueError(f"Required split unit {folio_id} missing from master manuscript companion.")
        if f"`{folio_id}`" not in markdown["crystal_companion"]:
            raise ValueError(f"Required split unit {folio_id} missing from crystal companion.")


def validate_canonical_promotion_outputs(
    machine: dict[str, Any],
    companions: dict[str, Any],
    promotion: dict[str, Any],
) -> None:
    manifest = promotion["manifest"]
    markdown = promotion["markdown"]
    canonical_paths = promotion["paths"]
    book_rollup = companions["book_operator_rollup"]
    manuscript_rollup = companions["manuscript_order_rollup"]
    neural_rollup = companions["neural_node_rollup"]
    metro_summary = summarize_metro_corridors(
        metro_edges=companions["metro_edge_rollup"],
        transport_registry=machine["transport_registry"],
    )

    for key, path in canonical_paths.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing promoted canonical file: {rel_path(path)}")
        if manifest["hashes"].get(key) != normalized_sha256(markdown[key]):
            raise ValueError(f"Canonical promotion manifest hash mismatch for {key}")

    unified_sequence = extract_markdown_folio_sequence(markdown["voynich_full_translation"])
    master_sequence = extract_markdown_folio_sequence(markdown["voynich_master_manuscript"])
    expected_sequence = [row["folio_id"] for row in manuscript_rollup]
    if unified_sequence != expected_sequence:
        raise ValueError("Promoted full translation does not preserve manuscript-order folio packets.")
    if master_sequence != expected_sequence:
        raise ValueError("Promoted master manuscript does not preserve manuscript-order folio packets.")
    if count_markdown_rows(markdown["voynich_full_translation"], "| `F") != len(manuscript_rollup):
        raise ValueError("Promoted full translation does not contain the expected folio packet count.")
    if count_markdown_rows(markdown["voynich_master_manuscript"], "| `F") != len(manuscript_rollup):
        raise ValueError("Promoted master manuscript does not contain the expected folio packet count.")

    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        book_row_prefix = f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} |"
        if book_row_prefix not in markdown["voynich_full_translation"]:
            raise ValueError(f"Promoted full translation missing book totals for {row['book_id']}")
        if book_row_prefix not in markdown["voynich_master_manuscript"]:
            raise ValueError(f"Promoted master manuscript missing book totals for {row['book_id']}")
        if book_row_prefix not in markdown["voynich_full_crystal"]:
            raise ValueError(f"Promoted crystal missing book totals for {row['book_id']}")

    for row in neural_rollup:
        books = ", ".join(f"`{book}`" for book in row["book_coverage"]) if row["book_coverage"] else "-"
        node_prefix = (
            f"| `{row['node_id']}` | {row['node_name']} | {row['source_document_count']} | {row['folio_count']} | "
            f"{row['rosetta_attachment_counts']['lines']} | {row['rosetta_attachment_counts']['tokens']} | {books} | {row['split_unit_count']} |"
        )
        if node_prefix not in markdown["master_neural_synthesis"]:
            raise ValueError(f"Promoted neural master missing node counts for {row['node_id']}")

    for row in metro_summary["top_notation"]:
        corridor_prefix = (
            f"| `{row['source_book']}` | `{row['target_notation']}` | `{row['notation_class']}` | {row['target_carrier']} | {row['weight']} |"
        )
        if corridor_prefix not in markdown["voynich_metro_map_working"]:
            raise ValueError("Promoted metro map is missing a top book-to-notation corridor.")
    for row in metro_summary["top_node"]:
        corridor_prefix = (
            f"| `{row['source_book']}` | `{row['target_node']}` | {row['target_label']} | {row['weight']} |"
        )
        if corridor_prefix not in markdown["voynich_metro_map_working"]:
            raise ValueError("Promoted metro map is missing a top book-to-node corridor.")
    for row in metro_summary["bottlenecks"]:
        corridor_prefix = (
            f"| `{row['source_book']}` | `{row['target_notation']}` | `{row['notation_class']}` | {row['target_carrier']} | {row['weight']} |"
        )
        if corridor_prefix not in markdown["voynich_metro_map_working"]:
            raise ValueError("Promoted metro map is missing a bottleneck corridor.")

    for folio_id in REQUIRED_SPLIT_UNITS:
        if f"`{folio_id}`" not in markdown["voynich_full_translation"]:
            raise ValueError(f"Required split unit {folio_id} missing from promoted full translation.")
        if f"`{folio_id}`" not in markdown["voynich_master_manuscript"]:
            raise ValueError(f"Required split unit {folio_id} missing from promoted master manuscript.")
        if f"`{folio_id}`" not in markdown["voynich_full_crystal"]:
            raise ValueError(f"Required split unit {folio_id} missing from promoted full crystal.")

    archive_snapshot_path = manifest.get("archive_snapshot_path")
    archive_snapshot_manifest = manifest.get("archive_snapshot_manifest")
    if not archive_snapshot_path or not archive_snapshot_manifest:
        raise ValueError("Canonical promotion manifest is missing archive snapshot references.")
    snapshot_manifest_path = ROOT / archive_snapshot_manifest
    if not snapshot_manifest_path.exists():
        raise FileNotFoundError(f"Missing promotion snapshot manifest: {archive_snapshot_manifest}")
    snapshot_manifest = read_json(snapshot_manifest_path)
    archived_targets = {entry["target_key"] for entry in snapshot_manifest["archived_files"]}
    if archived_targets != set(canonical_paths):
        raise ValueError("Promotion snapshot manifest does not cover every canonical target.")
    for entry in snapshot_manifest["archived_files"]:
        archived_path = ROOT / entry["archived_path"]
        if not archived_path.exists():
            raise FileNotFoundError(f"Missing archived canonical witness: {entry['archived_path']}")


def validate_giant_manuscript_outputs(
    machine: dict[str, Any],
    companions: dict[str, Any],
    promotion: dict[str, Any],
    giant: dict[str, Any],
) -> None:
    manifest = giant["manifest"]
    markdown = giant["markdown"]["giant_manuscript"]
    giant_path = giant["paths"]["giant_manuscript"]
    manuscript_rollup = companions["manuscript_order_rollup"]
    book_rollup = companions["book_operator_rollup"]

    if not giant_path.exists():
        raise FileNotFoundError(f"Missing giant manuscript: {rel_path(giant_path)}")
    if manifest["hashes"].get("giant_manuscript") != normalized_sha256(markdown):
        raise ValueError("Giant manuscript manifest hash mismatch for giant_manuscript.")
    if manifest.get("giant_manuscript_content_sha256") != sha256_text(markdown):
        raise ValueError("Giant manuscript content hash does not match manifest.")
    if manifest.get("docs_gate") != "BLOCKED":
        raise ValueError("Giant manuscript docs gate honesty check failed.")
    if manifest.get("closure_state") != "BLOCKED_MISSING_WITNESS":
        raise ValueError("Giant manuscript closure state is not BLOCKED_MISSING_WITNESS.")

    expected_overview_paths = [rel_path(path) for path in CANONICAL_OVERVIEW_PATHS]
    expected_folio_paths = [row["source_file"] for row in manuscript_rollup]
    expected_section_paths = [rel_path(path) for path in SECTION_PACKAGE_FILES]
    expected_crystal_paths = [rel_path(path) for path in CRYSTAL_PACKAGE_FILES]
    expected_explicit_metro = [rel_path(CANONICAL_METRO_MAP_PATH)]
    expected_emergent_metro = [rel_path(EMERGENT_METRO_PATH)]
    expected_ordered_inputs = (
        expected_overview_paths
        + expected_folio_paths
        + expected_section_paths
        + expected_crystal_paths
        + expected_explicit_metro
        + expected_emergent_metro
    )

    if manifest.get("ordered_inputs") != expected_ordered_inputs:
        raise ValueError("Giant manuscript manifest ordered input list does not match the fixed package order.")
    inventory_counts = manifest.get("package_inventory_counts", {})
    if inventory_counts.get("overview_sources") != len(expected_overview_paths):
        raise ValueError("Giant manuscript manifest overview count mismatch.")
    if inventory_counts.get("folios") != len(expected_folio_paths):
        raise ValueError("Giant manuscript manifest folio count mismatch.")
    if inventory_counts.get("sections") != len(expected_section_paths):
        raise ValueError("Giant manuscript manifest section count mismatch.")
    if inventory_counts.get("crystals") != len(expected_crystal_paths):
        raise ValueError("Giant manuscript manifest crystal count mismatch.")
    if inventory_counts.get("metros") != 2:
        raise ValueError("Giant manuscript manifest metro count mismatch.")

    folio_sequence = extract_inline_sequence(markdown, "FOLIO")
    section_sequence = extract_inline_sequence(markdown, "SECTION")
    crystal_sequence = extract_inline_sequence(markdown, "CRYSTAL")
    explicit_metro_sequence = extract_inline_sequence(markdown, "METRO_EXPLICIT")
    emergent_metro_sequence = extract_inline_sequence(markdown, "METRO_EMERGENT")
    if folio_sequence != expected_folio_paths:
        raise ValueError("Giant manuscript does not inline the 222 final-draft folios in manuscript order.")
    if section_sequence != expected_section_paths:
        raise ValueError("Giant manuscript does not inline the section synthesis files in the fixed order.")
    if crystal_sequence != expected_crystal_paths:
        raise ValueError("Giant manuscript does not inline the crystal stack in the fixed order.")
    if explicit_metro_sequence != expected_explicit_metro:
        raise ValueError("Giant manuscript explicit metro source is not the canonical working metro map.")
    if emergent_metro_sequence != expected_emergent_metro:
        raise ValueError("Giant manuscript emergent metro source is not the neural-network L2 emergent metro map.")

    if "No dedicated local post-`116r` authorial-line witness was found." not in markdown:
        raise ValueError("Giant manuscript closure section does not state the missing post-116r witness.")
    if "`BLOCKED/MISSING`" not in markdown:
        raise ValueError("Giant manuscript closure section does not preserve BLOCKED/MISSING status.")
    if rel_path(FOLIOS_DIR / "F116R_FINAL_DRAFT.md") not in markdown:
        raise ValueError("Giant manuscript closure section does not cite the f116r closing text witness.")
    if rel_path(FOLIOS_DIR / "F116V_FINAL_DRAFT.md") not in markdown:
        raise ValueError("Giant manuscript closure section does not cite the f116v colophon witness.")
    if "does not invent a post-`116r` authorial final line beyond the available witnesses" not in markdown:
        raise ValueError("Giant manuscript closure section does not explicitly forbid an invented final line.")

    for row in book_rollup:
        if row["book_id"] == "Corpus":
            continue
        book_row_prefix = f"| `{row['book_id']}` | {row['folio_count']} | {row['line_count']} | {row['token_count']} | {row['split_unit_count']} |"
        if book_row_prefix not in markdown:
            raise ValueError(f"Giant manuscript overview is missing book totals for {row['book_id']}")
    for folio_id in REQUIRED_SPLIT_UNITS:
        split_path = next(row["source_file"] for row in manuscript_rollup if row["folio_id"] == folio_id)
        if split_path not in folio_sequence:
            raise ValueError(f"Giant manuscript is missing required split unit {folio_id}.")

    archive_snapshot_path = manifest.get("archive_snapshot_path")
    archive_snapshot_manifest = manifest.get("archive_snapshot_manifest")
    if not archive_snapshot_path or not archive_snapshot_manifest:
        raise ValueError("Giant manuscript manifest is missing archive snapshot references.")
    snapshot_manifest_path = ROOT / archive_snapshot_manifest
    if not snapshot_manifest_path.exists():
        raise FileNotFoundError(f"Missing giant manuscript snapshot manifest: {archive_snapshot_manifest}")
    snapshot_manifest = read_json(snapshot_manifest_path)
    archived_targets = {entry["target_key"] for entry in snapshot_manifest["archived_files"]}
    if archived_targets != {"giant_manuscript"}:
        raise ValueError("Giant manuscript snapshot manifest does not cover the giant manuscript target.")
    for entry in snapshot_manifest["archived_files"]:
        archived_path = ROOT / entry["archived_path"]
        if not archived_path.exists():
            raise FileNotFoundError(f"Missing archived giant manuscript witness: {entry['archived_path']}")


def validate_type(expected: str, value: Any) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    expected_type = schema.get("type")
    if expected_type and not validate_type(expected_type, value):
        raise ValueError(f"{path}: expected {expected_type}, got {type(value).__name__}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: {value!r} not in enum")
    if expected_type == "object":
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValueError(f"{path}: missing required field {key}")
        properties = schema.get("properties", {})
        for key, prop_schema in properties.items():
            if key in value:
                validate_schema(value[key], prop_schema, f"{path}.{key}")
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(properties)
            if extra:
                raise ValueError(f"{path}: unexpected properties {sorted(extra)}")
    if expected_type == "array":
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise ValueError(f"{path}: expected at least {schema['minItems']} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                validate_schema(item, item_schema, f"{path}[{index}]")
    if expected_type in {"number", "integer"}:
        if "minimum" in schema and value < schema["minimum"]:
            raise ValueError(f"{path}: value below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValueError(f"{path}: value above maximum {schema['maximum']}")


def validate_simple_registry(records: list[dict[str, Any]], schema_name: str) -> None:
    schema = read_json(schema_paths()[schema_name])
    for index, record in enumerate(records):
        validate_schema(record, schema, f"{schema_name}[{index}]")


def validate_rosetta_machine() -> dict[str, Any]:
    build_one = build_rosetta_machine()
    build_two = build_rosetta_machine()
    if build_one["manifest"]["hashes"] != build_two["manifest"]["hashes"]:
        raise ValueError("Non-deterministic build hash detected for rosetta machine outputs.")
    export_one = export_rosetta_notations()
    export_two = export_rosetta_notations()
    if export_one["manifest"]["hashes"] != export_two["manifest"]["hashes"]:
        raise ValueError("Non-deterministic export hash detected for notation exports.")
    companion_one = build_rosetta_companions()
    companion_two = build_rosetta_companions()
    if companion_one["integration_manifest"]["hashes"] != companion_two["integration_manifest"]["hashes"]:
        raise ValueError("Non-deterministic integration hash detected for companion outputs.")
    archive_before = sorted(path.name for path in ARCHIVE_DIR.glob("*") if path.is_dir()) if ARCHIVE_DIR.exists() else []
    promotion_one = build_rosetta_canonical_promotion()
    archive_after_first = sorted(path.name for path in ARCHIVE_DIR.glob("*") if path.is_dir()) if ARCHIVE_DIR.exists() else []
    promotion_two = build_rosetta_canonical_promotion()
    archive_after_second = sorted(path.name for path in ARCHIVE_DIR.glob("*") if path.is_dir()) if ARCHIVE_DIR.exists() else []
    if promotion_one["manifest"]["hashes"] != promotion_two["manifest"]["hashes"]:
        raise ValueError("Non-deterministic canonical promotion hash detected for promoted outputs.")
    if archive_after_first != archive_after_second:
        raise ValueError("Canonical promotion created archive spam on an unchanged rerun.")
    giant_one = build_giant_manuscript()
    archive_after_giant_first = sorted(path.name for path in ARCHIVE_DIR.glob("*") if path.is_dir()) if ARCHIVE_DIR.exists() else []
    giant_two = build_giant_manuscript()
    archive_after_giant_second = sorted(path.name for path in ARCHIVE_DIR.glob("*") if path.is_dir()) if ARCHIVE_DIR.exists() else []
    if giant_one["manifest"]["hashes"] != giant_two["manifest"]["hashes"]:
        raise ValueError("Non-deterministic giant manuscript hash detected for packaged outputs.")
    if archive_after_giant_first != archive_after_giant_second:
        raise ValueError("Giant manuscript packaging created archive spam on an unchanged rerun.")

    machine = load_machine_outputs()
    exports = read_jsonl(EXPORTS_DIR / "notation_exports.jsonl")
    roundtrip_examples = read_json(EXPORTS_DIR / "roundtrip_examples.json")
    export_manifest = read_json(BUILD_DIR / "export_manifest.json")
    companions = load_companion_outputs()
    promotion = load_canonical_promotion_outputs()
    giant = load_giant_manuscript_outputs()
    docs_gate_info = resolve_docs_gate()
    final_draft_count = len(list(FOLIOS_DIR.glob("*_FINAL_DRAFT.md")))

    for path in schema_paths().values():
        if not path.exists():
            raise FileNotFoundError(f"Missing schema file: {path}")

    validate_simple_registry(machine["eva_atoms"], "eva_atom")
    validate_simple_registry(machine["morphemes"], "morpheme")
    validate_simple_registry(machine["operator_families"], "operator_family")
    validate_simple_registry(machine["transport_registry"], "transport_registry")
    validate_simple_registry(machine["folio_records"], "folio_algorithm")
    validate_schema(machine["corpus_index"], read_json(schema_paths()["corpus_index"]), "corpus_index")
    validate_simple_registry(exports, "notation_export")

    for record in machine["token_records"] + machine["line_records"] + machine["book_records"]:
        for field in ("id", "kind", "source_unit", "evidence_class", "confidence", "docs_gate", "inputs", "transform", "outputs", "constraints", "export_targets", "source_refs"):
            if field not in record:
                raise ValueError(f"Missing shared field {field} in {record.get('id', '<unknown>')}")

    if final_draft_count != 222:
        raise ValueError(f"Expected 222 final draft folios, found {final_draft_count}")
    if len(machine["folio_records"]) != final_draft_count:
        raise ValueError("Parsed final draft folio count does not match filesystem count.")

    present_split_units = {record["folio_id"] for record in machine["folio_records"] if record["split_unit"]}
    if not REQUIRED_SPLIT_UNITS.issubset(present_split_units):
        raise ValueError("Required split folio units were not preserved as first-class units.")

    if machine["corpus_index"]["docs_gate"] != docs_gate_info["status"]:
        raise ValueError("Corpus index docs gate status disagrees with live gate resolution.")
    if machine["manifest"]["docs_gate"] != docs_gate_info["status"] or export_manifest["docs_gate"] != docs_gate_info["status"]:
        raise ValueError("Manifest docs gate status disagrees with live gate resolution.")
    if docs_gate_info["status"] != "BLOCKED":
        raise ValueError("Docs gate honesty check failed: expected BLOCKED until live credentials and token exist.")
    if archive_before != archive_after_first and len(archive_after_first) < len(archive_before):
        raise ValueError("Archive directory count moved backwards during canonical promotion.")
    if archive_after_second != archive_after_giant_first and len(archive_after_giant_first) < len(archive_after_second):
        raise ValueError("Archive directory count moved backwards during giant manuscript packaging.")

    expected_build_hashes = {
        "eva_atoms": normalized_sha256(machine["eva_atoms"]),
        "morphemes": normalized_sha256(machine["morphemes"]),
        "operator_families": normalized_sha256(machine["operator_families"]),
        "transport_registry": normalized_sha256(machine["transport_registry"]),
        "token_instances": normalized_sha256(machine["token_records"]),
        "line_operator_chains": normalized_sha256(machine["line_records"]),
        "folio_algorithms": normalized_sha256(machine["folio_records"]),
        "book_algorithms": normalized_sha256(machine["book_records"]),
        "corpus_index": normalized_sha256(machine["corpus_index"]),
    }
    for key, digest in expected_build_hashes.items():
        if machine["manifest"]["hashes"].get(key) != digest:
            raise ValueError(f"Build manifest hash mismatch for {key}")

    expected_export_hashes = {
        "notation_exports": normalized_sha256(exports),
        "roundtrip_examples": normalized_sha256(roundtrip_examples),
    }
    for key, digest in expected_export_hashes.items():
        if export_manifest["hashes"].get(key) != digest:
            raise ValueError(f"Export manifest hash mismatch for {key}")

    roundtrip_ids = {item["sample_id"] for item in roundtrip_examples}
    if roundtrip_ids != {"qo_prefix", "dy_suffix", "aiin_cycle", "damaged_token", "full_line_chain"}:
        raise ValueError("Roundtrip example set is incomplete.")
    for example in roundtrip_examples:
        for notation_id in ("vml_ir", "hybrid_legal_dsl", "json_schema", "python", "rust"):
            if notation_id not in example["notations"]:
                raise ValueError(f"Roundtrip example {example['sample_id']} missing {notation_id}")

    validate_companion_outputs(machine, companions)
    validate_canonical_promotion_outputs(machine, companions, promotion)
    validate_giant_manuscript_outputs(machine, companions, promotion, giant)

    return {
        "docs_gate": docs_gate_info["status"],
        "final_draft_folios": len(machine["folio_records"]),
        "line_operator_chains": len(machine["line_records"]),
        "token_instances": len(machine["token_records"]),
        "notation_exports": len(exports),
        "companion_rollups": len(companions["manuscript_order_rollup"]),
        "canonical_promotions": len(promotion["markdown"]),
        "giant_packages": len(giant["markdown"]),
    }
