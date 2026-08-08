COLLECTIVE_V2_TOOLS = [
{
  "name":"athena_pheromone_reinforce",
  "description":"Persistently reinforce or evaporate one artifact/routing pheromone using evidence, reuse, novelty, staleness and contradiction observations.",
  "inputSchema":{"type":"object","required":["route_key","observations"],"properties":{
    "route_key":{"type":"string"},"observations":{"type":"object"},"age":{"type":["number","null"]},
    "evaporation_rate":{"type":"number"},"deposit_gain":{"type":"number"},"actor":{"type":"string"}
  },"additionalProperties":False}
},
{
  "name":"athena_pheromone_field",
  "description":"Read the durable stigmergic priority field for one route or the highest-priority routes.",
  "inputSchema":{"type":"object","properties":{
    "route_key":{"type":["string","null"]},"limit":{"type":"integer","minimum":1,"maximum":1000},"min_score":{"type":"number"}
  },"additionalProperties":False}
},
{
  "name":"athena_jspace_alarm",
  "description":"Compile typed JSPACE edges into an invalidation graph and propagate a bounded decaying alarm. Known dependency relations reverse direction so dependencies invalidate their dependents; unknown relations are ignored unless explicitly mapped.",
  "inputSchema":{"type":"object","required":["seeds"],"properties":{
    "seeds":{"type":"array","minItems":1,"items":{"type":"object","required":["node"],"properties":{"node":{"type":"string"},"severity":{"type":"number"}},"additionalProperties":False}},
    "relation_modes":{"type":"object"},"max_hops":{"type":"integer","minimum":0,"maximum":64},
    "hop_decay":{"type":"number"},"threshold":{"type":"number"}
  },"additionalProperties":False}
},
{
  "name":"athena_rgo_observe",
  "description":"Record predicted versus observed Return-on-Group-Organization and update the persistent online calibration witness.",
  "inputSchema":{"type":"object","required":["plan_key","predicted_rgo","observed_rgo"],"properties":{
    "plan_key":{"type":"string"},"predicted_rgo":{"type":"number"},"observed_rgo":{"type":"number"},
    "features":{"type":"object"},"scope":{"type":"string"},"actor":{"type":"string"}
  },"additionalProperties":False}
},
{
  "name":"athena_rgo_calibrate",
  "description":"Calibrate a new predicted RGO against accumulated downstream observations with reliability shrinkage toward the identity predictor.",
  "inputSchema":{"type":"object","required":["predicted_rgo"],"properties":{
    "predicted_rgo":{"type":"number"},"scope":{"type":"string"}
  },"additionalProperties":False}
},
{
  "name":"athena_topology_get",
  "description":"Read one versioned collective-control topology and its current CAS version.",
  "inputSchema":{"type":"object","required":["topology_id"],"properties":{"topology_id":{"type":"string"}},"additionalProperties":False}
},
{
  "name":"athena_topology_apply",
  "description":"Transactionally apply INIT/REPLACE/FISSION/FUSE/PATCH_MODULE to a collective topology only when expected_version matches current version; records reversible before/after witnesses.",
  "inputSchema":{"type":"object","required":["topology_id","expected_version","operation","payload"],"properties":{
    "topology_id":{"type":"string"},"expected_version":{"type":"integer","minimum":0},
    "operation":{"type":"string"},"payload":{"type":"object"},"actor":{"type":"string"}
  },"additionalProperties":False}
},
{
  "name":"athena_topology_rollback",
  "description":"Rollback a prior collective topology transaction under current-version CAS while preserving rollback itself as a new witnessed transaction.",
  "inputSchema":{"type":"object","required":["topology_id","txid","expected_version"],"properties":{
    "topology_id":{"type":"string"},"txid":{"type":"string"},"expected_version":{"type":"integer","minimum":0},"actor":{"type":"string"}
  },"additionalProperties":False}
},
{
  "name":"athena_failure_antibody_register",
  "description":"Persist a diagnosed failure as a reusable signature, trigger, detector, repair, evidence bundle and regression/replay references.",
  "inputSchema":{"type":"object","required":["signature"],"properties":{
    "signature":{"type":"string"},"trigger":{"type":"object"},"detector":{"type":"object"},"repair":{"type":"object"},
    "evidence":{"type":"object"},"regression_refs":{"type":"array","items":{"type":"string"}},"scope":{"type":"string"},"actor":{"type":"string"}
  },"additionalProperties":False}
},
{
  "name":"athena_failure_antibody_match",
  "description":"Match a new failure/event against the durable antibody registry and return reusable repairs and regression witnesses; optionally records successful antibody hits.",
  "inputSchema":{"type":"object","required":["event"],"properties":{
    "event":{"type":"string"},"tags":{"type":"array","items":{"type":"string"}},"scope":{"type":["string","null"]},
    "threshold":{"type":"number"},"limit":{"type":"integer","minimum":1,"maximum":100},"record_hits":{"type":"boolean"}
  },"additionalProperties":False}
},
]
