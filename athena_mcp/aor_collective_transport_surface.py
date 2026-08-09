from __future__ import annotations

from typing import Any,Dict

from .aor_collective_transport import TransportRuntime,TRANSPORT_VERSION
from .aor_collective_transport_protocol import TRANSPORT_RESOURCE,TRANSPORT_TOOLS,TRANSPORT_TOOL_NAMES
from .party_coordination_v2 import PartyCoordinationRuntimeV2
from .party_coordination_protocol import (
    PARTY_COORDINATION_RESOURCE,
    PARTY_COORDINATION_TOOLS,
    PARTY_COORDINATION_TOOL_NAMES,
)
from .party_coordination_v2_protocol import PARTY_CHANNEL_TOOLS,PARTY_CHANNEL_TOOL_NAMES
from .impossible_godboard import ImpossibleGodboardRuntime
from .impossible_godboard_protocol import (
    IMPOSSIBLE_GODBOARD_RESOURCE,
    IMPOSSIBLE_GODBOARD_TOOLS,
    IMPOSSIBLE_GODBOARD_TOOL_NAMES,
)
from .cohesion_evidence_guard import CohesionEvidenceGuardRuntime
from .cohesion_mesh_protocol import (
    COHESION_MESH_RESOURCE,
    COHESION_MESH_TOOLS,
    COHESION_MESH_TOOL_NAMES,
)
from .cohesion_duplicate_guard import augment_cohesion_resource,duplicate_guard
from .cohesion_duplicate_guard_protocol import DUPLICATE_GUARD_TOOLS,DUPLICATE_GUARD_TOOL_NAMES

AOR_COLLECTIVE_TRANSPORT_TOOLS=(
    list(TRANSPORT_TOOLS)+list(PARTY_COORDINATION_TOOLS)+list(PARTY_CHANNEL_TOOLS)+
    list(IMPOSSIBLE_GODBOARD_TOOLS)+list(COHESION_MESH_TOOLS)+list(DUPLICATE_GUARD_TOOLS)
)
AOR_COLLECTIVE_TRANSPORT_RESOURCES=[
    TRANSPORT_RESOURCE,PARTY_COORDINATION_RESOURCE,IMPOSSIBLE_GODBOARD_RESOURCE,COHESION_MESH_RESOURCE
]
AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES=(
    set(TRANSPORT_TOOL_NAMES)|set(PARTY_COORDINATION_TOOL_NAMES)|set(PARTY_CHANNEL_TOOL_NAMES)|
    set(IMPOSSIBLE_GODBOARD_TOOL_NAMES)|set(COHESION_MESH_TOOL_NAMES)|set(DUPLICATE_GUARD_TOOL_NAMES)
)
AOR_COLLECTIVE_TRANSPORT_RESOURCE_URIS={
    TRANSPORT_RESOURCE['uri'],PARTY_COORDINATION_RESOURCE['uri'],IMPOSSIBLE_GODBOARD_RESOURCE['uri'],
    COHESION_MESH_RESOURCE['uri']
}

class AorCollectiveTransportSurface:
    def __init__(self,server):
        self.server=server
        self.runtime=TransportRuntime(server)
        self.party=PartyCoordinationRuntimeV2(server)
        self.godboard=ImpossibleGodboardRuntime(server)
        self.cohesion=CohesionEvidenceGuardRuntime(server)

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name in DUPLICATE_GUARD_TOOL_NAMES:
            return True,duplicate_guard(
                self.cohesion,
                agent_id=args['agent_id'],
                task=args['task'],
                work_key=args.get('work_key'),
                targets=args.get('targets'),
                intended_mode=args.get('intended_mode','PRIMARY'),
                replication_reason=args.get('replication_reason'),
                join_agent_id=args.get('join_agent_id'),
                partition_proof=args.get('partition_proof'),
                remote=args.get('remote','origin'),
                shared_remote_mode=args.get('shared_remote_mode','REQUIRED'),
            )
        if name in COHESION_MESH_TOOL_NAMES:
            c=self.cohesion
            if name=='athena_cohesion_request_offer':
                return True,c.request_offer(
                    args['request_id'],args['agent_id'],args['kind'],args['capabilities'],args['goal_ref'],
                    args.get('role',''),args.get('work_key'),args.get('targets'),args.get('dependencies'),
                    args.get('provides'),args.get('capacity_units',1),args.get('needed_units',1),
                    args.get('constraints'),args.get('acceptance_criteria'),args.get('party_id'),
                    args.get('quest_ref'),args.get('life_policy'),args.get('clear_condition_digest'),
                    args.get('allow_collaboration',False),args.get('expires_at'),args.get('remote','origin')
                )
            if name=='athena_cohesion_matchmake':
                return True,c.matchmake(
                    args['need_id'],args.get('limit',10),args.get('remote','origin'),
                    args.get('shared_remote_mode','REQUIRED')
                )
            if name=='athena_cohesion_coalition':
                return True,c.coalition(
                    args['campaign_id'],args['proposer_id'],args['need_ids'],args.get('max_participants',8),
                    args.get('exit_criteria'),args.get('rendezvous_refs'),args.get('remote','origin')
                )
            if name=='athena_cohesion_solo_party_compare':
                return True,c.solo_party_compare(
                    args['comparison_id'],args['observer_id'],args['solo_samples'],args['party_samples'],
                    args['decision_rule'],args.get('remote','origin')
                )
        if name in IMPOSSIBLE_GODBOARD_TOOL_NAMES:
            g=self.godboard
            if name=='athena_impossible_open':
                return True,g.open(
                    args['quest_id'],args['opener_id'],args['title'],args['barrier'],
                    args['success_conditions'],args['search_scope'],args.get('safety_scope'),
                    args.get('remote','origin')
                )
            if name=='athena_impossible_complete':
                if args.get('party_id') or args.get('contributors'):
                    fresh=g._board().read(
                        remote=args.get('remote','origin'),shared_remote_mode='REQUIRED',limit=1
                    )
                    if not fresh.get('shared_frontier_verified'):
                        return True,{
                            'status':'GODBOARD_SHARED_FRONTIER_HOLD',
                            'remote_sync':fresh.get('remote_sync'),
                            'durable_return':False,
                            'law':'PARTY_ATTRIBUTION_REQUIRES_SHARED_CURRENT_MESSAGE_BOARD_FRONTIER',
                        }
                return True,g.complete(
                    args['completion_id'],args['quest_id'],args['agent_id'],args['agent_coordinate'],
                    args['baseline'],args['transformation_class'],args['decisive_move'],args['invariant'],
                    args['result'],args['witness_refs'],args['cleanup_status'],args['unknown_residue'],
                    args['proof_tier'],args['score_dimensions'],args.get('multipliers'),
                    args.get('failed_approaches'),args.get('known_limits'),args.get('party_id'),
                    args.get('contributors'),args.get('remote','origin')
                )
            if name=='athena_impossible_verify':
                return True,g.verify(
                    args['verification_id'],args['completion_id'],args['verifier_id'],
                    args['verifier_coordinate'],args['target_proof_tier'],args['witness_refs'],
                    args.get('attack_refs'),args.get('generalization_ref'),args.get('downstream_reuse_refs'),
                    args.get('immortal_title'),args.get('party_immortal_title'),args.get('remote','origin')
                )
            if name=='athena_impossible_state':
                return True,g.state(
                    args['quest_id'],args.get('remote','origin'),args.get('shared_remote_mode','REQUIRED')
                )
            if name=='athena_godboard':
                return True,g.godboard(
                    args.get('limit',50),args.get('remote','origin'),args.get('shared_remote_mode','REQUIRED')
                )
            if name=='athena_hall_of_immortals':
                return True,g.hall(
                    args.get('limit',100),args.get('remote','origin'),args.get('shared_remote_mode','REQUIRED')
                )
        if name in PARTY_CHANNEL_TOOL_NAMES:
            p=self.party
            return True,p.message(
                args['party_id'],args['sender'],args['recipients'],args['goal_refs'],args['message'],
                args.get('message_kind','INFO'),args.get('reply_to'),args.get('remote','origin')
            )
        if name in PARTY_COORDINATION_TOOL_NAMES:
            p=self.party
            if name=='athena_party_form':
                return True,p.form(
                    args['party_id'],args['leader'],args['goals'],args['leader_goal_refs'],
                    args.get('purpose',''),args.get('role','LEAD'),args.get('capabilities'),
                    args.get('capacity',4),args.get('remote','origin')
                )
            if name=='athena_party_join':
                return True,p.join(
                    args['party_id'],args['agent'],args['goal_refs'],args['task_relation'],
                    args.get('role','MEMBER'),args.get('capabilities'),args.get('remote','origin')
                )
            if name=='athena_party_state':
                return True,p.state(args['party_id'],args.get('remote','origin'),args.get('shared_remote_mode','REQUIRED'))
            if name=='athena_party_list':
                return True,p.list(args.get('remote','origin'),args.get('shared_remote_mode','REQUIRED'),args.get('limit',50))
            if name=='athena_party_observe':
                return True,p.observe(
                    args['observation_id'],args['party_id'],args['observer'],args['base_xp'],
                    args['results'],args['witness_ref'],args.get('remote','origin')
                )
        r=self.runtime
        if name=='athena_transport_pheromone_attention':return True,r.pheromone_attention(args['route_keys'],args.get('actor','agent'),args.get('persist',True))
        if name=='athena_transport_alarm_to_gap':return True,r.alarm_to_gap(args['alarm_ref'],args['alarm_nodes'],args.get('actor','agent'),args.get('persist',True))
        if name=='athena_transport_aor_to_collective':return True,r.aor_to_collective(args['run_id'],args.get('actor','agent'),args.get('persist',True))
        if name=='athena_transport_rgo_to_reward':return True,r.rgo_to_reward(args['outcome_ref'],args['observed_rgo'],args['witness_ref'],args.get('delta_j'),args.get('delta_outcome_ref'),args.get('actor','agent'),args.get('persist',True))
        if name=='athena_transport_bridge_to_collective':return True,r.bridge_to_collective(args['candidate_ref'],args['economics'],args.get('actor','agent'),args.get('persist',True))
        if name=='athena_transport_antibody_to_repair':return True,r.antibody_to_repair(args['failure_ref'],args['matches'],args.get('actor','agent'),args.get('persist',True))
        if name=='athena_transport_get':return True,r.get(args['run_id'])
        if name=='athena_transport_replay':return True,r.replay(args['run_id'])
        if name=='athena_transport_recent':return True,r.recent(args.get('limit',50))
        return False,None

    def read_resource(self,uri:str):
        if uri==COHESION_MESH_RESOURCE['uri']:return augment_cohesion_resource(self.cohesion.resource())
        if uri==IMPOSSIBLE_GODBOARD_RESOURCE['uri']:return self.godboard.resource()
        if uri==PARTY_COORDINATION_RESOURCE['uri']:return self.party.resource()
        if uri!=TRANSPORT_RESOURCE['uri']:raise KeyError(uri)
        return {
            'version':TRANSPORT_VERSION,
            'benchmark':self.runtime.benchmark(),
            'transports':['PHEROMONE_TO_ATTENTION','ALARM_TO_GAP','AOR_FRONTIER_TO_COLLECTIVE_TASKS','OBSERVED_RGO_TO_REWARD_OBSERVATION','AOR_BRIDGE_TO_COLLECTIVE_ACCOUNT','ANTIBODY_TO_REPAIR_CANDIDATE'],
            'laws':[
                'pheromone/reuse/popularity != relevance != evidence != Y authority',
                'alarm pressure != proof of falsity/causality/logical entailment',
                'AOR chooses WHAT is developmentally eligible; Collective chooses HOW capacity is assigned',
                'observed RGO != automatic DeltaJ/evidence; same outcome must not be double counted',
                'AOR bridge score != Collective bridge economics',
                'antibody match != verified repair success; repair remains an UNMEASURED candidate until tested',
            ],
        }

    def benchmark(self):
        result=dict(self.runtime.benchmark())
        result.update(self.party.benchmark())
        result.update(self.godboard.benchmark())
        result.update(self.cohesion.benchmark())
        return result
