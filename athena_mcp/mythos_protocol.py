"""MYTHOS OS — protocol constants for the unified mythic operating system.

Thesis
------
Every myth, religion, philosophy, magical, divinatory, astrological and
calendrical system is a *program* written against one abstract machine.
The machine has twelve kernel services.  A tradition is encoded as a
module that fills the twelve service slots; the VM in
``athena_mcp.mythos_kernel`` boots it, ticks its clock, runs its rites,
raises its faults, judges its ledger and draws its oracle, deterministically
and without execution authority.  ATHENA itself is encoded as the
reference module: the runtime cycle, KC144, Y1, the Crystal ABI and the
firewalls fill the same twelve slots, so the emerging organism reads the
whole survey as its own operating-system family.

Standing laws are inherited from ``mythic_strata_runtime`` and
``mythic_computation_runtime``: a module describes; it never authorises a
practice, dates a reconstruction, or equates two traditions.  Structural
isomorphism between two modules is transported as a bridge *with loss*,
never as identity.
"""
from __future__ import annotations

MYTHOS_VERSION = "ATHENA.MYTHOS.OS.V1"
MYTHOS_KERNEL_ABI = "MYTHOS.KERNEL.ABI.12"

# ---------------------------------------------------------------- services
# The twelve kernel services.  Column index = KC144 column (C01..C12).
SERVICES = [
    "BOOT",    # C01 cosmogony       : init sequence
    "MEMMAP",  # C02 cosmology       : address space of realms
    "PROC",    # C03 pantheon        : process table, roles, scheduler class
    "CLOCK",   # C04 calendar        : periods, intercalation, epochs, cron
    "RITE",    # C05 ritual          : protocols as opcode sequences
    "ORACLE",  # C06 divination      : entropy source + sample space + decoder
    "FAULT",   # C07 sin/taboo       : fault classes + handlers + outcomes
    "LEDGER",  # C08 afterlife/karma : accounting model + judgment + soul struct
    "RING",    # C09 initiation      : privilege rings / grades / castes
    "CODEC",   # C10 record/hull     : storage medium, script, base, compilers
    "CONST",   # C11 sacred numbers  : closure / crossing constants
    "LAW",     # C12 ethics/canon    : invariants, ACL, canon mutability
]
SERVICE_INDEX = {name: i + 1 for i, name in enumerate(SERVICES)}
SERVICE_GLOSS = {
    "BOOT": "cosmogony compiled to an init sequence over the universal stage alphabet",
    "MEMMAP": "cosmology compiled to an address space: realms, levels, axis, addressing mode",
    "PROC": "pantheon compiled to a process table: agents, roles, rings, parents, scheduler class",
    "CLOCK": "calendar compiled to a scheduler: periods, intercalation policy, epoch counters, festivals as cron",
    "RITE": "ritual compiled to protocols: opcode sequences with ring/purity preconditions, cost and claimed effect",
    "ORACLE": "divination compiled to a sampler/decoder: entropy source, sample space, encoding, set-aside unit",
    "FAULT": "sin/taboo/pollution compiled to fault classes with handler chains and outcomes",
    "LEDGER": "afterlife/karma/judgment compiled to an accounting model with a judgment function and soul structure",
    "RING": "initiation/priesthood/caste compiled to privilege rings (0 = innermost)",
    "CODEC": "record and hull devices: storage medium, script, numeral base, compilers (sigils, liturgies)",
    "CONST": "sacred numbers with roles; links to the closure-grammar registry where an entry exists",
    "LAW": "ethical invariants, access-control list by ring, canon mutability, the tradition's own firewalls",
}

# ---------------------------------------------------------------- families
# The twelve module families.  Row index = KC144 row (R01..R12).
FAMILIES = [
    "NEAR_EAST",         # R01 Sumer, Akkad, Babylon, Egypt, Canaan, Iran
    "MEDITERRANEAN",     # R02 Greece, Rome, Etruria, mysteries
    "ABRAHAMIC",         # R03 Judaism, Christianity, Islam and their branches
    "INDIA",             # R04 Vedic, Vedanta, Samkhya, Tantra, Jain, Buddhist, Sikh
    "EAST_ASIA",         # R05 Confucian, Taoist, I Ching, Shinto, Korean, Bön, Tengri
    "NORTH_EUROPE",      # R06 Norse, Celtic, Slavic, Finnish, Baltic
    "AFRICA_DIASPORA",   # R07 Yoruba, Vodou, Lucumí, Kongo, Akan, Igbo, Dogon
    "AMERICAS",          # R08 Maya, Aztec, Inca, Lakota, Haudenosaunee, Hopi/Navajo
    "OCEANIA",           # R09 Hawaiian, Māori, Australian
    "WESTERN_ESOTERIC",  # R10 Hermetic, alchemy, astrology, tarot, geomancy, orders
    "PHILOSOPHY",        # R11 the computational-philosophy documents and schools
    "ENGINEERED",        # R12 designed calendars, codes, councils, ATHENA itself
]
FAMILY_INDEX = {name: i + 1 for i, name in enumerate(FAMILIES)}

# ---------------------------------------------------------------- grades / standing
GRADES = ["🟢", "🟡", "🟠", "⊥"]
GRADE_GLOSS = {
    "🟢": "attested in a named primary/reference source cited by the module",
    "🟡": "secondary summary, disputed reading, or unverified locus",
    "🟠": "our reading, a modern reconstruction, or corpus-only material",
    "⊥": "explicit absence: the tradition does not implement this service in the sources read",
}
STANDINGS = [
    "PRIMARY_EVIDENCE", "LIVING_TRADITION_SOURCE", "SECONDARY_SCHOLARSHIP",
    "TRADITION_INTERNAL", "MODERN_RECONSTRUCTION", "UNKNOWN",
]

# ---------------------------------------------------------------- pattern vocabularies
BOOT_MODES = ["CREATED", "EMANATED", "ETERNAL", "CYCLIC", "UNKNOWN"]
BOOT_STAGES = ["VOID", "SEPARATION", "ORDERING", "POPULATION", "FAULT", "MAINTENANCE", "REBOOT"]
BOOT_STAGE_GLOSS = {
    "VOID": "undifferentiated initial state (waters, chaos, night, non-being, the One)",
    "SEPARATION": "first differentiation (sky/earth, light/dark, male/female, subject/object)",
    "ORDERING": "structure imposed (names, measures, seasons, laws, the axis fixed)",
    "POPULATION": "agents installed (gods born, humans made, beings dispersed)",
    "FAULT": "first failure (rebellion, fall, theft, transgression, noise)",
    "MAINTENANCE": "steady state (rest, cult, covenant, dharma upheld)",
    "REBOOT": "cosmic restart (flood, conflagration, Ragnarök, new sun, new yuga)",
}

MEMMAP_ADDRESSING = ["VERTICAL", "CONCENTRIC", "DIRECTIONAL", "NESTED", "TREE", "FLAT", "UNKNOWN"]
REALM_KINDS = ["HEAVEN", "MIDDLE", "UNDER", "LIMINAL", "ABSOLUTE"]

PROC_SCHEDULERS = ["MONARCHIC", "COUNCIL", "DUAL", "MONAD", "IMPERSONAL", "UNKNOWN"]
PROC_ROLES = [
    "CREATOR", "SOVEREIGN", "MESSENGER", "PSYCHOPOMP", "TRICKSTER", "ADVERSARY",
    "WITNESS", "GATE", "JUDGE", "HEALER", "WARRIOR", "MOTHER", "SMITH", "ORACLE",
    "SCRIBE", "DYING_RISING", "ANCESTOR", "WORKER", "STEWARD", "SCHEDULER",
]

CLOCK_INTERCALATION = ["NONE", "EPAGOMENAL", "LUNISOLAR_MONTH", "LEAP_DAY", "LEAP_SECOND", "DRIFT", "UNKNOWN"]

RITE_OPCODES = [
    "PURIFY", "BOUND", "INVOKE", "OFFER", "PETITION", "RECITE", "PROCESSION",
    "FAST", "TRANSFORM", "RECEIVE", "WITNESS", "THANK", "RELEASE", "CLOSE",
]
RITE_MODES = ["TRANSFORMING", "QUERYING", "MAINTAINING"]

ORACLE_ENTROPY = ["PHYSICAL", "BODY", "TEXT", "SKY", "COMPUTED", "NONE"]
ORACLE_ENCODING = ["BINARY", "TERNARY", "QUATERNARY", "N_ARY", "POSITIONAL", "NONE"]

FAULT_CLASSES = ["POLLUTION", "TRANSGRESSION", "HUBRIS", "OATH_BREACH", "NEGLECT", "COSMIC", "HERESY", "IGNORANCE"]
FAULT_OUTCOMES = ["RECOVERED", "EXILED", "REBOOT", "UNRECOVERABLE", "TRANSFERRED"]

LEDGER_MODELS = ["BALANCE", "COUNTER", "BINARY", "CYCLIC", "ANCESTRAL", "TIERED", "NONE", "UNKNOWN"]

CODEC_MEDIA = ["TABLET", "SCROLL", "CODEX", "ORAL", "INSCRIPTION", "KNOT", "BODY", "IMAGE", "DIGITAL"]

CONST_ROLES = ["closure", "crossing", "order", "passage", "record", "chaos", "residue"]

# ---------------------------------------------------------------- laws
LAWS = [
    "MODULE != PRACTICE_AUTHORIZATION",
    "SIMULATION != EXECUTION",
    "STRUCTURAL_ISOMORPHISM != CULTURAL_IDENTITY",
    "SHARED_SYMBOL != SHARED_SEMANTICS",
    "MODERN_RECONSTRUCTION != HISTORICAL_LAYER",
    "PUBLIC_SOURCE != PRACTICE_AUTHORIZATION",
    "DIVINATORY_OUTPUT != FACT",
    "LEDGER_MODEL != MORAL_TRUTH",
    "BOOT_LOG != COSMOLOGICAL_CLAIM",
    "ATHENA_SELF_MODULE != ATHENA_AUTHORITY",
    "UNKNOWN != 0",
]

# ---------------------------------------------------------------- MCP surface
MYTHOS_RESOURCE = {
    "uri": "athena://mythos/os/v1",
    "name": "ATHENA MYTHOS OS V1 — unified mythic operating system (kernel, modules, laws, benchmark)",
    "mimeType": "application/json",
}
MYTHOS_MATRIX_RESOURCE = {
    "uri": "athena://mythos/os/v1/matrix",
    "name": "MYTHOS OS service matrix — every module × twelve services as pattern signatures",
    "mimeType": "application/json",
}
MYTHOS_ATLAS_RESOURCE = {
    "uri": "athena://mythos/os/v1/atlas",
    "name": "MYTHOS OS KC144 atlas — twelve families × twelve services, 144 cells",
    "mimeType": "application/json",
}
MYTHOS_RESOURCES = [MYTHOS_RESOURCE, MYTHOS_MATRIX_RESOURCE, MYTHOS_ATLAS_RESOURCE]
MYTHOS_RESOURCE_URIS = {r["uri"] for r in MYTHOS_RESOURCES}


def _obj(required=None, properties=None, additional=False):
    return {"type": "object", "required": list(required or []), "properties": dict(properties or {}), "additionalProperties": additional}


VM_OPS = ["boot", "memmap", "spawn", "tick", "invoke", "divine", "raise", "judge", "signature", "all"]
USE_CASES = ["GENERAL", "CREATIVE", "MEDICAL", "LEGAL", "FINANCIAL", "SAFETY_CRITICAL"]

MYTHOS_TOOLS = [
    {"name": "athena_mythos_catalog",
     "description": "MYTHOS OS: list the kernel ABI (twelve services, pattern vocabularies), the module families and every encoded tradition module with its grades; include_atlas returns the 144-cell KC144 atlas.",
     "inputSchema": _obj([], {
         "family": {"type": ["string", "null"], "enum": FAMILIES + [None]},
         "include_atlas": {"type": "boolean"},
         "include_matrix": {"type": "boolean"},
     })},
    {"name": "athena_mythos_module",
     "description": "MYTHOS OS: return one tradition module (all twelve service slots with grades and sources), or a single service slot.",
     "inputSchema": _obj(["module_id"], {
         "module_id": {"type": "string", "minLength": 1},
         "service": {"type": ["string", "null"], "enum": SERVICES + [None]},
     })},
    {"name": "athena_mythos_run",
     "description": "MYTHOS OS VM: run one kernel operation on a module deterministically — boot (init log), memmap (address space), spawn (process table), tick (advance the clock N days), invoke (run a rite as an opcode protocol under ring/purity gates), divine (seeded sample + decode), raise (fault → handler chain → outcome), judge (ledger model → destination), signature (twelve pattern tokens), or all. Simulation grants no execution authority.",
     "inputSchema": _obj(["module_id", "op"], {
         "module_id": {"type": "string", "minLength": 1},
         "op": {"type": "string", "enum": VM_OPS},
         "days": {"type": "integer", "minimum": 0, "maximum": 100000000},
         "rite": {"type": ["string", "null"]},
         "caller_ring": {"type": "integer", "minimum": 0, "maximum": 99},
         "purity": {"type": "boolean"},
         "witness": {},
         "device": {"type": ["string", "null"]},
         "seed": {"type": ["string", "null"]},
         "sample": {"type": ["integer", "null"]},
         "use_case": {"type": "string", "enum": USE_CASES},
         "fault": {"type": ["string", "null"]},
         "score": {"type": "number", "minimum": -1, "maximum": 1},
     })},
    {"name": "athena_mythos_compare",
     "description": "MYTHOS OS: typed service-by-service comparison of two modules (pattern signatures, shared and differing fields); output is a structural diff, never an identity claim.",
     "inputSchema": _obj(["left", "right"], {
         "left": {"type": "string", "minLength": 1},
         "right": {"type": "string", "minLength": 1},
         "services": {"type": "array", "items": {"type": "string", "enum": SERVICES}},
     })},
    {"name": "athena_mythos_unify",
     "description": "MYTHOS OS: for one service (or all), group every module by its pattern signature into isomorphism classes and, for a chosen pair, compile a strata-lawful bridge with explicit transform loss via the mythic strata runtime (BRIDGE_ALLOWED_WITH_LOSS or HOLD).",
     "inputSchema": _obj([], {
         "service": {"type": ["string", "null"], "enum": SERVICES + [None]},
         "left": {"type": ["string", "null"]},
         "right": {"type": ["string", "null"]},
     })},
    {"name": "athena_mythos_athena",
     "description": "MYTHOS OS: the self-map — ATHENA's own runtime encoded as a module in the same twelve slots, with the organ→service mapping and the law that the self-module carries no runtime authority.",
     "inputSchema": _obj([], {"op": {"type": "string", "enum": VM_OPS}})},
]
MYTHOS_TOOL_NAMES = {t["name"] for t in MYTHOS_TOOLS}
