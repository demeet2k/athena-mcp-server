from __future__ import annotations

import ast
import json
import re
from collections import Counter
from hashlib import md5
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
BOT = ROOT / "Trading Bot"
CRYPTO = BOT / "CRYPTO CURRENCY"
OUT = BOT / "TRADING_BOT_ATHENA_256X4"
ATLAS = ROOT / "self_actualize" / "corpus_atlas.json"
DOCX = CRYPTO / "docx_output.txt"
HOLO = CRYPTO / "temp_hologram_time.txt"
TR = CRYPTO / "time_fractal_analysis" / "05_FULL_SYNTHESIS_REPORT.txt"
FR = CRYPTO / "forex_data" / "10_ANALYSIS_REPORT.txt"
ENGINE = CRYPTO / "time_fractal_engine.py"
SIGNALS = CRYPTO / "trading_bot_signals.py"
PIPE = CRYPTO / "run_full_analysis.py"

CARRIERS = {
    "0": ("Square", "structure, books, states"),
    "1": ("Circle", "phase, timing, toroidal return"),
    "2": ("Triangle", "control, corridors, risk"),
    "3": ("Fractal", "swarm, replay, recursion"),
}

LAYERS = ["LPPL", "DSI", "Elliott Wave", "Kondratiev", "Holographic Phase", "Volatility Structure"]
SIGNAL_TYPES = ["NEXUS_ALERT", "REGIME_SHIFT", "PHASE_EDGE", "QUALITY_READ"]
MEMORY = [
    "HIGHER-D SQUARE CIRCLE TRIANGLE",
    "Holographic Reality Structure",
    "LEGAL TRANSPORT CALCULUS",
    "THE UNIFIED CYCLICAL TIME SYSTEM",
    "Omega Metro Calculus",
    "Omega Tunneling Coherence Crystal",
]
LINES = [
    ("L1", "Atlas Line", "project-wide intake"),
    ("L2", "Memory Line", "Trading Bot memory docs"),
    ("L3", "Kernel Line", "time-fractal algebra"),
    ("L4", "Market Line", "crypto, forex, macro routing"),
    ("L5", "Signal Line", "signal ranking and synthesis"),
    ("L6", "Risk Line", "exposure and legality"),
    ("L7", "Replay Line", "verification and receipts"),
    ("L8", "Deployment Line", "runtime and monitoring"),
]
HUBS = [("H1", "Intake Hub"), ("H2", "Phase Hub"), ("H3", "Asset Hub"), ("H4", "Signal Hub"), ("H5", "Risk Hub"), ("H6", "Execution Hub"), ("H7", "Replay Hub"), ("H8", "Audit Hub"), ("H9", "Deployment Hub")]
ROLES = [
    ("R01", "Corpus Cartographer", "maps corpus evidence into bot coordinates"),
    ("R02", "Memory Weaver", "folds the higher-dimensional manuscripts into runtime"),
    ("R03", "Kernel Architect", "maintains the time-fractal algebra"),
    ("R04", "DSI Scout", "tracks scale-ratio alignment"),
    ("R05", "LPPL Watcher", "monitors critical-transition signatures"),
    ("R06", "Elliott Reader", "binds swing structure into manuscripts"),
    ("R07", "K-Wave Sentinel", "places signals inside macro cycle context"),
    ("R08", "Asset Librarian", "maintains asset baskets"),
    ("R09", "Signal Conductor", "turns scores into ranked outputs"),
    ("R10", "Risk Governor", "constrains sizing and stops"),
    ("R11", "Execution Broker", "defines entries and exits"),
    ("R12", "Portfolio Balancer", "spreads conviction across baskets"),
    ("R13", "Replay Auditor", "verifies receipts and reproducibility"),
    ("R14", "Ledger Keeper", "writes source and residual ledgers"),
    ("R15", "Deployment Steward", "moves the body into runtime"),
    ("R16", "Living-System Conductor", "keeps the whole system in a rebuild loop"),
]
CHAPTERS = [
    ("Ch01", "Trading Bot Origin Field"),
    ("Ch02", "Corpus Intake and Gaps"),
    ("Ch03", "Square Circle Triangle Fractal Translation"),
    ("Ch04", "Kernel Algebra"),
    ("Ch05", "Time-Fractal Market Physics"),
    ("Ch06", "Asset Universe Cartography"),
    ("Ch07", "The 256-State Hologram"),
    ("Ch08", "Signal Hierarchy"),
    ("Ch09", "Risk Corridors"),
    ("Ch10", "Execution Grammar"),
    ("Ch11", "Oracle Uncertainty and Zero Point"),
    ("Ch12", "Backtest and Replay"),
    ("Ch13", "Emergent Swarm Runtime"),
    ("Ch14", "Metro Map of the Bot"),
    ("Ch15", "Cross-Corpus Connectors"),
    ("Ch16", "Portfolio Tensor"),
    ("Ch17", "Forex Extension"),
    ("Ch18", "Crypto Extension"),
    ("Ch19", "Governance and Ledgers"),
    ("Ch20", "Deployment and Monitoring"),
    ("Ch21", "Infinite Recursion Loop"),
]
APPENDICES = [
    ("AppA", "Corpus Intake Schema"),
    ("AppB", "Source Ledger"),
    ("AppC", "Square Grammar"),
    ("AppD", "Circle Grammar"),
    ("AppE", "Triangle Grammar"),
    ("AppF", "Fractal Grammar"),
    ("AppG", "Signal Schema"),
    ("AppH", "Risk Schema"),
    ("AppI", "Truth Typing"),
    ("AppJ", "Residual Ledger"),
    ("AppK", "Conflict Ledger"),
    ("AppL", "Evidence Plans"),
    ("AppM", "Meta-Zero Snap"),
    ("AppN", "Containers and Runtime"),
    ("AppO", "Publication Surface"),
    ("AppP", "Mycelium Connectors"),
]
PLANES = [
    {"key": "kernel", "dir": "08_PLANES/01_KERNEL_PLANE", "label": "Kernel Plane", "desc": "higher-dimensional market semantics", "terms": [("address lattice", "phase ring", "control hinge", "fractal echo"), ("data carrier", "timing carrier", "risk carrier", "swarm carrier"), ("signal grammar", "octave grammar", "corridor grammar", "proof grammar"), ("state vector", "nexus vector", "execution vector", "renewal vector")]},
    {"key": "market", "dir": "08_PLANES/02_MARKET_PLANE", "label": "Market Plane", "desc": "asset universes and basket routing", "terms": [("crypto basket", "forex basket", "macro basket", "cross-market basket"), ("liquidity stream", "cycle stream", "volatility stream", "fractal stream"), ("leader set", "rotation set", "hedge set", "stress set"), ("thesis window", "transition window", "execution window", "review window")]},
    {"key": "execution", "dir": "08_PLANES/03_EXECUTION_PLANE", "label": "Execution Plane", "desc": "signals, risk, portfolio logic, action grammar", "terms": [("signal stack", "risk stack", "portfolio stack", "order stack"), ("entry gate", "hold gate", "exit gate", "loop gate"), ("sizing rule", "stop rule", "transfer rule", "rebuild rule"), ("journal packet", "alert packet", "execution packet", "audit packet")]},
    {"key": "governance", "dir": "08_PLANES/04_GOVERNANCE_PLANE", "label": "Governance Plane", "desc": "ledgers, truth typing, replay, deployment", "terms": [("evidence table", "replay capsule", "truth corridor", "deployment corridor"), ("pin ledger", "residual ledger", "ambiguity ledger", "conflict ledger"), ("verification path", "promotion path", "rollback path", "publication path"), ("container pack", "import pack", "observer pack", "conductor pack")]},
]

CHAPTER_NOTES = {
    "Ch01": "Locates the pre-framework Trading Bot body and names the difference between an analytical kernel and a living manuscript system.",
    "Ch02": "Binds the Trading Bot body back into the wider Athena corpus and identifies what arrived late or not at all.",
    "Ch03": "Translates square, circle, triangle, and fractal into direct trading language without losing higher-dimensional meaning.",
    "Ch04": "States the kernel algebra in market-facing terms and shows where the current runtime already encodes it.",
    "Ch05": "Maps the time-fractal engine to actual market-reading responsibilities rather than abstract theory.",
    "Ch06": "Explains how crypto, forex, and macro surfaces form one atlas rather than separate folders.",
    "Ch07": "Uses the 256-state hologram as a timing lattice instead of leaving it trapped in memory manuscripts.",
    "Ch08": "Turns the signal hierarchy into a full internal language of ranking, escalation, and routing.",
    "Ch09": "Specifies how corridor logic constrains exposure, sizing, stops, and legal action zones.",
    "Ch10": "Moves from reading to doing by defining execution grammar and transfer discipline.",
    "Ch11": "Holds the zero-point honesty law: structure can be read, exact manifestation cannot be forced.",
    "Ch12": "Defines what proof, replay, and verification should mean in this internal body.",
    "Ch13": "Materializes an emergent swarm that owns the framework instead of merely decorating it.",
    "Ch14": "Shows how the lines, hubs, and transfers actually move attention and action.",
    "Ch15": "Specifies how the Trading Bot body attaches to the larger Athena mycelium without semantic drift.",
    "Ch16": "Builds the multi-asset, multi-timescale tensor needed for portfolio-level reasoning.",
    "Ch17": "Gives forex its own strong line instead of treating it as a side annex to crypto.",
    "Ch18": "Gives crypto its own strong line with cycle, signal, and governance structure.",
    "Ch19": "Turns truth typing, ledgers, and promotion into actual governance rather than headings.",
    "Ch20": "Describes the route from manuscript shell to deployment, monitoring, and maintenance.",
    "Ch21": "Defines the perpetual deepen-review-rebuild loop that prevents stagnation.",
}

APPENDIX_NOTES = {
    "AppA": "Pins the input contract so evidence can enter the framework without semantic blur.",
    "AppB": "Keeps source origin visible as the body evolves.",
    "AppC": "Defines address logic for assets, states, and discrete grid structure.",
    "AppD": "Defines cycle, phase, and toroidal return semantics.",
    "AppE": "Carries corridor legality, position governance, and decision thresholds.",
    "AppF": "Defines recursive rebuild, swarm return, and replay recursion.",
    "AppG": "Specifies the signal object that the rest of the body should route around.",
    "AppH": "Collects risk controls into one auditable surface.",
    "AppI": "Defines what counts as OK, NEAR, AMBIG, and FAIL inside trading research.",
    "AppJ": "Preserves residuals so approximate structure is not confused with full proof.",
    "AppK": "Preserves contradiction and fences it instead of hiding it.",
    "AppL": "Turns uncertainty into bounded evidence plans and decision branches.",
    "AppM": "Defines the snap-to-canonical mechanism for competing market views.",
    "AppN": "Connects manuscript logic to folders, scripts, containers, and monitors.",
    "AppO": "Separates internal and external publication surfaces.",
    "AppP": "Connects the Trading Bot body to the wider Athena mycelium.",
}


def txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def ded(text: str) -> str:
    return dedent(text).strip() + "\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def b4(num: int, width: int = 4) -> str:
    out = []
    n = num
    for _ in range(width):
        out.append(str(n % 4))
        n //= 4
    return "".join(reversed(out))


def idx(seed: str, size: int) -> int:
    return int(md5(seed.encode("utf-8")).hexdigest()[:8], 16) % size


def picks(items: list[str], seed: str, count: int = 3) -> list[str]:
    if not items:
        return []
    start = idx(seed, len(items))
    return [items[(start + i) % len(items)] for i in range(count)]


def classes(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    return [n.name for n in tree.body if isinstance(n, ast.ClassDef)]


def atlas_summary() -> dict[str, object]:
    raw = json.loads(txt(ATLAS)) if ATLAS.exists() else {"records": []}
    body, ext, kind = Counter(), Counter(), Counter()
    for rec in raw.get("records", []):
        rp = str(rec.get("relative_path", "")).replace("\\", "/")
        top = rp.split("/", 1)[0] if rp else "<root>"
        body[top] += 1
        ext[rec.get("extension") or Path(rp).suffix or "<none>"] += 1
        kind[str(rec.get("kind", "unknown"))] += 1
    return {"records": len(raw.get("records", [])), "body": body, "ext": ext, "kind": kind}


def kw_counts(text: str) -> Counter:
    low = text.lower()
    keys = ["square", "circle", "triangle", "fractal", "metro", "time", "kernel", "state", "256", "torus", "tunnel"]
    return Counter({k: len(re.findall(rf"\b{k}\b", low)) for k in keys})


def rx(pattern: str, text: str, default: str = "unknown") -> str:
    m = re.search(pattern, text, re.MULTILINE)
    return m.group(1) if m else default


SUMMARY = atlas_summary()
DOCX_TEXT = txt(DOCX)
HOLO_TEXT = txt(HOLO)
TR_TEXT = txt(TR)
FR_TEXT = txt(FR)
COUNTS = kw_counts(DOCX_TEXT + "\n" + HOLO_TEXT)
ENGINE_CLASSES = classes(ENGINE)
SIGNAL_CLASSES = classes(SIGNALS)
ASSETS = sorted(p.stem.replace("_full_history", "") for p in (CRYPTO / "data").glob("*_full_history.csv"))
PAIRS = sorted(p.stem.replace("_history", "") for p in (CRYPTO / "forex_data").glob("USD_*_history.csv"))
DSI = rx(r"Total DSI detections:\s+([0-9]+)", TR_TEXT)
ALIGN = rx(r"Average kernel alignment:\s+([0-9.]+%)", TR_TEXT)
FX_DAYS = rx(r"Dataset:\s+([0-9,]+ trading days)", FR_TEXT)
FX_PERIOD = rx(r"Period:\s+([0-9\-]+\s+to\s+[0-9\-]+)", FR_TEXT)


def folder_stats(root: Path, folders: list[str]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for folder in folders:
        files = list((root / folder).rglob("*.md"))
        words = [len(p.read_text(encoding="utf-8", errors="ignore").split()) for p in files]
        stats[folder] = {
            "files": len(files),
            "avg_words": round(sum(words) / len(words), 1) if words else 0.0,
            "min_words": min(words) if words else 0.0,
            "max_words": max(words) if words else 0.0,
        }
    return stats


BASELINE_STATS = folder_stats(
    OUT,
    ["00_CONTROL", "01_ATLAS", "02_KERNEL", "03_METRO", "04_SWARM", "06_APPENDICES", "07_MANUSCRIPTS", "08_PLANES", "09_LEDGERS"],
) if OUT.exists() else {}


def top_lines(counter: Counter, limit: int) -> str:
    return "\n".join(f"- `{k}`: {v}" for k, v in counter.most_common(limit))


def role(seed: str) -> tuple[str, str, str]:
    return ROLES[idx(seed, len(ROLES))]


def line(seed: str) -> tuple[str, str, str]:
    return LINES[idx(seed, len(LINES))]


def hubs(seed: str) -> tuple[tuple[str, str], tuple[str, str]]:
    a = idx(seed, len(HUBS))
    return HUBS[a], HUBS[(a + 3) % len(HUBS)]


def chapter(seed: str) -> tuple[str, str]:
    return CHAPTERS[idx(seed, len(CHAPTERS))]


def appendix(seed: str) -> tuple[str, str]:
    return APPENDICES[idx(seed, len(APPENDICES))]


def carrier_profile(addr: str) -> tuple[str, str]:
    c = Counter(addr)
    dom = max("0123", key=lambda d: (c[d], -int(d)))
    lines = [f"- `{CARRIERS[d][0]}`: {c[d]} slots -> {CARRIERS[d][1]}" for d in "0123"]
    return CARRIERS[dom][0], "\n".join(lines)


def add(files: dict[Path, str], relpath: str, text: str) -> None:
    files[OUT / relpath] = ded(text)


def readme(total: int) -> str:
    return ded(
        f"""
        # Trading Bot Athena 256x4

        This folder is the Athena-native manuscript shell for the Trading Bot body. It binds the live kernel, memory manuscripts, reports, swarm ownership, and metro routing into a four-plane 256-cell system.

        - Atlas records: `{SUMMARY["records"]}`
        - Trading Bot atlas body: `{SUMMARY["body"].get("Trading Bot", 0)}`
        - Crypto assets: `{len(ASSETS)}`
        - Forex pairs: `{len(PAIRS)}`
        - DSI detections: `{DSI}`
        - Average kernel alignment: `{ALIGN}`
        - Generated files: `{total}`

        ## 256^4 Law

        The filesystem materializes four 256-cell planes:

        - `kernel[256]`
        - `market[256]`
        - `execution[256]`
        - `governance[256]`

        The full cartesian `256^4` body is preserved as a routing tensor instead of being exploded into billions of fake files.

        ## Start Order

        1. `00_CONTROL/05_FULL_FRAMEWORK_SPECIFICATION.md`
        2. `10_INSPECTION/00_FRAMEWORK_PROGRESS_SYNTHESIS.md`
        3. `11_SELF_IMPROVEMENT_256X256/00_PLAN_LAW_256x256.md`
        4. `01_ATLAS/00_PROJECT_CORPUS_SYNTHESIS.md`
        5. `02_KERNEL/00_KERNEL_OVERVIEW.md`
        6. `03_METRO/00_SYSTEM_METRO_MAP.md`
        7. `07_MANUSCRIPTS/00_TITLE_ABSTRACT_REVIEW_METRO_MAP.md`
        8. `04_SWARM/00_SWARM_OVERVIEW.md`
        9. `08_PLANES/01_KERNEL_PLANE/INDEX.md`
        10. `09_LEDGERS/05_NEXT_EXPANSION_SEED.md`
        """
    )


def build() -> dict[Path, str]:
    files: dict[Path, str] = {}
    sources = [
        ("Corpus atlas", rel(ATLAS)),
        ("Signal runtime", rel(SIGNALS)),
        ("Time-fractal engine", rel(ENGINE)),
        ("Analysis pipeline", rel(PIPE)),
        ("Time-fractal report", rel(TR)),
        ("Forex report", rel(FR)),
        ("Memory extract", rel(DOCX)),
        ("Time hologram extract", rel(HOLO)),
    ]
    source_lines = "\n".join(f"- `{name}` -> `{path}`" for name, path in sources)

    control = {
        "00_CONTROL/00_SYSTEM_CHARTER.md": f"# System Charter\n\nThe Trading Bot already had real code, real reports, and real data. What it lacked was an Athena-native framework shell binding those surfaces together.\n\n## Sources\n\n{source_lines}",
        "00_CONTROL/01_CORPUS_AND_BODY_INTAKE.md": f"# Corpus And Body Intake\n\n- Total atlas records: `{SUMMARY['records']}`\n- Trading Bot records: `{SUMMARY['body'].get('Trading Bot', 0)}`\n- Engine classes: `{', '.join(ENGINE_CLASSES)}`\n- Runtime classes: `{', '.join(SIGNAL_CLASSES)}`\n\n## Top Bodies\n\n{top_lines(SUMMARY['body'], 12)}",
        "00_CONTROL/02_ADDRESS_LAW_256x4.md": "# Address Law 256x4\n\nEach manuscript plane uses a four-slot base-4 address from `0000` to `3333`.\n\n- `0 = Square`\n- `1 = Circle`\n- `2 = Triangle`\n- `3 = Fractal`\n\nThe four visible planes preserve the larger internal `256^4` tensor.",
        "00_CONTROL/03_BUILD_PROTOCOL.md": f"# Build Protocol\n\nRun:\n\n```powershell\npython \"{rel(Path(__file__))}\"\n```\n\nThe generator reads the atlas, Trading Bot code, reports, and memory extracts, then writes the full framework shell.",
        "00_CONTROL/04_TRADING_BOT_GAP_REPORT.md": "# Trading Bot Gap Report\n\nThe body already had a kernel, signals, data, and reports. The missing layer was integration: no manuscript shell, no metro map, no swarm ownership, and no unified address law.",
        "00_CONTROL/05_FULL_FRAMEWORK_SPECIFICATION.md": f"# Full Framework Specification\n\nThis framework joins five surfaces:\n\n- project corpus synthesis from `{rel(ATLAS)}`\n- memory doctrine from `{rel(DOCX)}` and `{rel(HOLO)}`\n- live analytical kernel from `{rel(ENGINE)}`\n- signal/risk runtime from `{rel(SIGNALS)}`\n- report evidence from `{rel(TR)}` and `{rel(FR)}`",
        "00_CONTROL/06_INFINITE_LOOP_RUNTIME.md": "# Infinite Loop Runtime\n\nThe system is built to cycle: ingest, score, compare, replay, ledger, and rebuild. That loop prevents the Trading Bot body from becoming a dead folder.",
        "00_CONTROL/07_GOOGLE_DOCS_GATE.md": "# Google Docs Gate\n\nA live Google Docs search was attempted but is still blocked by missing `credentials.json`. This build is grounded in the local corpus and Trading Bot surfaces.",
    }
    for p, t in control.items():
        add(files, p, t)

    atlas_docs = {
        "01_ATLAS/00_PROJECT_CORPUS_SYNTHESIS.md": f"# Project Corpus Synthesis\n\nThe Trading Bot body sits inside a larger atlas with `{SUMMARY['records']}` records.\n\n## Top Bodies\n\n{top_lines(SUMMARY['body'], 12)}\n\n## Extensions\n\n{top_lines(SUMMARY['ext'], 10)}\n\n## Kinds\n\n{top_lines(SUMMARY['kind'], 8)}",
        "01_ATLAS/01_TRADING_BOT_BODY.md": f"# Trading Bot Body\n\n- crypto assets: `{len(ASSETS)}`\n- forex pairs: `{len(PAIRS)}`\n- DSI detections in report: `{DSI}`\n- forex history window: `{FX_DAYS}` across `{FX_PERIOD}`",
        "01_ATLAS/02_MEMORY_DOC_INGEST.md": f"# Memory Doc Ingest\n\n## Core Memory Sources\n\n" + "\n".join(f"- `{m}`" for m in MEMORY) + f"\n\n## Extract Keyword Density\n\n- `square`: {COUNTS['square']}\n- `circle`: {COUNTS['circle']}\n- `triangle`: {COUNTS['triangle']}\n- `fractal`: {COUNTS['fractal']}\n- `metro`: {COUNTS['metro']}\n- `256`: {COUNTS['256']}",
        "01_ATLAS/03_CODE_SURFACE_MAP.md": f"# Code Surface Map\n\n## Engine Classes\n\n" + "\n".join(f"- `{c}`" for c in ENGINE_CLASSES) + f"\n\n## Runtime Classes\n\n" + "\n".join(f"- `{c}`" for c in SIGNAL_CLASSES),
        "01_ATLAS/04_DATA_SURFACE_MAP.md": "# Data Surface Map\n\n## Crypto Assets\n\n" + "\n".join(f"- `{a}`" for a in ASSETS) + "\n\n## Forex Pairs\n\n" + "\n".join(f"- `{p}`" for p in PAIRS),
        "01_ATLAS/05_REPORT_SURFACE_MAP.md": f"# Report Surface Map\n\n- DSI detections: `{DSI}`\n- Average kernel alignment: `{ALIGN}`\n- Forex report span: `{FX_DAYS}` / `{FX_PERIOD}`\n\nThe internal framework inherits these live findings instead of using placeholder prose.",
    }
    for p, t in atlas_docs.items():
        add(files, p, t)

    kernel_docs = {
        "02_KERNEL/00_KERNEL_OVERVIEW.md": f"# Kernel Overview\n\nThe Trading Bot kernel already expresses a higher-dimensional market language through `{rel(ENGINE)}`, `{rel(SIGNALS)}`, and `{rel(TR)}`.",
        "02_KERNEL/01_SQUARE_CIRCLE_TRIANGLE_FRACTAL.md": "# Square Circle Triangle Fractal\n\n- `Square`: addresses, state tables, measurable partitions\n- `Circle`: phase rotation, cycle timing, toroidal return\n- `Triangle`: control law, risk, corridor legality\n- `Fractal`: replay, swarm emergence, recursive rebuild",
        "02_KERNEL/02_TIME_FRACTAL_ENGINE_BINDING.md": "# Time Fractal Engine Binding\n\n" + "\n".join(f"- `{layer}`" for layer in LAYERS),
        "02_KERNEL/03_SIGNAL_HIERARCHY.md": "# Signal Hierarchy\n\n" + "\n".join(f"- `{s}`" for s in SIGNAL_TYPES),
        "02_KERNEL/04_MARKET_STATE_VECTOR.md": "# Market State Vector\n\nThe bot reads structure, phase quality, volatility, signal strength, corridor legality, and replay confidence as one state vector.",
        "02_KERNEL/05_ORACLE_UNCERTAINTY.md": "# Oracle Uncertainty\n\nThe system reads regime quality honestly and refuses to pretend it knows exact manifestation ahead of time.",
        "02_KERNEL/06_TOROIDAL_RUNTIME.md": "# Toroidal Runtime\n\nTime is treated as a nested return body rather than a line. This is why the framework is a metro, not a flat note.",
        "02_KERNEL/07_256_STATE_HOLOGRAM.md": "# 256 State Hologram\n\nThe Trading Bot time manuscripts already argued for 256-state timing resolution. This framework turns that into a reusable internal timing lattice.",
        "02_KERNEL/08_256X4_TRADING_CRYSTAL.md": "# 256x4 Trading Crystal\n\nThe visible shell is four 256-cell planes: kernel, market, execution, governance. Their cross-product is the internal `256^4` tensor.",
    }
    for p, t in kernel_docs.items():
        add(files, p, t)

    metro = "\n".join(f"- `{c} {n}`: {d}" for c, n, d in LINES)
    hubs_md = "\n".join(f"- `{c} {n}`" for c, n in HUBS)
    metro_docs = {
        "03_METRO/00_SYSTEM_METRO_MAP.md": "# System Metro Map\n\n```mermaid\nflowchart LR\n    A[\"Atlas Line\"] --> B[\"Memory Line\"]\n    B --> C[\"Kernel Line\"]\n    C --> D[\"Market Line\"]\n    D --> E[\"Signal Line\"]\n    E --> F[\"Risk Line\"]\n    F --> G[\"Replay Line\"]\n    G --> H[\"Deployment Line\"]\n```\n\n## Lines\n\n" + metro + "\n\n## Hubs\n\n" + hubs_md,
        "03_METRO/01_LINES_AND_HUBS.md": "# Lines And Hubs\n\n" + metro + "\n\n" + hubs_md,
        "03_METRO/02_ASSET_RING.md": f"# Asset Ring\n\nThe market ring combines `{len(ASSETS)}` crypto assets and `{len(PAIRS)}` forex pairs into one transit body.",
        "03_METRO/03_SIGNAL_RING.md": "# Signal Ring\n\n" + "\n".join(f"- `{s}`" for s in SIGNAL_TYPES),
        "03_METRO/04_RISK_CORRIDORS.md": "# Risk Corridors\n\nRisk corridors translate the triangle carrier into exposure, stop, and legality rules.",
        "03_METRO/05_EXECUTION_TRANSFERS.md": "# Execution Transfers\n\nSignals do not finish at scoring. They transfer through thesis, order, journal, replay, and audit.",
        "03_METRO/06_TENSOR_COORDINATES.md": "# Tensor Coordinates\n\nEvery point can be written as `plane.address.role.task.atom.chapter.appendix.line.hub`.",
        "03_METRO/07_CROSS_CORPUS_CONNECTORS.md": "# Cross Corpus Connectors\n\nTrading Bot now routes back into the wider Athena corpus through the atlas, deeper crystallization bodies, and metro-style manuscript systems.",
        "03_METRO/08_TORUS_AND_RETURN.md": "# Torus And Return\n\nIntake becomes signal, signal becomes execution, execution becomes replay, and replay rewrites intake. That is the toroidal return path.",
    }
    for p, t in metro_docs.items():
        add(files, p, t)

    swarm_docs = {
        "04_SWARM/00_SWARM_OVERVIEW.md": "# Swarm Overview\n\nThe Trading Bot framework is maintained by roles, task cells, and output atoms so the manuscript body stays tied to real operating functions.",
        "04_SWARM/01_ROLE_MATRIX.md": "# Role Matrix\n\n" + "\n".join(f"- `{c} {n}`: {d}" for c, n, d in ROLES),
        "04_SWARM/02_TASK_CELL_INDEX.md": "# Task Cell Index\n\nTask cells are the 64 three-slot micro-loops bridging roles and outputs.",
        "04_SWARM/03_OUTPUT_ATOM_INDEX.md": "# Output Atom Index\n\nOutput atoms are the 256 atomic manuscript packets of the system.",
        "04_SWARM/04_37_GATE_EXECUTION_LOOP.md": "# 37 Gate Execution Loop\n\nThe loop detects the current gap, routes it through evidence and execution, then re-enters the manuscript body with a stronger pass.",
        "04_SWARM/05_HIGHER_DIMENSIONAL_SWARM.md": "# Higher Dimensional Swarm\n\nThe swarm has vertical depth, lateral spread across assets, recursive review depth, and toroidal return through replay.",
        "04_SWARM/06_TOROIDAL_SWARM_RUNTIME.md": "# Toroidal Swarm Runtime\n\nRoles hand work to task cells, task cells emit atoms, atoms feed chapters and ledgers, and the whole body returns to the swarm.",
    }
    for p, t in swarm_docs.items():
        add(files, p, t)
    add(files, "04_SWARM/roles/INDEX.md", "# Roles\n\n" + "\n".join(f"- `{c}` {n}" for c, n, _ in ROLES))
    for code, name, desc in ROLES:
        add(files, f"04_SWARM/roles/{slug(code + '_' + name)}.md", f"# {code} {name}\n\n{desc}\n\n- keep the framework bound to live evidence\n- maintain metro connectivity\n- prevent manuscript drift away from code reality")
    add(files, "04_SWARM/task_cells/INDEX.md", "# Task Cells\n\n64 task cells bridge roles and output atoms.")
    add(files, "04_SWARM/output_atoms/INDEX.md", "# Output Atoms\n\n256 output atoms provide the atomic packets of the framework.")
    task_terms = [["intake", "phase", "risk", "replay"], ["crypto", "forex", "macro", "cross"], ["scan", "synthesize", "route", "certify"]]
    atom_terms = [["seed", "cycle", "signal", "swarm"], ["snapshot", "alignment", "transition", "echo"], ["thesis", "execution", "ledger", "repair"], ["note", "packet", "certificate", "loop"]]
    for i in range(64):
        addr = b4(i, 3)
        parts = [task_terms[n][int(d)] for n, d in enumerate(addr)]
        r = role(f"task:{addr}")
        ln = line(f"task:{addr}")
        add(files, f"04_SWARM/task_cells/task_{addr}.md", f"# Task Cell {addr}\n\nTask cell `{addr}` combines `{parts[0]}`, `{parts[1]}`, and `{parts[2]}`.\n\n- owner: `{r[0]} {r[1]}`\n- primary line: `{ln[0]} {ln[1]}`")
    for i in range(256):
        addr = b4(i, 4)
        parts = [atom_terms[n][int(d)] for n, d in enumerate(addr)]
        ch = chapter(f"atom:{addr}")
        ap = appendix(f"atom:{addr}")
        add(files, f"04_SWARM/output_atoms/atom_{addr}.md", f"# Output Atom {addr}\n\n- `{parts[0]}`\n- `{parts[1]}`\n- `{parts[2]}`\n- `{parts[3]}`\n\n- chapter anchor: `{ch[0]} {ch[1]}`\n- appendix anchor: `{ap[0]} {ap[1]}`")

    add(files, "07_MANUSCRIPTS/00_TITLE_ABSTRACT_REVIEW_METRO_MAP.md", "# Trading Bot Athena 256x4\n\nThis manuscript body treats the Trading Bot as a higher-dimensional market intelligence system whose live code, data, reports, and memory docs can be folded into one metro-routable operating shell.\n\n## Chapter Spine\n\n" + "\n".join(f"- `{c}`: {t}" for c, t in CHAPTERS) + "\n\n## Appendix Spine\n\n" + "\n".join(f"- `{c}`: {t}" for c, t in APPENDICES) + "\n\n## Current Shadow\n\nThe framework achieved breadth first. The next step is to deepen manuscript density, strengthen cross-plane navigation, and formalize self-improvement as a first-class internal law.")
    add(files, "07_MANUSCRIPTS/chapters/INDEX.md", "# Chapters\n\n" + "\n".join(f"- `{c}` {t}" for c, t in CHAPTERS))
    for code, title in CHAPTERS:
        ln = line(code)
        ap = appendix(code)
        note = CHAPTER_NOTES[code]
        add(files, f"07_MANUSCRIPTS/chapters/{code}_{slug(title)}.md", f"# {code} {title}\n\n## Focus\n\n{note}\n\n## Bound Route\n\n- line: `{ln[0]} {ln[1]}`\n- appendix: `{ap[0]} {ap[1]}`\n- source anchors: `{rel(ENGINE)}`, `{rel(SIGNALS)}`, `{rel(TR)}`\n\n## Current Progress\n\nThe current framework already names this chapter as part of the full body. The live code and reports prove the subject exists. What still matters is deepening this chapter from structural heading into a full internal manuscript surface.\n\n## Shadow And Gap\n\nThe present build shows breadth before density. This chapter is therefore strong as a coordinate and weak as a finished theorem. Its next growth edge is to bind more direct code evidence, report evidence, and cross-plane consequences into one sustained argument.\n\n## Actuation Vector\n\n- clarify how this chapter changes behavior in the bot\n- bind it to swarm ownership and replay expectations\n- route its outputs into at least one kernel, market, execution, and governance cell")

    add(files, "06_APPENDICES/INDEX.md", "# Appendices\n\n" + "\n".join(f"- `{c}` {t}" for c, t in APPENDICES))
    for code, title in APPENDICES:
        note = APPENDIX_NOTES[code]
        add(files, f"06_APPENDICES/{code}_{slug(title)}.md", f"# {code} {title}\n\n## Appendix Duty\n\n{note}\n\n## Why It Exists\n\nThis appendix keeps the main body from becoming hand-wavy. It provides one of the strict support surfaces needed to hold evidence, legality, interpretation, or replay in place.\n\n## Current Gap\n\nThe appendix exists as a strong coordinate but still needs deeper population with examples, contracts, and failure cases. That gap is now explicitly carried into the self-improvement corpus.")

    ledgers = {
        "09_LEDGERS/00_SOURCE_BINDING.md": "# Source Binding\n\n" + source_lines,
        "09_LEDGERS/01_CODE_BINDING.md": f"# Code Binding\n\n- engine classes: `{', '.join(ENGINE_CLASSES)}`\n- runtime classes: `{', '.join(SIGNAL_CLASSES)}`\n- layers: `{', '.join(LAYERS)}`\n- signal types: `{', '.join(SIGNAL_TYPES)}`",
        "09_LEDGERS/02_DATA_BINDING.md": f"# Data Binding\n\n- crypto assets: `{len(ASSETS)}`\n- forex pairs: `{len(PAIRS)}`\n- DSI detections: `{DSI}`\n- forex window: `{FX_DAYS}` / `{FX_PERIOD}`",
        "09_LEDGERS/03_MEMORY_DOC_BINDING.md": "# Memory Doc Binding\n\n" + "\n".join(f"- `{m}`" for m in MEMORY) + f"\n\n- `square`: {COUNTS['square']}\n- `circle`: {COUNTS['circle']}\n- `triangle`: {COUNTS['triangle']}\n- `fractal`: {COUNTS['fractal']}\n- `metro`: {COUNTS['metro']}",
        "09_LEDGERS/04_CORPUS_CONNECTOR_LEDGER.md": "# Corpus Connector Ledger\n\n" + top_lines(SUMMARY["body"], 12),
        "09_LEDGERS/05_NEXT_EXPANSION_SEED.md": "# Next Expansion Seed\n\nDeepen live Docs ingress once credentials exist, attach replay harnesses to the manuscripts, and keep routing the build back through the living loop.",
    }
    for p, t in ledgers.items():
        add(files, p, t)

    ch_stats = BASELINE_STATS.get("07_MANUSCRIPTS", {})
    ap_stats = BASELINE_STATS.get("06_APPENDICES", {})
    sw_stats = BASELINE_STATS.get("04_SWARM", {})
    mt_stats = BASELINE_STATS.get("03_METRO", {})
    insp = {
        "10_INSPECTION/00_FRAMEWORK_PROGRESS_SYNTHESIS.md": f"# Framework Progress Synthesis\n\nThe framework now has real breadth: 4 planes, 21 chapter coordinates, 16 appendices, 16 swarm roles, 64 task cells, 256 output atoms, and 1028 plane files. The progress is structural and genuine.\n\n## What Is Already Working\n\n- the Trading Bot kernel and runtime are bound into the shell\n- the atlas, memory docs, and reports are explicitly surfaced\n- the metro, swarm, and plane bodies exist as one navigable corpus\n- the `256^4` law is encoded honestly as a visible four-plane system\n\n## Current Limitation\n\nThe current weakness is density. Before this actuation pass, chapter files averaged `{ch_stats.get('avg_words', 0)}` words, appendices averaged `{ap_stats.get('avg_words', 0)}`, metro docs averaged `{mt_stats.get('avg_words', 0)}`, and swarm docs averaged `{sw_stats.get('avg_words', 0)}`. The body was highly addressable but not yet equally deep everywhere.",
        "10_INSPECTION/01_METRO_NAVIGATION_OBSERVATION.md": "# Metro Navigation Observation\n\nThe declared line order is coherent: Atlas -> Memory -> Kernel -> Market -> Signal -> Risk -> Replay -> Deployment. The system therefore already has a valid navigation spine.\n\nThe gap is that most transfers are still declarative rather than path-checked. Hubs are named, but many routes are not yet demonstrated with concrete multi-step examples, replay packets, or decision traces.",
        "10_INSPECTION/02_HOLOGRAPHIC_FRACTAL_GAP_REPORT.md": "# Holographic Fractal Gap Report\n\n## Gap 1: Breadth exceeds density\nThe framework expanded quickly into many files, but its chapter and appendix prose remained too thin.\n\n## Gap 2: Metro is named more than traversed\nThe lines and hubs exist, but route proofs are still sparse.\n\n## Gap 3: Swarm is named more than behaviorally integrated\nRoles, task cells, and atoms exist, but ownership is not yet propagated into enough concrete examples.\n\n## Gap 4: The fractal loop is stated more than executed\nInfinite recursion is present as doctrine, but the self-improvement loop was not yet a first-class corpus surface.\n\n## Gap 5: Cross-plane integration is shallow\nMany plane cells point to one another, but there was no dedicated plan body explaining how to strengthen those couplings over time.",
        "10_INSPECTION/03_SHADOW_MATRIX.md": "# Shadow Matrix\n\n## Absent Element Shadow\nThe weakest element was deep Earth-like implementation density: many coordinates, fewer sustained examples.\n\n## Axis Shadow\nThe build privileged structure over time-evolving maturation. It needed a stronger maintenance and repair axis.\n\n## Cross-Synthesis Shadow\nThe thinnest pair was metro x swarm: routes were declared, but operational custody remained light.\n\n## Meta Shadow\nThe crystal shape was strong, but the self-repair mechanism was underdeveloped.\n\n## Context Shadow\nThe live code was present, yet not enough chapter and appendix text was directly quoting or unpacking it.",
        "10_INSPECTION/04_HIDDEN_LINES_AND_HUBS.md": "# Hidden Lines And Hubs\n\n## Hidden Lines\n\n- `Evidence Line`: atlas -> reports -> ledgers -> replay\n- `Timing Line`: memory docs -> kernel -> 256-state hologram -> execution windows\n- `Risk Line`: signal hierarchy -> corridors -> governance plane\n- `Repair Line`: infinite loop runtime -> swarm -> next expansion seed\n- `Mycelium Line`: corpus connectors -> metro -> deployment\n\n## Zero Hub\n\n`Kernel Line` is the true transfer center because the memory doctrine, market data, signals, and governance all pass through it.",
        "10_INSPECTION/05_ACTUATION_WAVE_0.md": "# Actuation Wave 0\n\nThis pass actuates the inspection immediately by:\n\n- thickening chapter and appendix templates so they carry focus, gap, and actuation sections\n- materializing a dedicated self-improvement corpus\n- turning the previous one-line expansion seed into a deeper improvement program\n- preserving the local-code-first evidence floor while Google Docs access remains blocked",
    }
    for p, t in insp.items():
        add(files, p, t)

    improve_terms = [
        ["density", "routing", "swarm", "recursion"],
        ["control", "atlas", "market", "governance"],
        ["repair", "expand", "verify", "integrate"],
        ["seed", "relay", "audit", "renew"],
    ]
    improve_dirs = {
        "11_SELF_IMPROVEMENT_256X256/00_PLAN_LAW_256x256.md": "# Plan Law 256x256\n\nThe deepest self-improvement body is encoded as a `256^256` recursive manuscript law.\n\nVisible layer: one fully materialized 256-step root octave.\nRecursive law: every visible step can itself unfold into another 256-step octave when local depth is exhausted.\n\nThis is the only honest way to carry `256^256` without creating a fake filesystem explosion.",
        "11_SELF_IMPROVEMENT_256X256/01_METRO_OF_IMPROVEMENT.md": "# Metro Of Improvement\n\nThe improvement metro runs:\n\nAtlas diagnosis -> kernel diagnosis -> metro proof -> swarm proof -> chapter deepening -> appendix deepening -> cross-plane coupling -> replay -> deployment -> loop restart.",
        "11_SELF_IMPROVEMENT_256X256/02_ACTUATION_PROTOCOL.md": "# Actuation Protocol\n\n1. inspect the current body honestly\n2. name the shadow\n3. choose the smallest repair that changes future behavior\n4. route the repair through code, docs, metro, and governance\n5. record the repair in ledgers\n6. restart the loop with stronger density",
        "11_SELF_IMPROVEMENT_256X256/03_PRIORITY_STACK.md": f"# Priority Stack\n\n1. Deepen manuscript density: chapter average was `{ch_stats.get('avg_words', 0)}` words before this pass.\n2. Deepen appendix density: appendix average was `{ap_stats.get('avg_words', 0)}` words.\n3. Strengthen swarm-to-metro proofs.\n4. Add replay-grade examples.\n5. Increase cross-plane causality instead of simple mirroring.",
        "11_SELF_IMPROVEMENT_256X256/04_WAVE_0_IMPLEMENTED.md": "# Wave 0 Implemented\n\nWave 0 is the actuation already completed in this pass: the framework now contains an inspection body and a recursive self-improvement body, and the chapter/appendix surfaces are richer than the previous generation.",
        "11_SELF_IMPROVEMENT_256X256/steps/INDEX.md": "# Improvement Steps\n\nThese 256 visible steps are the root octave of the larger `256^256` improvement law.",
    }
    for p, t in improve_dirs.items():
        add(files, p, t)
    for i in range(256):
        addr = b4(i, 4)
        parts = [improve_terms[n][int(d)] for n, d in enumerate(addr)]
        ln = line(f"improve:{addr}")
        ha, hb = hubs(f"improve:{addr}")
        r = role(f"improve:{addr}")
        ch = chapter(f"improve:{addr}")
        ap = appendix(f"improve:{addr}")
        add(
            files,
            f"11_SELF_IMPROVEMENT_256X256/steps/improve_{addr}_{slug('_'.join(parts[:2]))}.md",
            f"# Improvement Step {addr}\n\n## Improvement Signature\n\n- `{parts[0]}` -> `{parts[1]}` -> `{parts[2]}` -> `{parts[3]}`\n- role owner: `{r[0]} {r[1]}`\n- metro route: `{ln[0]} {ln[1]}` via `{ha[0]} {ha[1]}` -> `{hb[0]} {hb[1]}`\n- chapter anchor: `{ch[0]} {ch[1]}`\n- appendix anchor: `{ap[0]} {ap[1]}`\n\n## Gap Addressed\n\nThis step repairs a local weakness where `{parts[0]}` has not yet been fully carried through `{parts[1]}` into `{parts[2]}` and `{parts[3]}`.\n\n## Concrete Actuation\n\n- inspect the target files attached to this coordinate\n- deepen at least one explanation, one route, and one replay expectation\n- push the repaired knowledge back into the loop so the next octave starts stronger\n\n## Recursive Law\n\nIf this step saturates, expand it into its own 256-step child plan instead of pretending the work is finished.",
        )

    for plane in PLANES:
        add(files, f"{plane['dir']}/INDEX.md", f"# {plane['label']}\n\n{plane['desc']}\n\nEach file in this plane is one four-slot base-4 manuscript address.")
        for i in range(256):
            addr = b4(i, 4)
            comp = [plane["terms"][n][int(d)] for n, d in enumerate(addr)]
            dom, profile = carrier_profile(addr)
            r = role(f"{plane['key']}:{addr}")
            ln = line(f"{plane['key']}:{addr}")
            ha, hb = hubs(f"{plane['key']}:{addr}")
            ch = chapter(f"{plane['key']}:{addr}")
            ap = appendix(f"{plane['key']}:{addr}")
            market = addr[1:] + addr[:1]
            exe = "".join(str(3 - int(d)) for d in addr)
            gov = addr[::-1]
            crypto = ", ".join(picks(ASSETS, f"crypto:{plane['key']}:{addr}", 3))
            forex = ", ".join(picks(PAIRS, f"forex:{plane['key']}:{addr}", 3))
            add(files, f"{plane['dir']}/cells/{plane['key']}_{addr}_{slug('_'.join(comp[:2]))}.md", f"# {plane['label']} {addr}\n\n## Address Signature\n\n- plane: `{plane['key']}`\n- address: `{addr}`\n- components: `{comp[0]}` -> `{comp[1]}` -> `{comp[2]}` -> `{comp[3]}`\n- dominant carrier: `{dom}`\n\n## Carrier Profile\n\n{profile}\n\n## Live Bindings\n\n- `{rel(SIGNALS)}`\n- `{rel(ENGINE)}`\n- `{rel(TR)}`\n- `{rel(FR)}`\n\nSample crypto focus: `{crypto}`\nSample forex focus: `{forex}`\n\n## Metro Connectivity\n\n- line: `{ln[0]} {ln[1]}`\n- hubs: `{ha[0]} {ha[1]}` -> `{hb[0]} {hb[1]}`\n- role: `{r[0]} {r[1]}`\n- chapter: `{ch[0]} {ch[1]}`\n- appendix: `{ap[0]} {ap[1]}`\n- task cell: `04_SWARM/task_cells/task_{addr[:3]}.md`\n- output atom: `04_SWARM/output_atoms/atom_{addr}.md`\n\n## 256^4 Expansion Vector\n\n- kernel address: `{addr if plane['key'] == 'kernel' else market}`\n- market address: `{addr if plane['key'] == 'market' else market}`\n- execution address: `{addr if plane['key'] == 'execution' else exe}`\n- governance address: `{addr if plane['key'] == 'governance' else gov}`")
    return files


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = build()
    for path, text in files.items():
        write(path, text)
    total = sum(1 for p in OUT.rglob("*") if p.is_file())
    write(OUT / "README.md", readme(total))
    print(f"Generated {total} files at {OUT}")


if __name__ == "__main__":
    main()
