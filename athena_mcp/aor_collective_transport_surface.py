from __future__ import annotations

from typing import Any,Dict

from .aor_collective_transport import TransportRuntime,TRANSPORT_VERSION
from .aor_collective_transport_protocol import TRANSPORT_RESOURCE,TRANSPORT_TOOLS,TRANSPORT_TOOL_NAMES
from .party_coordination import PartyCoordinationRuntime
from .party_coordination_protocol import (
    PARTY_COORDINATION_RESOURCE,
    PARTY_COORDINATION_TOOLS,
    PARTY_COORDINATION_TOOL_NAMES,
)
from .impossible_godboard import ImpossibleGodboardRuntime
from .impossible_godboard_protocol import (
    IMPOSSIBLE_GODBOARD_RESOURCE,
    IMPOSSIBLE_GODBOARD_TOOLS,
    IMPOSSIBLE_GODBOARD_TOOL_NAMES,
)
from .stay_in_game_life_loop import StayInGameLifeLoopRuntime
from .stay_in_game_life_loop_protocol import (
    STAY_IN_GAME_LIFE_LOOP_RESOURCE,
    STAY_IN_GAME_LIFE_LOOP_TOOLS,
    STAY_IN_GAME_LIFE_LOOP_TOOL_NAMES,
)

AOR_COLLECTIVE_TRANSPORT_TOOLS=(
    list(TRANSPORT_TOOLS)+list(PARTY_COORDINATION_TOOLS)+list(IMPOSSIBLE_GODBOARD_TOOLS)+list(STAY_IN_GAME_LIFE_LOOP_TOOLS)
)
AOR_COLLECTIVE_TRANSPORT_RESOURCES=[
    TRANSPORT_RESOURCE,PARTY_COORDINATION_RESOURCE,IMPOSSIBLE_GODBOARD_RESOURCE,STAY_IN_GAME_LIFE_LOOP_RESOURCE
]
AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES=(
    set(TRANSPORT_TOOL_NAMES)|set(PARTY_COORDINATION_TOOL_NAMES)|set(IMPOSSIBLE_GODBOARD_TOOL_NAMES)|set(STAY_IN_GAME_LIFE_LOOP_TOOL_NAMES)
)
AOR_COLLECTIVE_TRANSPORT_RESOURCE_URIS={
    TRANSPORT_RESOURCE['uri'],PARTY_COORDINATION_RESOURCE['uri'],IMPOSSIBLE_GODBOARD_RESOURCE['uri'],
    STAY_IN_GAME_LIFE_LOOP_RESOURCE['uri']
}

class AorCollectiveTransportSurface:
    def __init__(self,server):
        self.server=server
        self.runtime=TransportRuntime(server)
        self.party=PartyCoordinationRuntime(server)
        self.godboard=ImpossibleGodboardRuntime(server)
        self.life=StayInGameLifeLoopRuntime(server)

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name in STAY_IN_GAME_LIFE_LOOP_TOOL_NAMES:
            life=self.life
            if name=='athena_life_world_new':
                return True,life.world_new(args['game_id'])
            if name=='athena_life_agent_enter':
                return True,life.agent_enter(args['world'],args['agent_id'],args['quest_id'],args['quest_version'])
            if name=='athena_life_resolve':
                return True,life.resolve(args['world'],args['agent_id'],args['attempt'])
            if name=='athena_campaign_life_bind':
                return True,life.campaign_bind(
                    args['bound_receipt'],args['pulse'],args['agent_coordinate_name'],args['quest_id'],
                    args['quest_version'],args['clear_conditions'],args['reseed_anchor'],
                    args.get('extra_life_reward_candidate')
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
        if uri==STAY_IN_GAME_LIFE_LOOP_RESOURCE['uri']:return self.life.resource()
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
        result.update(self.life.benchmark())
        return result
