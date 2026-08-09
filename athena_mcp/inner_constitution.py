from __future__ import annotations

from dataclasses import dataclass, asdict

ACTIVE_EPOCH = "EPOCH-B-EIGHT-BLOCK"


@dataclass(frozen=True)
class InnerSeat:
    gid: int
    block: str
    code: str
    role: str
    coordinate: str | None = None
    known_obligations: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        out = asdict(self)
        out["known_obligations"] = list(self.known_obligations)
        return out


def _h6() -> list[InnerSeat]:
    roles = [
        ("H01", "ADDRESS_IDENTITY_REGISTRY"),
        ("H02", "DOMAIN_PROJECTION_SEATING_ALIAS_REGISTRY"),
        ("H03", "MYCELIAL_NAVIGATION_REGISTRY"),
        ("H04", "INVARIANT_BRIDGE_DEFECT_REGISTRY"),
        ("H05", "SOURCE_EVIDENCE_VERSION_LEDGER"),
        ("H06", "ACTIVATION_REPLAY_RESEED_HUB"),
    ]
    return [InnerSeat(i + 1, "H6", code, role) for i, (code, role) in enumerate(roles)]


def _x16() -> list[InnerSeat]:
    pole_roles = {"11":"BODY_IDENTITY_SEED","10":"TRANSFORM_VECTOR","00":"INVARIANT_DEFECT","01":"RETURN_RECONSTRUCTION"}
    lens_roles = {"SQ":"EXACT_LOCAL","FL":"RELATIONAL_PROPAGATION","CL":"ALTERNATIVE_AMBIGUITY","FR":"RECURSIVE_SCALE"}
    out=[]; gid=7
    for pole in ("11","10","00","01"):
        for lens in ("SQ","FL","CL","FR"):
            out.append(InnerSeat(gid,"X16",f"X-{pole}-{lens}",f"{pole_roles[pole]}__{lens_roles[lens]}",coordinate=f"{pole}/{lens}")); gid+=1
    return out


def _br21() -> list[InnerSeat]:
    stages=("ADMIT","EXPAND","NAVIGATE","TRANSFORM","TEST","COMPRESS","RETURN")
    rails=(("+","CONSTRUCTIVE"),("HINGE","COMPATIBILITY"),("*","ADVERSARIAL_RETURN"))
    out=[]; gid=23
    for stage in stages:
        for symbol,rail in rails:
            out.append(InnerSeat(gid,"BR21",f"{stage}.{symbol}",f"{stage}_{rail}",coordinate=f"{stage}/{symbol}")); gid+=1
    return out


def _f37() -> list[InnerSeat]:
    roles=[
        "DIAGONAL_LATIN_SQUARE_ADDRESS_RECURSIVE_COORDINATE","COMPACTIFIED_COMPLEX_HILBERT_STATE","RIGGED_DISTRIBUTION_INSTRUMENT","ORBIT_CHARACTER","EXACT_AFFINE_MOTION","BINARY_OCTAHEDRAL_QUATERNION_LIFT","ANALYTIC_BRANCH_COVER","JET_LOCAL_ASYMPTOTIC","BULK_BOUNDARY_TOTALIZED_CHANNEL","OBSERVABLE_ALGEBRA","COMMUTANT_SECTOR","ELLIPTIC_TWO_TORSION","ROOT_LATTICE","BINARY_CODE_PAULI","CLIFFORD_SPIN","FINITE_INCIDENCE_GEOMETRY","QUANTUM_GROUP_DEFORMATION","TWISTED_K_COHOMOLOGICAL_COMPLETION","PHYSICAL_GEOMETRIC_SEATING","G2_REDUCED_TRANSPORT_GEOMETRY","OCTONIONIC_EXCEPTIONAL_ALGEBRA","KUMMER_K3_COMPACTIFIED_BRIDGE","VISIBLE_DISCRETE_PHYSICAL_SYMMETRY_COMPRESSION","SYMMETRY_PROTECTED_PHASE_RG_SHADOW","TORIC_CODE_REALIZATION","KITAEV_HONEYCOMB_NONABELIAN_LIFT","DIJKGRAAF_WITTEN_FINITE_GAUGE","QUESTION_LANGUAGE_CODIFICATION","MODULAR_VISIBILITY","MOONSHINE_GRADED_MEMORY","E7_LATTICE_VOA_CROSS_SYMMETRY","GLOBAL_CONFORMAL_BODY_OBLIGATION","SUBFACTOR_FUSION_INDEX_MERKLE_REPLAY","MOTIVIC_ENVELOPE","HIGHER_COHERENCE_ARCHITECTURE","DERIVED_SINGULARITY_EMPIRICAL_CLOSURE_REPLAY_MEMORY","INTEGRABLE_AQM_DYNAMICAL_CAPSTONE_RETURN"]
    obligations={30:("GRADED_MEMORY_PARTIAL_EXACTIFICATION",),34:("MOTIVIC_COMPARISON_DEBT",),35:("HIGHER_COHERENCE_COMPOSITION_WITNESS",),36:("DERIVED_SINGULARITY_AND_EMPIRICAL_CLOSURE",)}
    return [InnerSeat(44+i,"F37",f"F{i+1:02d}",role,known_obligations=obligations.get(i+1,())) for i,role in enumerate(roles)]


def _ic10() -> list[InnerSeat]:
    roles=["IDENTITY_PROVENANCE","SYNTAX_NORMALIZATION_DEPENDENCIES","TYPE_UNIT_CARRIER","SCOPE_CORRIDOR_EVIDENCE_ALIGNMENT","INVARIANT_PRESERVATION","EVIDENCE_SUFFICIENCY_INDEPENDENCE","DEPENDENCY_CLOSURE_REPLAY_PREREQUISITES","BRIDGE_GLUING_RETURN_DEFECT","AUDIT_REPLAY_COMPLETENESS","PROMOTION_CANONICAL_EMISSION_RESEED"]
    return [InnerSeat(81+i,"IC10",f"I{i+1:02d}",role) for i,role in enumerate(roles)]


def _kc15() -> list[InnerSeat]:
    masks=[("1000","{11}"),("0100","{10}"),("1100","{11,10}"),("0010","{00}"),("1010","{11,00}"),("0110","{10,00}"),("1110","{11,10,00}"),("0001","{01}"),("1001","{11,01}"),("0101","{10,01}"),("1101","{11,10,01}"),("0011","{00,01}"),("1011","{11,00,01}"),("0111","{10,00,01}"),("1111","{11,10,00,01}")]
    return [InnerSeat(91+i,"KC15",mask,"FOUR_POLE_SUPPORT_MASK",coordinate=poles) for i,(mask,poles) in enumerate(masks)]


def _kc27() -> list[InnerSeat]:
    anchors={8:"DIFFERENTIAL_COHOMOLOGICAL_BOUNDARY_CALCULUS",9:"ADDRESSING_RANDOM_ACCESS_SEED_RETRIEVAL",10:"BR21_PEER_RUNTIME",11:"IC10_COMPILER_INDEX",12:"BRANCH_COMPLETE_CUT_NAVIGATION",13:"CODEC_COMPRESSION_QSHRINK",14:"MEMORY_MERKLE_CONTENT_ADDRESSING"}
    out=[]
    for p in range(27):
        a,rem=divmod(p,9); b,c=divmod(rem,3); coord=f"{a}{b}{c}"
        out.append(InnerSeat(106+p,"KC27",f"P{p:02d}",anchors.get(p,"UNRESOLVED_DOMAIN_ROLE"),coordinate=coord))
    return out


def _ssn12() -> list[InnerSeat]:
    roles=["NODE_STATE_MATURITY_REGISTRY","EDGE_BRIDGE_ROUTE_REGISTRY","EPOCH_ALIAS_CROSSWALK_REGISTRY","LIMINAL_DISAGREEMENT_JSPACE_REGISTRY","ACTIVATION_OBSERVER_COVERAGE_MAP","BRANCH_TOMBSTONE_QUARANTINE_REJECTED_ROUTE_STORE","DEFECT_EVIDENCE_DEBT_REPAIR_SCHEDULER","HEALING_ROUTE_UNRESOLVED_BRIDGE_RESOLVER","PATH_SIGNATURE_TRAVERSAL_LEDGER","REPLAY_REPLICA_COLD_BOOT_OBSERVATORY","MERGE_DEPLOYMENT_AUTHORITY_RELEASE_RECEIPT","SUCCESSOR_CERTIFICATE_GLOBAL_SEED_REENTRY"]
    return [InnerSeat(133+i,"SSN12",f"M{i+1:02d}",role) for i,role in enumerate(roles)]


def seats() -> list[dict]:
    values=_h6()+_x16()+_br21()+_f37()+_ic10()+_kc15()+_kc27()+_ssn12()
    if len(values)!=144 or [s.gid for s in values]!=list(range(1,145)):
        raise RuntimeError("invalid KC144 inner constitution")
    return [s.as_dict() for s in values]


def seat(gid:int)->dict:
    if not 1<=int(gid)<=144: raise ValueError("gid must be 1..144")
    return seats()[int(gid)-1]


def block_counts()->dict[str,int]:
    out={}
    for item in seats(): out[item["block"]]=out.get(item["block"],0)+1
    return out
