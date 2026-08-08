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

AOR_COLLECTIVE_TRANSPORT_TOOLS=list(TRANSPORT_TOOLS)+list(PARTY_COORDINATION_TOOLS)
AOR_COLLECTIVE_TRANSPORT_RESOURCES=[TRANSPORT_RESOURCE,PARTY_COORDINATION_RESOURCE]
AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES=set(TRANSPORT_TOOL_NAMES)|set(PARTY_COORDINATION_TOOL_NAMES)
AOR_COLLECTIVE_TRANSPORT_RESOURCE_URIS={
    TRANSPORT_RESOURCE['uri'],PARTY_COORDINATION_RESOURCE['uri']
}

class AorCollectiveTransportSurface:
    def __init__(self,server):
        self.server=server;self.runtime=TransportRuntime(server);self.party=PartyCoordinationRuntime(server)

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name in PARTY_COORDINATION_TOOL_NAMES:
            p=self.party
            if name=='athena_party_form':
                return True,p.form(
                    args['party_id'],args['task_ref'],args['leader'],args['goals'],args['channels'],
                    args.get('purpose',''),args.get('capacity',4),args.get('role','LEAD'),
                    args.get('capabilities'),args.get('claim_refs')
                )
            if name=='athena_party_join':
                return True,p.join(
                    args['party_id'],args['agent'],args['channel_ref'],args['task_relation'],
                    args.get('role','MEMBER'),args.get('capabilities'),args.get('claim_refs'),
                    args.get('coordination_mode','PARALLEL_COMPLEMENT')
                )
            if name=='athena_party_board_post':
                return True,p.board_post(
                    args['post_id'],args['party_id'],args['agent'],args['kind'],args['channel_ref'],
                    args['body'],args.get('goal_refs'),args.get('claim_refs'),args.get('witness_ref')
                )
            if name=='athena_party_state':return True,p.state(args['party_id'])
            if name=='athena_party_list':return True,p.list(args.get('status'),args.get('limit',50))
            if name=='athena_party_observe':
                return True,p.observe(
                    args['observation_id'],args['party_id'],args['observer'],args['base_xp'],
                    args['advanced_goal_ids'],args['witness_ref']
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
        result=dict(self.runtime.benchmark());result.update(self.party.benchmark());return result
