from __future__ import annotations

import math
from typing import Any,Dict,List

from .bionanomachine_protocol import BIONANO_VERSION

COLUMNS=[
    'identity_role','energy_drive','input_cargo','output_work','substrate_track','geometry_topology',
    'state_cycle','coupling_gating','fidelity_error_control','assembly_maintenance','failure_recovery','interface_transfer'
]

EPISTEMIC_LAWS=[
    'BIOLOGICAL_MECHANISM != SOFTWARE_IMPLEMENTATION',
    'MECHANISTIC_ANALOGY != CAUSAL_EQUIVALENCE',
    'USER_SEED != VERIFIED_EMPIRICAL_CONSTANT',
    'STRUCTURAL_SIMILARITY != SHARED_EVOLUTIONARY_ORIGIN',
    'SIMULATION != OBSERVATION',
    'TRANSFER_OPERATOR != BIOLOGICAL_CLAIM',
    'GRAPH_TOPOLOGY != FUNCTIONAL_IDENTITY',
    'INTERFACE_MATCH_PROXY != PHYSICAL_IMPEDANCE',
]

ARCHETYPES={
    1:{'id':'ROTARY_GRADIENT_TRANSDUCER','label':'rotary gradient transducer','examples':['ATP_SYNTHASE'],'mechanism':'potential gradient -> selective flow -> rotor/conformation cycle -> coupled work','portable':['gradient_to_work','reversible_transduction','rotor_stator_coupling','phase_locked_substeps'],'athena':['pressure_to_execution adapter','gradient-driven scheduling','coupled phase control'],'cycle':['IDLE','DRIVEN','ROTATING','COUPLED_WORK','RELEASE','IDLE']},
    2:{'id':'ROTARY_PROPULSION_MOTOR','label':'rotary propulsion motor','examples':['BACTERIAL_FLAGELLAR_MOTOR'],'mechanism':'distributed drive units -> rotor -> shaft/joint -> external propulsion','portable':['distributed_drive','rapid_direction_switch','shafted_actuation','load_coupling'],'athena':['direction/drive/action separation','distributed actuation','fast mode switching'],'cycle':['IDLE','DRIVEN','ROTATING','PROPULSION','SWITCH_OR_STOP']},
    3:{'id':'PROCESSIVE_TRACK_WALKER','label':'processive track walker','examples':['KINESIN','DYNEIN'],'mechanism':'track address -> alternating bind/step cycle -> directional cargo advance','portable':['typed_route_walking','cargo_bound_navigation','polarity_aware_transport','processivity'],'athena':['JSPACE route walking','bidirectional transport roles','packet track/address binding'],'cycle':['DETACHED','BOUND','STEP_A','STEP_B','ADVANCED','BOUND_OR_RELEASE']},
    4:{'id':'CONTRACTILE_SLIDING_ACTUATOR','label':'contractile sliding actuator','examples':['MYOSIN'],'mechanism':'many local force cycles -> coordinated sliding -> contractile work','portable':['parallel_local_actuation','load_sharing','collective_force_integration','attach_pull_release'],'athena':['collective worker actuation','local-to-global force integration','load-aware execution'],'cycle':['AVAILABLE','ATTACHED','POWER_STROKE','RELEASE','RESET']},
    5:{'id':'TEMPLATE_TRANSLATION_ASSEMBLER','label':'template translation assembler','examples':['RIBOSOME'],'mechanism':'template read -> adapter decode -> ordered component admission -> assembly -> translocation','portable':['template_compiler','adapter_mediated_decode','sequential_assembly','stop_condition'],'athena':['spec-to-artifact compiler','decoder/adapter separation','ordered assembly receipt'],'cycle':['READY','READ','DECODE','ADMIT','ASSEMBLE','TRANSLOCATE','READ_OR_STOP']},
    6:{'id':'TEMPLATE_COPY_PROOFREADER','label':'template copy + proofreader','examples':['DNA_POLYMERASE'],'mechanism':'template traversal -> append -> inspect -> correct/accept -> advance','portable':['copy_with_integrity','inline_proofread','transactional_append','local_error_repair'],'athena':['version-bound replication','inline verification','copy-with-integrity witness'],'cycle':['READY','READ','APPEND','CHECK','CORRECT_OR_ACCEPT','ADVANCE']},
    7:{'id':'FRONTIER_UNWINDING_TRANSLOCASE','label':'frontier unwinding translocase','examples':['HELICASE'],'mechanism':'advance on coupled substrate -> separate local frontier -> expose downstream substrate','portable':['frontier_open','progressive_unzip','dependency_separation','stream_exposure'],'athena':['recursive source mining','dependency unzipping','progressive frontier access'],'cycle':['BOUND','ADVANCE','SEPARATE','EXPOSE','ADVANCE_OR_RELEASE']},
    8:{'id':'TOPOLOGICAL_STRESS_EDITOR','label':'topological stress editor','examples':['TOPOISOMERASE'],'mechanism':'detect topological stress -> bounded cut/gate -> rearrange -> reseal -> verify invariant','portable':['temporary_cut','conflict_torsion_relief','rejoin_with_witness','invariant_preserving_topology_edit'],'athena':['branch reconciliation','bounded conflict edit','ancestry-preserving reseal'],'cycle':['MONITOR','STRESS_DETECTED','GATE_OPEN','REARRANGE','RESEAL','VERIFY']},
    9:{'id':'TAGGED_SELECTIVE_DEGRADER','label':'tagged selective degrader','examples':['PROTEASOME'],'mechanism':'recognition tag -> gated admission -> process/degrade -> fragment/recycle','portable':['tagged_garbage_collection','selective_pruning','gated_decomposition','recyclable_fragment_return'],'athena':['artifact lifecycle','prune-active-not-lineage','recycling pipeline'],'cycle':['SCAN','TAG_RECOGNIZED','ADMIT','PROCESS','FRAGMENT','RECYCLE']},
    10:{'id':'ISOLATED_REFOLDING_CHAMBER','label':'isolated refolding chamber','examples':['GROEL_GROES_CHAPERONIN'],'mechanism':'capture malformed object -> isolate -> bounded transformation/retry -> release -> recheck','portable':['sandboxed_repair','bounded_retry','failure_isolation','refold_then_reverify'],'athena':['quarantine repair','sandboxed refolding','retest before reintegration'],'cycle':['OPEN','CAPTURE','ISOLATE','REFOLD_RETRY','OPEN','RECHECK']},
    11:{'id':'GATED_BOUNDARY_SECRETION_CONDUIT','label':'gated boundary secretion conduit','examples':['TYPE_III_SECRETION_SYSTEM'],'mechanism':'boundary-spanning conduit -> payload recognition -> gate -> translocation -> delivery witness','portable':['typed_boundary_channel','payload_gate','source_to_recipient_transport','delivery_receipt'],'athena':['cross-lane conduit','payload admission gate','persistent typed delivery'],'cycle':['ASSEMBLED','PAYLOAD_RECOGNIZED','DOCKED','TRANSLOCATING','DELIVERED','READY']},
    12:{'id':'CONTRACTILE_PUNCTURE_INJECTOR','label':'contractile puncture injector','examples':['TYPE_VI_SECRETION_SYSTEM','BACTERIOPHAGE_TAIL_ASSEMBLY'],'mechanism':'target attachment -> armed/ready -> stored-energy release or contraction -> penetration -> payload delivery -> spent/reset','portable':['attachment_before_execution','commit_gated_injection','stored_energy_release','one_shot_delivery_transaction','terminal_spent_state'],'athena':['attachment-gated commit','one-shot delivery transaction','terminal receipt'],'cycle':['SEARCH','ATTACHED','ARMED','PENETRATION','DELIVERY','SPENT_OR_RESET']},
}

SEEDS={
    'ATP_SYNTHASE':{'name':'ATP synthase','row':1},
    'BACTERIAL_FLAGELLAR_MOTOR':{'name':'Bacterial flagellar motor','row':2},
    'KINESIN':{'name':'Kinesin','row':3},
    'DYNEIN':{'name':'Dynein','row':3},
    'MYOSIN':{'name':'Myosin','row':4},
    'RIBOSOME':{'name':'Ribosome','row':5},
    'DNA_POLYMERASE':{'name':'DNA polymerase','row':6},
    'HELICASE':{'name':'Helicase','row':7},
    'TOPOISOMERASE':{'name':'Topoisomerase','row':8},
    'PROTEASOME':{'name':'Proteasome','row':9},
    'GROEL_GROES_CHAPERONIN':{'name':'GroEL/GroES chaperonin','row':10},
    'TYPE_III_SECRETION_SYSTEM':{'name':'Type III secretion system','row':11},
    'TYPE_VI_SECRETION_SYSTEM':{'name':'Type VI secretion system','row':12},
    'BACTERIOPHAGE_TAIL_ASSEMBLY':{
        'name':'T4-like bacteriophage tail assembly','row':12,
        'visual_components':['capsid','genome','portal protein','contractile sheath','tail tube','base plate','long tail fibers','short tail fibers','tail pins','lysozyme enzyme','fiber attachment knobs','sheath terminator','core rod','tail tube adapter','base plate wedges'],
        'visual_sequence':['attachment','penetration/sheath contraction','payload injection','spent/empty external particle']
    },
}

FACET_PURPOSE={
    'identity_role':'what machine class/role is being represented',
    'energy_drive':'what energetic or control potential drives state change',
    'input_cargo':'what payload/reactant/cargo enters the machine contract',
    'output_work':'what useful transformation or work leaves the cycle',
    'substrate_track':'what membrane/track/template/target constrains operation',
    'geometry_topology':'what spatial/graph organization enables the mechanism',
    'state_cycle':'what ordered states and transitions constitute operation',
    'coupling_gating':'what binding/gating/switching couples drive to work',
    'fidelity_error_control':'what local checks constrain malformed output',
    'assembly_maintenance':'how the machine is built, maintained, reset or turned over',
    'failure_recovery':'how stall/failure is detected and repaired or held',
    'interface_transfer':'what producer/consumer interface and computational analogy are lawful',
}

PHAGE_ASSEMBLY_EDGES=[
    {'src':'portal protein','relation':'interfaces','dst':'capsid'},
    {'src':'portal protein','relation':'interfaces','dst':'contractile sheath'},
    {'src':'tail tube','relation':'nested_within','dst':'contractile sheath'},
    {'src':'contractile sheath','relation':'anchors_to','dst':'base plate'},
    {'src':'tail tube','relation':'connects_via','dst':'tail tube adapter'},
    {'src':'tail tube adapter','relation':'interfaces','dst':'base plate'},
    {'src':'long tail fibers','relation':'attach_via','dst':'fiber attachment knobs'},
    {'src':'fiber attachment knobs','relation':'attach_to','dst':'base plate'},
    {'src':'tail pins','relation':'attach_to','dst':'base plate'},
    {'src':'base plate wedges','relation':'compose','dst':'base plate'},
]


def _gid(row:int,column:int)->int:return 12*(row-1)+column


def _cells(row:int,arch:Dict[str,Any])->List[Dict[str,Any]]:
    return [
        {
            'row':row,'column':i,'gid':_gid(row,i),'facet':facet,
            'role':f"{arch['label']} :: {FACET_PURPOSE[facet]}",
            'status':'MODELED_MECHANISM_FACET'
        }
        for i,facet in enumerate(COLUMNS,1)
    ]


def _kernel12(seed:Dict[str,Any],arch:Dict[str,Any])->Dict[str,Any]:
    out={}
    for facet in COLUMNS:
        out[facet]={
            'terms':[facet],
            'roles':[FACET_PURPOSE[facet]],
            'claims':[{'text':f"{seed['name']} is represented under {arch['id']} for the {facet} facet.",'status':'MODELED'}],
            'loss':['This is a mechanism abstraction; source-specific molecular detail and quantitative constants require independent evidence.']
        }
    return out


def _lift4(kernel:Dict[str,Any])->Dict[str,Any]:
    def pack(keys):
        return {'terms':keys,'roles':[kernel[k]['roles'][0] for k in keys],'claims':sum((kernel[k]['claims'] for k in keys),[]),'loss':['Typed compression of 12D facets; inspect kernel12 for full separation.']}
    return {
        'structure':pack(['identity_role','substrate_track','geometry_topology']),
        'drive':pack(['energy_drive','input_cargo','coupling_gating']),
        'work':pack(['output_work','state_cycle','interface_transfer']),
        'integrity':pack(['fidelity_error_control','assembly_maintenance','failure_recovery']),
    }


class BionanomachineRuntime:
    def catalog(self,include_atlas:bool=False)->Dict[str,Any]:
        rows=[{'row':r,'row_id':f'R{r:02d}',**{k:v for k,v in a.items() if k!='cycle'}} for r,a in ARCHETYPES.items()]
        result={
            'version':BIONANO_VERSION,
            'status':'MODELED_OPERATOR_LIBRARY',
            'epistemic_laws':list(EPISTEMIC_LAWS),
            'columns':[{'column':i,'id':f'C{i:02d}','facet':f} for i,f in enumerate(COLUMNS,1)],
            'rows':rows,
            'seed_machines':[{'machine_id':mid,'native_name':s['name'],'row':s['row'],'evidence_mode':['USER_SEED','MECHANISTIC_MODEL'],'numeric_seed_policy':'UNVERIFIED_NUMERIC_VALUES_NOT_CANONICAL'} for mid,s in SEEDS.items()],
            'kc144':{'rows':12,'columns':12,'cells':144,'gid_law':'gid=12*(row-1)+column'},
            'authority':'ANALOGY_AND_MECHANISM_MODEL_ONLY',
        }
        if include_atlas:
            result['atlas']=[cell for row,arch in ARCHETYPES.items() for cell in _cells(row,arch)]
        return result

    def compile(self,machine_id:str)->Dict[str,Any]:
        mid=str(machine_id).strip().upper()
        seed=SEEDS.get(mid)
        if seed is None:
            return {'version':BIONANO_VERSION,'status':'HOLD_UNKNOWN_MACHINE','machine_id':mid,'known_machine_ids':sorted(SEEDS),'law':'UNKNOWN_MACHINE != FABRICATED_CLASSIFICATION'}
        row=seed['row'];arch=ARCHETYPES[row];kernel=_kernel12(seed,arch)
        return {
            'version':BIONANO_VERSION,'status':'COMPILED_MODEL','machine_id':mid,'native_name':seed['name'],
            'archetype':arch['id'],'row':row,'row_id':f'R{row:02d}',
            'evidence_mode':['USER_SEED','MECHANISTIC_MODEL'],
            'lift4':_lift4(kernel),'kernel12':kernel,
            'kc144':{'row':row,'row_id':f'R{row:02d}','cells':_cells(row,arch)},
            'state_machine':{'states':list(arch['cycle']),'reset_or_terminal':arch['cycle'][-1]},
            'mechanism':arch['mechanism'],'portable_operators':list(arch['portable']),'athena_targets':list(arch['athena']),
            'numeric_seed_policy':'UNVERIFIED_USER_NUMBERS_NOT_CANONICAL',
            'authority':'MODELED_MECHANISM_NOT_EMPIRICAL_VERIFICATION',
            'laws':list(EPISTEMIC_LAWS),
        }

    def transfer(self,machine_id:str,target:str,constraints=None)->Dict[str,Any]:
        compiled=self.compile(machine_id)
        if compiled.get('status')!='COMPILED_MODEL':return compiled
        return {
            'version':BIONANO_VERSION,'status':'ANALOGY_CANDIDATE','machine_id':compiled['machine_id'],'target':str(target),
            'portable_operators':compiled['portable_operators'],'suggested_athena_targets':compiled['athena_targets'],
            'constraints':list(constraints or []),
            'nonportable_context':['molecular composition','organism-specific environment','biochemical quantitative constants','evolutionary history'],
            'transfer_loss':['biological mechanism has richer stochastic, energetic, spatial and evolutionary context than the computational abstraction'],
            'authority':'COMPUTATIONAL_ANALOGY_ONLY',
            'law':'ANALOGY_TO != IS_SAME_AS; TRANSFER_OPERATOR != BIOLOGICAL_CLAIM',
        }

    def interface_match(self,producer:Dict[str,float],consumer:Dict[str,float])->Dict[str,Any]:
        keys=['rate','latency','error_tolerance','statefulness','reversibility','coupling']
        p=[float(producer[k]) for k in keys];c=[float(consumer[k]) for k in keys]
        for v in p+c:
            if not 0.0<=v<=1.0:raise ValueError('interface profile values must be within [0,1]')
        mismatch=math.sqrt(sum((a-b)**2 for a,b in zip(p,c)))/math.sqrt(len(keys))
        match=max(0.0,min(1.0,1.0-mismatch))
        status='MATCHED' if match>=0.85 else ('ADAPTER_RECOMMENDED' if match>=0.60 else 'MISMATCH_HOLD')
        deltas={k:round(producer[k]-consumer[k],6) for k in keys}
        return {'version':BIONANO_VERSION,'status':status,'match':round(match,6),'mismatch':round(mismatch,6),'deltas':deltas,'coordinate':'INTERFACE_PROFILE_6D','authority':'COMPUTATIONAL_COMPATIBILITY_PROXY','law':'INTERFACE_MATCH_PROXY != PHYSICAL_IMPEDANCE; ROUTE_EXISTS != INTERFACE_MATCHED'}

    def convergence_gate(self,**kwargs)->Dict[str,Any]:
        tests=[]
        nth=kwargs.get('nth_term_limit')
        if nth is not None:
            tests.append({'test':'NTH_TERM','value':nth,'status':'DIVERGES' if abs(float(nth))>1e-12 else 'INCONCLUSIVE','law':'nonzero term limit is incompatible with series convergence; zero is necessary not sufficient'})
        for key,label in [('ratio_limit','RATIO'),('root_limit','ROOT')]:
            value=kwargs.get(key)
            if value is not None:
                v=float(value);status='CONVERGES_ABSOLUTELY' if v<1 else ('DIVERGES' if v>1 else 'INCONCLUSIVE')
                tests.append({'test':label,'value':v,'status':status,'law':'applies only when the corresponding test assumptions are satisfied'})
        q=kwargs.get('contraction_q')
        if q is not None:
            v=float(q);status='CONTRACTION_WITNESS' if v<1 else ('NOT_A_CONTRACTION' if v>1 else 'BOUNDARY_INCONCLUSIVE')
            tests.append({'test':'CONTRACTION','value':v,'status':status,'law':'q<1 witnesses contraction under the caller-supplied metric/domain assumptions'})
        rho=kwargs.get('spectral_radius')
        if rho is not None:
            v=float(rho);status='LINEAR_STABLE' if v<1 else ('LINEAR_UNSTABLE' if v>1 else 'BOUNDARY_INCONCLUSIVE')
            tests.append({'test':'SPECTRAL_RADIUS','value':v,'status':status,'law':'rho<1 is a scoped discrete linear stability witness, not a general nonlinear proof'})
        failing={'DIVERGES','NOT_A_CONTRACTION','LINEAR_UNSTABLE'}
        passing={'CONVERGES_ABSOLUTELY','CONTRACTION_WITNESS','LINEAR_STABLE'}
        if any(t['status'] in failing for t in tests):status='FAIL_WITNESS'
        elif any(t['status'] in passing for t in tests):status='PASS_WITNESS_SCOPED'
        else:status='HOLD_INCONCLUSIVE'
        if not tests:status='HOLD_NO_WITNESS'
        return {'version':BIONANO_VERSION,'status':status,'tests':tests,'law':'AVAILABLE_TEST != APPLICABLE_TEST; PASS_WITNESS_SCOPED != UNIVERSAL_CONVERGENCE_PROOF'}

    def assembly(self,machine_id:str)->Dict[str,Any]:
        mid=str(machine_id).strip().upper();compiled=self.compile(mid)
        if compiled.get('status')!='COMPILED_MODEL':return compiled
        seed=SEEDS[mid]
        if mid=='BACTERIOPHAGE_TAIL_ASSEMBLY':
            return {
                'version':BIONANO_VERSION,'status':'USER_VISUAL_ASSEMBLY_PACKET','machine_id':mid,
                'components':list(seed['visual_components']),'dependency_edges':list(PHAGE_ASSEMBLY_EDGES),
                'functional_sequence':list(seed['visual_sequence']),
                'component_count':len(seed['visual_components']),'provenance':'USER_VISUAL_SEED',
                'authority':'STRUCTURAL_VISUAL_SEED_NOT_INDEPENDENT_BIOLOGICAL_VERIFICATION',
                'law':'PARTS_LIST != ASSEMBLED_CAPABILITY; ASSEMBLY != EXECUTION; EXECUTION != SUCCESS'
            }
        arch=ARCHETYPES[seed['row']]
        return {
            'version':BIONANO_VERSION,'status':'GENERIC_MECHANISM_ASSEMBLY_ABSTRACTION','machine_id':mid,
            'components':['input_interface','energy_coupling_module','work_core','quality_gate','output_interface'],
            'dependency_edges':[
                {'src':'input_interface','relation':'feeds','dst':'work_core'},
                {'src':'energy_coupling_module','relation':'drives','dst':'work_core'},
                {'src':'work_core','relation':'checked_by','dst':'quality_gate'},
                {'src':'quality_gate','relation':'releases_to','dst':'output_interface'},
            ],
            'functional_sequence':list(arch['cycle']),'provenance':'MODELED_MECHANISM_ABSTRACTION',
            'authority':'NOT_A_SOURCE_SPECIFIC_MOLECULAR_BOM',
            'law':'GENERIC_FUNCTIONAL_MODULES != NATIVE_PROTEIN_SUBUNIT_INVENTORY'
        }

    def benchmark(self)->Dict[str,Any]:
        atlas=[cell for row,arch in ARCHETYPES.items() for cell in _cells(row,arch)]
        return {
            'bionano_archetypes':len(ARCHETYPES),'bionano_seed_machines':len(SEEDS),'bionano_columns':len(COLUMNS),
            'bionano_kc144_cells':len(atlas),'bionano_gid_unique':len({c['gid'] for c in atlas})==144,
            'bionano_phage_visual_components':len(SEEDS['BACTERIOPHAGE_TAIL_ASSEMBLY']['visual_components']),
        }
