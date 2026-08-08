from __future__ import annotations

from typing import Any,Dict,List

from .bionanomachine_runtime import BionanomachineRuntime,ARCHETYPES,COLUMNS,FACET_PURPOSE,SEEDS,PHAGE_ASSEMBLY_EDGES,_lift4
from .bionanomachine_protocol import BIONANO_VERSION
from .bionanomachine_evidence import (
    ADAPTERS,EVIDENCE_LAWS,EVIDENCE_VERSION,OPERATOR_PHYLOGENY,QUANTITATIVE_CLAIMS,
    ROW_FACETS,SECOND_ORDER_OPERATORS,SOURCES,UNPROMOTED_USER_NUMERIC_CLAIMS,
)


def _source_packet(source_id:str)->Dict[str,Any]:
    src=dict(SOURCES[source_id])
    src['source_id']=source_id
    src['source_class']='PRIMARY_RESEARCH'
    return src


def _claims(machine_id:str)->List[Dict[str,Any]]:
    return [dict(c) for c in QUANTITATIVE_CLAIMS if c['machine_id']==machine_id]


def _evidence_kernel(machine_id:str,row:int)->Dict[str,Any]:
    adapter=ADAPTERS[machine_id];source_id=adapter['source_id'];profile=ROW_FACETS[row]
    result={}
    for facet in COLUMNS:
        result[facet]={
            'terms':[facet],
            'roles':[FACET_PURPOSE[facet]],
            'claims':[{
                'text':profile[facet],
                'status':'PRIMARY_SUPPORTED_MECHANISM_SYNTHESIS',
                'source_ids':[source_id],
            }],
            'loss':[
                'Row-level mechanism synthesis is conditioned on the cited primary-source adapter and does not replace source-specific molecular detail.',
                'Computational transfer is a separate analogy plane and gains no biological or execution authority from source support.',
            ],
        }
    return result


def _evidence_cells(row:int)->List[Dict[str,Any]]:
    profile=ROW_FACETS[row]
    adapter_ids=sorted(a['adapter_id'] for a in ADAPTERS.values() if row in a['rows'])
    source_ids=sorted({a['source_id'] for a in ADAPTERS.values() if row in a['rows']})
    return [
        {
            'row':row,'column':column,'gid':12*(row-1)+column,'facet':facet,
            'role':f"{ARCHETYPES[row]['label']} :: {FACET_PURPOSE[facet]}",
            'value':profile[facet],
            'adapter_ids':adapter_ids,'source_ids':source_ids,
            'status':'SOURCE_BACKED_POPULATED_FACET',
        }
        for column,facet in enumerate(COLUMNS,1)
    ]


def _generic_assembly(machine_id:str,adapter:Dict[str,Any],status:str,authority:str)->Dict[str,Any]:
    return {
        'version':BIONANO_VERSION,'evidence_version':EVIDENCE_VERSION,'status':status,
        'machine_id':machine_id,
        'components':['input_interface','energy_coupling_module','work_core','quality_gate','output_interface'],
        'dependency_edges':[
            {'src':'input_interface','relation':'feeds','dst':'work_core'},
            {'src':'energy_coupling_module','relation':'drives','dst':'work_core'},
            {'src':'work_core','relation':'checked_by','dst':'quality_gate'},
            {'src':'quality_gate','relation':'releases_to','dst':'output_interface'},
        ],
        'functional_sequence':list(adapter['cycle']),'mechanism_source':_source_packet(adapter['source_id']),
        'authority':authority,
        'law':'ASSEMBLY_GRAPH != FUNCTION_GRAPH; GENERIC_FUNCTIONAL_MODULES != NATIVE_PROTEIN_SUBUNIT_INVENTORY',
    }


class EvidenceBionanomachineRuntime(BionanomachineRuntime):
    """BNMK V2 evidence join while preserving the V1 MCP ABI and authority ceiling."""

    def catalog(self,include_atlas:bool=False,include_evidence:bool=False)->Dict[str,Any]:
        result=super().catalog(False)
        expansions=[
            {
                'machine_id':mid,'native_name':a['name'],'row_associations':list(a['rows']),
                'primary_source_id':a['source_id'],'source_backed':True,'scope':'EVIDENCE_BACKED_EXPANSION'
            }
            for mid,a in ADAPTERS.items() if not a['original_seed']
        ]
        result.update({
            'evidence_version':EVIDENCE_VERSION,
            'status':'SOURCE_BACKED_OPERATOR_LIBRARY',
            'source_backed_adapter_count':len(ADAPTERS),
            'primary_source_count':len(SOURCES),
            'conditioned_quantitative_claim_count':len(QUANTITATIVE_CLAIMS),
            'original_seed_count':sum(1 for a in ADAPTERS.values() if a['original_seed']),
            'evidence_expansion_count':sum(1 for a in ADAPTERS.values() if not a['original_seed']),
            'expansion_machines':expansions,
            'operator_phylogeny':{k:list(v) for k,v in OPERATOR_PHYLOGENY.items()},
            'second_order_operators':list(SECOND_ORDER_OPERATORS),
            'authority':'PRIMARY_SOURCE_CONDITIONED_MECHANISM_LIBRARY; COMPUTATIONAL_TRANSFER_REMAINS_ANALOGY_ONLY',
            'epistemic_laws':list(dict.fromkeys(result.get('epistemic_laws',[])+EVIDENCE_LAWS)),
        })
        if include_atlas:
            result['atlas']=[cell for row in range(1,13) for cell in _evidence_cells(row)]
        if include_evidence:
            result['source_backed_machines']=[
                {
                    'machine_id':mid,'adapter_id':a['adapter_id'],'native_name':a['name'],
                    'row_associations':list(a['rows']),'primary_source':_source_packet(a['source_id']),
                    'quantitative_claims':_claims(mid),'original_seed':a['original_seed'],
                }
                for mid,a in ADAPTERS.items()
            ]
            result['unpromoted_user_numeric_claims']=[dict(x) for x in UNPROMOTED_USER_NUMERIC_CLAIMS]
        return result

    def compile(self,machine_id:str)->Dict[str,Any]:
        mid=str(machine_id).strip().upper()
        adapter=ADAPTERS.get(mid)
        if adapter is None:
            return {
                'version':BIONANO_VERSION,'evidence_version':EVIDENCE_VERSION,'status':'HOLD_UNKNOWN_MACHINE',
                'machine_id':mid,'known_machine_ids':sorted(ADAPTERS),
                'law':'UNKNOWN_MACHINE != FABRICATED_CLASSIFICATION',
            }
        rows=list(adapter['rows']);primary_row=rows[0];kernel=_evidence_kernel(mid,primary_row)
        row_packets=[{'row':row,'row_id':f'R{row:02d}','cells':_evidence_cells(row)} for row in rows]
        return {
            'version':BIONANO_VERSION,'evidence_version':EVIDENCE_VERSION,'status':'COMPILED_SOURCE_BACKED_MODEL',
            'machine_id':mid,'native_name':adapter['name'],'adapter_id':adapter['adapter_id'],
            'archetype':ARCHETYPES[primary_row]['id'],'row':primary_row,'row_id':f'R{primary_row:02d}',
            'row_associations':rows,
            'evidence_mode':['PRIMARY_RESEARCH','MECHANISTIC_MODEL'],
            'primary_source':_source_packet(adapter['source_id']),
            'quantitative_claims':_claims(mid),
            'lift4':_lift4(kernel),'kernel12':kernel,
            'kc144':{
                'row':primary_row,'row_id':f'R{primary_row:02d}','cells':row_packets[0]['cells'],
                'associated_rows':row_packets,
                'semantic_identity_law':'MULTI_ROW_ASSOCIATION != DUPLICATED_OBJECT',
            },
            'state_machine':{'states':list(adapter['cycle']),'reset_or_terminal':adapter['cycle'][-1]},
            'mechanism_role':adapter['role'],'portable_operators':list(adapter['portable']),
            'athena_targets':list(adapter['athena']),
            'numeric_policy':'PRIMARY_CONDITIONED_ONLY; USER_SEED_NUMBERS_UNPROMOTED',
            'authority':'PRIMARY_SOURCE_CONDITIONED_MECHANISM_MODEL_NOT_CANONICAL_BIOLOGICAL_TRUTH',
            'laws':list(EVIDENCE_LAWS),
        }

    def transfer(self,machine_id:str,target:str,constraints=None)->Dict[str,Any]:
        compiled=self.compile(machine_id)
        if compiled.get('status')!='COMPILED_SOURCE_BACKED_MODEL':return compiled
        return {
            'version':BIONANO_VERSION,'evidence_version':EVIDENCE_VERSION,'status':'ANALOGY_CANDIDATE',
            'machine_id':compiled['machine_id'],'adapter_id':compiled['adapter_id'],'target':str(target),
            'source_backed_mechanism':True,
            'portable_operators':compiled['portable_operators'],'suggested_athena_targets':compiled['athena_targets'],
            'constraints':list(constraints or []),
            'nonportable_context':['molecular composition','organism/species context','assay conditions','biochemical quantitative constants','evolutionary history'],
            'transfer_loss':['Primary support improves the biological mechanism model but does not establish software equivalence, execution authority, or causal transfer.'],
            'authority':'COMPUTATIONAL_ANALOGY_ONLY',
            'law':'PRIMARY_SOURCE_SUPPORT != EXECUTION_AUTHORITY; ANALOGY_TO != IS_SAME_AS; TRANSFER_OPERATOR != BIOLOGICAL_CLAIM',
        }

    def assembly(self,machine_id:str)->Dict[str,Any]:
        mid=str(machine_id).strip().upper();adapter=ADAPTERS.get(mid)
        if adapter is None:return self.compile(mid)
        if mid=='BACTERIOPHAGE_TAIL_ASSEMBLY':
            seed=SEEDS[mid]
            return {
                'version':BIONANO_VERSION,'evidence_version':EVIDENCE_VERSION,'status':'DUAL_PROVENANCE_ASSEMBLY_PACKET',
                'machine_id':mid,
                'components':list(seed['visual_components']),'dependency_edges':list(PHAGE_ASSEMBLY_EDGES),
                'visual_functional_sequence':list(seed['visual_sequence']),
                'primary_supported_transition_sequence':list(adapter['cycle']),
                'component_count':len(seed['visual_components']),
                'visual_provenance':'USER_VISUAL_SEED','mechanism_source':_source_packet(adapter['source_id']),
                'authority':'VISUAL_COMPONENT_LABELS_USER_SEED; TRANSITION_MECHANISM_PRIMARY_CONDITIONED',
                'law':'USER_VISUAL_BOM != PRIMARY_VERIFIED_NATIVE_SUBUNIT_INVENTORY; ASSEMBLY_GRAPH != FUNCTION_GRAPH; ASSEMBLY != EXECUTION',
            }
        if mid in SEEDS:
            return _generic_assembly(
                mid,adapter,'GENERIC_MECHANISM_ASSEMBLY_ABSTRACTION',
                'GENERIC_FUNCTIONAL_ASSEMBLY_PLUS_PRIMARY_CONDITIONED_MECHANISM; NOT_NATIVE_BOM'
            )
        return _generic_assembly(
            mid,adapter,'SOURCE_BACKED_GENERIC_ASSEMBLY_ABSTRACTION',
            'PRIMARY_CONDITIONED_FUNCTION_SEQUENCE; GENERIC_FUNCTIONAL_MODULES_NOT_NATIVE_BOM'
        )

    def benchmark(self)->Dict[str,Any]:
        base=super().benchmark();atlas=[cell for row in range(1,13) for cell in _evidence_cells(row)]
        base.update({
            'bionano_source_backed_adapters':len(ADAPTERS),
            'bionano_primary_sources':len(SOURCES),
            'bionano_conditioned_quantitative_claims':len(QUANTITATIVE_CLAIMS),
            'bionano_evidence_expansion_machines':sum(1 for a in ADAPTERS.values() if not a['original_seed']),
            'bionano_populated_kc144_cells':len(atlas),
            'bionano_populated_kc144_nonempty':all(bool(c['value'].strip()) for c in atlas),
            'bionano_populated_gid_unique':len({c['gid'] for c in atlas})==144,
            'bionano_unpromoted_user_numeric_claims':len(UNPROMOTED_USER_NUMERIC_CLAIMS),
        })
        return base
