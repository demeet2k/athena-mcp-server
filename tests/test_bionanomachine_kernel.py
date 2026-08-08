from athena_mcp.bionanomachine_protocol import BIONANO_RESOURCE,BIONANO_TOOL_NAMES
from athena_mcp.bionanomachine_runtime import BionanomachineRuntime
from athena_mcp.bionanomachine_surface import BionanomachineSurface
from athena_mcp.aor_development_surface import AOR_DEVELOPMENT_TOOL_NAMES,AOR_DEVELOPMENT_RESOURCES


def test_catalog_is_native_kc144_and_preserves_all_seed_machines():
    r=BionanomachineRuntime()
    c=r.catalog(include_atlas=True)
    assert len(c['rows'])==12
    assert len(c['columns'])==12
    assert len(c['seed_machines'])==14
    assert len(c['atlas'])==144
    assert {cell['gid'] for cell in c['atlas']}==set(range(1,145))
    assert c['kc144']['gid_law']=='gid=12*(row-1)+column'
    assert 'USER_SEED != VERIFIED_EMPIRICAL_CONSTANT' in c['epistemic_laws']


def test_every_known_machine_compiles_to_4d_12d_and_one_kc144_row():
    r=BionanomachineRuntime()
    for item in r.catalog()['seed_machines']:
        packet=r.compile(item['machine_id'])
        assert packet['status']=='COMPILED_MODEL'
        assert set(packet['lift4'])=={'structure','drive','work','integrity'}
        assert len(packet['kernel12'])==12
        assert len(packet['kc144']['cells'])==12
        assert packet['numeric_seed_policy']=='UNVERIFIED_USER_NUMBERS_NOT_CANONICAL'


def test_unknown_machine_holds_instead_of_guessing():
    p=BionanomachineRuntime().compile('imaginary_motor')
    assert p['status']=='HOLD_UNKNOWN_MACHINE'
    assert p['law']=='UNKNOWN_MACHINE != FABRICATED_CLASSIFICATION'


def test_transfer_is_explicit_analogy_not_equivalence():
    p=BionanomachineRuntime().transfer('TOPOISOMERASE','resolve a divergent Git/JSPACE branch')
    assert p['status']=='ANALOGY_CANDIDATE'
    assert p['authority']=='COMPUTATIONAL_ANALOGY_ONLY'
    assert 'ANALOGY_TO != IS_SAME_AS' in p['law']
    assert 'temporary_cut' in p['portable_operators']


def test_interface_match_is_bounded_and_exact_identity_matches():
    r=BionanomachineRuntime()
    x={'rate':0.7,'latency':0.2,'error_tolerance':0.9,'statefulness':0.8,'reversibility':0.4,'coupling':0.6}
    same=r.interface_match(x,x)
    assert same['match']==1.0
    assert same['status']=='MATCHED'
    y={k:1.0-v for k,v in x.items()}
    diff=r.interface_match(x,y)
    assert 0.0<=diff['match']<=1.0
    assert diff['authority']=='COMPUTATIONAL_COMPATIBILITY_PROXY'


def test_convergence_gate_preserves_scope_and_inconclusive_boundaries():
    r=BionanomachineRuntime()
    assert r.convergence_gate(nth_term_limit=0.2)['status']=='FAIL_WITNESS'
    assert r.convergence_gate(ratio_limit=0.5)['status']=='PASS_WITNESS_SCOPED'
    assert r.convergence_gate(ratio_limit=1.0)['status']=='HOLD_INCONCLUSIVE'
    assert r.convergence_gate(contraction_q=0.8)['status']=='PASS_WITNESS_SCOPED'
    assert r.convergence_gate(contraction_q=1.0)['status']=='HOLD_INCONCLUSIVE'
    assert r.convergence_gate(spectral_radius=1.2)['status']=='FAIL_WITNESS'
    assert r.convergence_gate()['status']=='HOLD_NO_WITNESS'


def test_phage_visual_seed_preserves_exploded_bom_and_sequence_without_overclaim():
    p=BionanomachineRuntime().assembly('BACTERIOPHAGE_TAIL_ASSEMBLY')
    assert p['status']=='USER_VISUAL_ASSEMBLY_PACKET'
    assert p['component_count']==15
    assert len(p['components'])==15
    assert p['functional_sequence']==['attachment','penetration/sheath contraction','payload injection','spent/empty external particle']
    assert p['authority']=='STRUCTURAL_VISUAL_SEED_NOT_INDEPENDENT_BIOLOGICAL_VERIFICATION'


def test_generic_assembly_does_not_fabricate_native_subunits():
    p=BionanomachineRuntime().assembly('RIBOSOME')
    assert p['status']=='GENERIC_MECHANISM_ASSEMBLY_ABSTRACTION'
    assert p['authority']=='NOT_A_SOURCE_SPECIFIC_MOLECULAR_BOM'


def test_surface_dispatches_all_six_tools_and_resource():
    s=BionanomachineSurface()
    for name in BIONANO_TOOL_NAMES:
        assert name in AOR_DEVELOPMENT_TOOL_NAMES
    assert BIONANO_RESOURCE in AOR_DEVELOPMENT_RESOURCES
    handled,value=s.call_tool('athena_bionano_catalog',{'include_atlas':False})
    assert handled and value['version']=='BNMK.1'
    resource=s.read_resource(BIONANO_RESOURCE['uri'])
    assert resource['benchmark']['bionano_kc144_cells']==144
    assert resource['benchmark']['bionano_phage_visual_components']==15
