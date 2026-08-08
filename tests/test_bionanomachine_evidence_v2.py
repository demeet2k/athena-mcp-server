from athena_mcp.bionanomachine_evidence import (
    ADAPTERS,EVIDENCE_VERSION,QUANTITATIVE_CLAIMS,ROW_FACETS,SOURCES,UNPROMOTED_USER_NUMERIC_CLAIMS
)
from athena_mcp.bionanomachine_evidence_runtime import EvidenceBionanomachineRuntime


def test_v2_preserves_14_seed_ids_and_adds_only_six_bounded_expansions():
    r=EvidenceBionanomachineRuntime();c=r.catalog()
    assert c['evidence_version']==EVIDENCE_VERSION
    assert c['source_backed_adapter_count']==20
    assert c['original_seed_count']==14
    assert c['evidence_expansion_count']==6
    assert len(c['seed_machines'])==14
    assert len(c['expansion_machines'])==6
    assert len(ADAPTERS)==20
    assert len(SOURCES)==20


def test_all_twenty_adapters_compile_with_primary_source_and_row_identity():
    r=EvidenceBionanomachineRuntime()
    for machine_id,adapter in ADAPTERS.items():
        p=r.compile(machine_id)
        assert p['status']=='COMPILED_SOURCE_BACKED_MODEL'
        assert p['adapter_id']==adapter['adapter_id']
        assert p['row_associations']==adapter['rows']
        assert p['primary_source']['source_class']=='PRIMARY_RESEARCH'
        assert p['primary_source']['doi']
        assert len(p['kernel12'])==12
        assert set(p['lift4'])=={'structure','drive','work','integrity'}
        assert p['numeric_policy']=='PRIMARY_CONDITIONED_ONLY; USER_SEED_NUMBERS_UNPROMOTED'
        assert p['authority']=='PRIMARY_SOURCE_CONDITIONED_MECHANISM_MODEL_NOT_CANONICAL_BIOLOGICAL_TRUTH'


def test_quantitative_claim_membrane_is_conditioned_and_never_universal():
    assert len(QUANTITATIVE_CLAIMS)==15
    for claim in QUANTITATIVE_CLAIMS:
        assert claim['source_id'] in SOURCES
        assert claim['standing']=='PRIMARY_CONDITIONED'
        assert claim['universal_constant'] is False
        assert claim['conditions']
        assert claim['unit']


def test_user_seed_rpm_and_polymerase_rate_remain_explicitly_unpromoted():
    assert len(UNPROMOTED_USER_NUMERIC_CLAIMS)==3
    by_machine={x['machine_id']:x for x in UNPROMOTED_USER_NUMERIC_CLAIMS}
    assert by_machine['ATP_SYNTHASE']['claim']=='up to 9000 RPM'
    assert by_machine['BACTERIAL_FLAGELLAR_MOTOR']['claim']=='up to 100000 RPM'
    assert by_machine['DNA_POLYMERASE']['claim']=='up to 1000 bases/s'
    assert all(x['status']=='UNVERIFIED_USER_SEED' for x in UNPROMOTED_USER_NUMERIC_CLAIMS)


def test_populated_evidence_atlas_is_exact_144_and_every_cell_has_content():
    r=EvidenceBionanomachineRuntime();c=r.catalog(include_atlas=True)
    atlas=c['atlas']
    assert len(ROW_FACETS)==12
    assert all(len(profile)==12 for profile in ROW_FACETS.values())
    assert len(atlas)==144
    assert {cell['gid'] for cell in atlas}==set(range(1,145))
    assert all(cell['value'].strip() for cell in atlas)
    assert all(cell['source_ids'] for cell in atlas)
    assert all(cell['adapter_ids'] for cell in atlas)


def test_multirow_association_projects_one_identity_without_duplication():
    r=EvidenceBionanomachineRuntime()
    p=r.compile('FTSK_TRANSLOCASE')
    assert p['row_associations']==[3,7]
    assert p['machine_id']=='FTSK_TRANSLOCASE'
    assert len(p['kc144']['associated_rows'])==2
    assert p['kc144']['semantic_identity_law']=='MULTI_ROW_ASSOCIATION != DUPLICATED_OBJECT'


def test_primary_source_support_never_upgrades_transfer_authority():
    r=EvidenceBionanomachineRuntime()
    p=r.transfer('ATP_SYNTHASE','convert developmental pressure into executable work')
    assert p['source_backed_mechanism'] is True
    assert p['authority']=='COMPUTATIONAL_ANALOGY_ONLY'
    assert 'PRIMARY_SOURCE_SUPPORT != EXECUTION_AUTHORITY' in p['law']


def test_original_phage_packet_preserves_visual_bom_separately_from_primary_transition():
    r=EvidenceBionanomachineRuntime();p=r.assembly('BACTERIOPHAGE_TAIL_ASSEMBLY')
    assert p['status']=='DUAL_PROVENANCE_ASSEMBLY_PACKET'
    assert p['component_count']==15
    assert len(p['components'])==15
    assert p['visual_functional_sequence']==['attachment','penetration/sheath contraction','payload injection','spent/empty external particle']
    assert p['primary_supported_transition_sequence']==ADAPTERS['BACTERIOPHAGE_TAIL_ASSEMBLY']['cycle']
    assert p['visual_provenance']=='USER_VISUAL_SEED'
    assert 'USER_VISUAL_BOM != PRIMARY_VERIFIED_NATIVE_SUBUNIT_INVENTORY' in p['law']


def test_generic_assembly_for_original_and_expansion_remains_not_native_bom():
    r=EvidenceBionanomachineRuntime()
    original=r.assembly('RIBOSOME')
    assert original['status']=='GENERIC_MECHANISM_ASSEMBLY_ABSTRACTION'
    assert original['authority']=='GENERIC_FUNCTIONAL_ASSEMBLY_PLUS_PRIMARY_CONDITIONED_MECHANISM; NOT_NATIVE_BOM'
    assert original['mechanism_source']['source_id']=='S06'
    expanded=r.assembly('SPLICEOSOME')
    assert expanded['status']=='SOURCE_BACKED_GENERIC_ASSEMBLY_ABSTRACTION'
    assert expanded['mechanism_source']['source_id']=='S16'
    assert 'ASSEMBLY_GRAPH != FUNCTION_GRAPH' in expanded['law']


def test_v1_interface_and_convergence_semantics_are_unchanged_in_v2():
    r=EvidenceBionanomachineRuntime()
    x={'rate':0.5,'latency':0.5,'error_tolerance':0.5,'statefulness':0.5,'reversibility':0.5,'coupling':0.5}
    assert r.interface_match(x,x)['match']==1.0
    assert r.interface_match(x,x)['authority']=='COMPUTATIONAL_COMPATIBILITY_PROXY'
    assert r.convergence_gate(ratio_limit=1.0)['status']=='HOLD_INCONCLUSIVE'
    assert r.convergence_gate(contraction_q=0.9)['status']=='PASS_WITNESS_SCOPED'


def test_v2_benchmark_proves_populated_atlas_and_evidence_counts():
    b=EvidenceBionanomachineRuntime().benchmark()
    assert b['bionano_source_backed_adapters']==20
    assert b['bionano_primary_sources']==20
    assert b['bionano_conditioned_quantitative_claims']==15
    assert b['bionano_evidence_expansion_machines']==6
    assert b['bionano_populated_kc144_cells']==144
    assert b['bionano_populated_kc144_nonempty'] is True
    assert b['bionano_populated_gid_unique'] is True
    assert b['bionano_unpromoted_user_numeric_claims']==3
