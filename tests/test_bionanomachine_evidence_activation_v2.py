from athena_mcp.bionanomachine_protocol import BIONANO_RESOURCE,BIONANO_TOOL_NAMES
from athena_mcp.bionanomachine_surface import (
    BionanomachineSurface,
    BIONANOMACHINE_RESOURCE_URIS,
    BIONANOMACHINE_TOOL_NAMES,
)
from athena_mcp.mythic_computation_protocol import MCK_RESOURCE,MCK_TOOL_NAMES


def test_public_catalog_preserves_stable_seed_view_and_adds_opt_in_evidence():
    s=BionanomachineSurface()
    handled,base=s.call_tool('athena_bionano_catalog',{'include_atlas':False})
    assert handled
    assert base['version']=='BNMK.V1'
    assert base['evidence_version']=='BNMK.ADAPTER20.V2'
    assert len(base['seed_machines'])==14
    assert base['source_backed_adapter_count']==20
    assert base['primary_source_count']==20
    assert base['conditioned_quantitative_claim_count']==15
    assert 'source_backed_machines' not in base

    handled,evidence=s.call_tool('athena_bionano_catalog',{'include_atlas':True,'include_evidence':True})
    assert handled
    assert len(evidence['seed_machines'])==14
    assert len(evidence['source_backed_machines'])==20
    assert len(evidence['atlas'])==144
    assert {cell['gid'] for cell in evidence['atlas']}==set(range(1,145))
    assert all(cell['value'].strip() for cell in evidence['atlas'])
    assert len(evidence['unpromoted_user_numeric_claims'])==3


def test_public_compile_supports_original_and_expansion_with_primary_source():
    s=BionanomachineSurface()
    for machine_id in ('ATP_SYNTHASE','SPLICEOSOME','FTSK_TRANSLOCASE'):
        handled,p=s.call_tool('athena_bionano_compile',{'machine_id':machine_id})
        assert handled
        assert p['status']=='COMPILED_SOURCE_BACKED_MODEL'
        assert p['primary_source']['source_class']=='PRIMARY_RESEARCH'
        assert p['primary_source']['doi']
        assert p['authority']=='PRIMARY_SOURCE_CONDITIONED_MECHANISM_MODEL_NOT_CANONICAL_BIOLOGICAL_TRUTH'


def test_public_transfer_never_inherits_execution_authority_from_primary_source():
    s=BionanomachineSurface()
    handled,p=s.call_tool('athena_bionano_transfer',{
        'machine_id':'CONDENSIN',
        'target':'resolve a graph collision through topology-aware traversal',
    })
    assert handled
    assert p['source_backed_mechanism'] is True
    assert p['authority']=='COMPUTATIONAL_ANALOGY_ONLY'
    assert 'PRIMARY_SOURCE_SUPPORT != EXECUTION_AUTHORITY' in p['law']


def test_public_t4_assembly_keeps_visual_and_primary_mechanism_provenance_separate():
    s=BionanomachineSurface()
    handled,p=s.call_tool('athena_bionano_assembly',{'machine_id':'BACTERIOPHAGE_TAIL_ASSEMBLY'})
    assert handled
    assert p['status']=='DUAL_PROVENANCE_ASSEMBLY_PACKET'
    assert p['component_count']==15
    assert p['visual_provenance']=='USER_VISUAL_SEED'
    assert p['mechanism_source']['source_class']=='PRIMARY_RESEARCH'
    assert 'ASSEMBLY_GRAPH != FUNCTION_GRAPH' in p['law']


def test_public_interface_match_and_convergence_keep_v1_semantics():
    s=BionanomachineSurface()
    profile={'rate':0.5,'latency':0.5,'error_tolerance':0.5,'statefulness':0.5,'reversibility':0.5,'coupling':0.5}
    handled,match=s.call_tool('athena_bionano_interface_match',{'producer':profile,'consumer':profile})
    assert handled and match['match']==1.0
    assert match['authority']=='COMPUTATIONAL_COMPATIBILITY_PROXY'
    handled,ratio=s.call_tool('athena_bionano_convergence_gate',{'ratio_limit':1.0})
    assert handled and ratio['status']=='HOLD_INCONCLUSIVE'
    handled,contract=s.call_tool('athena_bionano_convergence_gate',{'contraction_q':0.9})
    assert handled and contract['status']=='PASS_WITNESS_SCOPED'


def test_mck_tools_and_resource_survive_bionano_activation_seam():
    s=BionanomachineSurface()
    assert MCK_TOOL_NAMES <= BIONANOMACHINE_TOOL_NAMES
    assert BIONANO_TOOL_NAMES <= BIONANOMACHINE_TOOL_NAMES
    assert MCK_RESOURCE['uri'] in BIONANOMACHINE_RESOURCE_URIS
    assert BIONANO_RESOURCE['uri'] in BIONANOMACHINE_RESOURCE_URIS

    handled,p=s.call_tool('athena_mck_symbolic_address',{
        'query':'mars',
        'address_space':[{'id':'mars','terms':['mars'],'standing':'SOURCE_REPORTED','source_ref':'fixture'}],
    })
    assert handled
    assert p['status']=='ADDRESS_SELECTED'
    assert p['authority']=='SYMBOLIC_ADDRESS_SELECTION_ONLY'
    resource=s.read_resource(MCK_RESOURCE['uri'])
    assert resource['version']=='MCK.RUNTIME.V1'


def test_bnm_resource_reports_active_evidence_version_and_counts():
    s=BionanomachineSurface()
    resource=s.read_resource(BIONANO_RESOURCE['uri'])
    assert resource['version']=='BNMK.V1'
    assert resource['evidence_version']=='BNMK.ADAPTER20.V2'
    assert resource['benchmark']['bionano_source_backed_adapters']==20
    assert resource['benchmark']['bionano_populated_kc144_cells']==144
    assert resource['authority']=='PRIMARY_SOURCE_CONDITIONED_MECHANISM_LIBRARY; COMPUTATIONAL_TRANSFER_REMAINS_ANALOGY_ONLY'


def test_extension_union_has_no_duplicate_tool_names():
    # Set semantics alone would hide duplicate declarations; compare declared list length to unique names.
    from athena_mcp.bionanomachine_surface import BIONANOMACHINE_TOOLS
    names=[tool['name'] for tool in BIONANOMACHINE_TOOLS]
    assert len(names)==len(set(names))
