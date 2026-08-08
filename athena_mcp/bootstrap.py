GENESIS=[
('TOOL','IDENTITY','RESOLVE','CAPABILITY','CANONICAL_SIGNATURE',{'need':'functional signature'},{'oid':'string','cid':'string','canonical_name':'string'}),
('TOOL','NAVIGATION','RESOLVE','OBJECT','KC144_JSPACE',{'identifier':'OID|CID|name'},{'coordinate':'polycoordinate','edges':'graph'}),
('TOOL','STATE','MUTATE','CANONICAL_OBJECT','EXPECTED_VID_CAS',{'oid':'string','expected_vid':'VID','delta':'object'},{'status':'COMMITTED|STALE_TARGET'}),
('TOOL','TEXT','INDEX','MANIFESTATION','EXACT_LEXEME_COORDINATES',{'text':'string','oid':'OID','vid':'VID'},{'mid':'MID','token_coordinates':'array'}),
('TOOL','SWARM','EMIT','AGENT_PROGRESS','LIMINAL_TELEMETRY',{'agent':'string','event':'public telemetry'},{'eid':'EID','liminal_coordinate':'string'}),
('ALGO','SWARM','REPRESENT','N_WAY_INTERACTION','LAZY_SIMPLEX',{'participants':'2..60'},{'dimension':'n-1','faces':'lazy'}),
('TOOL','SWARM','MATCH','HELP','NEED_OFFER_COMPLEMENTARITY',{'agent':'string'},{'matches':'ranked peers'}),
('POLICY','SWARM','ADOPT','GLOBAL_MUTATION','NEXT_CYCLE_REQUIRED',{'mutation':'global class'},{'adoption_receipt':'EID'}),
('HARNESS','DEVELOPMENT','MAXIMIZE','WHOLE_SYSTEM_DELTA','MAXDEV_SELFPLAY',{'task':'whole objective'},{'crystal_delta':'integrated output'}),
('BENCH','PERFORMANCE','MEASURE','MAXDEV','FRONTIER_VECTOR',{'run':'metrics'},{'pareto_record':'vector'}),
('MODEL','REPRESENTATION','LIFT','EVENTS_TO_ORGAN','SCALE_S0_S5',{'events':'ledger'},{'representation':'S0..S5'}),
('INDEX','GRAPH','PROJECT','CAUSAL_LEDGER','JSPACE',{'events':'ledger'},{'graph':'typed multigraph'})]
def bootstrap(core):
    if core.s.one('SELECT COUNT(*) n FROM objects')['n']: return
    for kind,domain,verb,obj,method,inp,out in GENESIS:
        core.register(kind,domain,verb,obj,method,inp,out,actor='GENESIS',status='CANONICAL')
