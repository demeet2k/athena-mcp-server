"""Self-contained KC144 V7 runtime for the live Athena MCP repository."""
from __future__ import annotations
import dataclasses, enum, hashlib, json, os, pathlib, re, time
from typing import Any, Callable, Iterable, Mapping, Sequence

def plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value): return {k: plain(v) for k,v in dataclasses.asdict(value).items()}
    if isinstance(value, enum.Enum): return value.value
    if isinstance(value, Mapping): return {str(k):plain(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,set,frozenset)): return [plain(v) for v in value]
    return value

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(plain(value),sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

class RevisionKind(str,enum.Enum): PROMPT='PROMPT'; TYPE='TYPE'; CLIENT='CLIENT'; GENERATOR='GENERATOR'; TEST='TEST'; OTHER='OTHER'
class AttemptStatus(str,enum.Enum): PASS='PASS'; FAIL='FAIL'; VALIDATION_ERROR='VALIDATION_ERROR'; TIMEOUT='TIMEOUT'; SKIPPED='SKIPPED'
class CoalitionState(str,enum.Enum): FORMING='FORMING'; ACTIVE='ACTIVE'; RETURNING='RETURNING'; DISSOLVED='DISSOLVED'; HOLD='HOLD'
@dataclasses.dataclass(frozen=True)
class RevisionEvent: seq:int; path:str; kind:RevisionKind; old_digest:str; new_digest:str; previous_digest:str; digest:str; authority_effect:str='NONE'
@dataclasses.dataclass(frozen=True)
class RecordedFixture: recording_id:str; function_name:str; request:Mapping[str,Any]; response:Mapping[str,Any]; provider:Mapping[str,Any]; external_witness:bool; digest:str
@dataclasses.dataclass(frozen=True)
class ModelProfile: model_id:str; provider:str; estimated_cost_usd:float; expected_latency_ms:float; reliability:float; capabilities:tuple[str,...]; enabled:bool=True
@dataclasses.dataclass(frozen=True)
class AttemptReceipt: attempt:int; model_id:str; provider:str; status:AttemptStatus; input_digest:str; output_digest:str; latency_ms:float; estimated_cost_usd:float; recorded:bool; defects:tuple[str,...]; error:str|None; truth_effect:str='NONE'; evidence_effect:str='NONE'; authority_effect:str='NONE'
@dataclasses.dataclass(frozen=True)
class FallbackReceipt: function_name:str; selected_model_id:str|None; attempts:tuple[AttemptReceipt,...]; final_status:AttemptStatus; total_estimated_cost_usd:float; total_latency_ms:float; output_digest:str; authority_effect:str='NONE'
@dataclasses.dataclass(frozen=True)
class OrganProposal: organ_id:str; activation:float; priority:int; locks:frozenset[str]; dependencies:frozenset[str]; required_fields:frozenset[str]; return_capable:bool
@dataclasses.dataclass(frozen=True)
class CoalitionWave: sequence:int; selected_organs:tuple[str,...]; observed_fields:tuple[str,...]; state:CoalitionState; defects:tuple[str,...]; evidence_effect:str='NONE'; authority_effect:str='NONE'
@dataclasses.dataclass(frozen=True)
class CoalitionReceipt: waves:tuple[CoalitionWave,...]; completed_organs:tuple[str,...]; held_organs:tuple[str,...]; state:CoalitionState; return_complete:bool; defects:tuple[str,...]; authority_effect:str='NONE'

class BoundaryValidator:
    SCHEMAS={'CompileQueryContract':('query_id','literal','intents','exact_addresses','requires_sources','requires_execution','requires_audit','route_budget','claim_ceiling','authority_effect')}
    def validate(self,function_name:str,output:Any)->tuple[str,...]:
        if not isinstance(output,Mapping): return ('OUTPUT_NOT_MAPPING',)
        defects=[]; missing=[f for f in self.SCHEMAS.get(function_name,()) if f not in output]
        if missing: defects.append('MISSING_FIELDS:'+','.join(missing))
        if output.get('authority_effect')!='NONE': defects.append('AUTHORITY_EFFECT_NOT_NONE')
        if function_name=='CompileQueryContract':
            if int(output.get('route_budget',0))<=0: defects.append('ROUTE_BUDGET_INVALID')
            if output.get('claim_ceiling') not in {'RESEARCH_ONLY','PAUSE','REFUSE'}: defects.append('CLAIM_CEILING_TOO_HIGH')
        return tuple(defects)

class RevisionJournal:
    ROLES={'functions.baml':RevisionKind.PROMPT,'types.baml':RevisionKind.TYPE,'clients.baml':RevisionKind.CLIENT,'generators.baml':RevisionKind.GENERATOR,'tests.baml':RevisionKind.TEST}
    def __init__(self): self.state={}; self.events=[]
    def _append(self,path,old,new):
        prev=self.events[-1].digest if self.events else 'GENESIS'; body={'seq':len(self.events)+1,'path':path,'kind':self.ROLES.get(path,RevisionKind.OTHER).value,'old_digest':old,'new_digest':new,'previous_digest':prev,'authority_effect':'NONE'}
        event=RevisionEvent(body['seq'],path,RevisionKind(body['kind']),old,new,prev,digest(body)); self.events.append(event); return event
    def scan(self,root):
        root=pathlib.Path(root); out=[]; paths=sorted(root.glob('*.baml')); current={p.name for p in paths}
        for p in paths:
            new=hashlib.sha256(p.read_bytes()).hexdigest(); old=self.state.get(p.name,'')
            if new!=old: out.append(self._append(p.name,old,new)); self.state[p.name]=new
        for deleted in sorted(set(self.state)-current): out.append(self._append(deleted,self.state.pop(deleted),''))
        return tuple(out)
    def verify(self):
        prev='GENESIS'
        for seq,e in enumerate(self.events,1):
            body={'seq':e.seq,'path':e.path,'kind':e.kind.value,'old_digest':e.old_digest,'new_digest':e.new_digest,'previous_digest':e.previous_digest,'authority_effect':'NONE'}
            if e.seq!=seq or e.previous_digest!=prev or digest(body)!=e.digest:return False
            prev=e.digest
        return True

class FixtureStore:
    def __init__(self,root): self.root=pathlib.Path(root)
    def load(self,name):
        raw=json.loads((self.root/name).read_text());
        for k,v in raw.get('headers',{}).items():
            if re.search('authorization',k,re.I) and v!='REDACTED': raise ValueError('UNREDACTED_HEADER')
        if re.search(r'sk-[A-Za-z0-9_-]+',json.dumps(raw)): raise ValueError('SECRET_PATTERN')
        body={'recording_id':raw['recording_id'],'function_name':raw['function_name'],'request':raw['request'],'response':raw['response'],'provider':raw['provider'],'external_witness':bool(raw.get('external_witness',False))}
        return RecordedFixture(**body,digest=digest(body))
    def list(self): return tuple(sorted(p.name for p in self.root.glob('*.json')))

class FallbackRouter:
    def __init__(self,profiles,validator=None): self.profiles={p.model_id:p for p in profiles}; self.validator=validator or BoundaryValidator(); self.invokers={}
    def bind(self,model_id,invoker): self.invokers[model_id]=invoker
    def route(self,function_name,args,required_capabilities=()):
        required=set(required_capabilities); profiles=[p for p in self.profiles.values() if p.enabled and required.issubset(p.capabilities)]; profiles.sort(key=lambda p:(-p.reliability,p.expected_latency_ms,p.estimated_cost_usd,p.model_id)); attempts=[]; selected=None; output=None
        for i,p in enumerate(profiles,1):
            fn=self.invokers.get(p.model_id)
            if fn is None: attempts.append(AttemptReceipt(i,p.model_id,p.provider,AttemptStatus.SKIPPED,digest(args),'',0,0,False,('MODEL_INVOKER_UNBOUND',),'MODEL_INVOKER_UNBOUND')); continue
            started=time.perf_counter()
            try:
                raw=fn(function_name,args); recorded=bool(isinstance(raw,Mapping) and raw.get('__recorded__')); clean={k:v for k,v in raw.items() if k!='__recorded__'} if isinstance(raw,Mapping) else raw; defects=self.validator.validate(function_name,clean); status=AttemptStatus.PASS if not defects else AttemptStatus.VALIDATION_ERROR
                attempts.append(AttemptReceipt(i,p.model_id,p.provider,status,digest(args),digest(clean),(time.perf_counter()-started)*1000,p.estimated_cost_usd,recorded,defects,None if status==AttemptStatus.PASS else 'VALIDATION_ERROR'))
                if status==AttemptStatus.PASS: selected=p.model_id; output=clean; break
            except TimeoutError as exc: attempts.append(AttemptReceipt(i,p.model_id,p.provider,AttemptStatus.TIMEOUT,digest(args),'',(time.perf_counter()-started)*1000,p.estimated_cost_usd,False,(),str(exc)))
            except Exception as exc: attempts.append(AttemptReceipt(i,p.model_id,p.provider,AttemptStatus.FAIL,digest(args),'',(time.perf_counter()-started)*1000,p.estimated_cost_usd,False,(),f'{type(exc).__name__}:{exc}'))
        status=AttemptStatus.PASS if selected else attempts[-1].status if attempts else AttemptStatus.FAIL
        return FallbackReceipt(function_name,selected,tuple(attempts),status,sum(a.estimated_cost_usd for a in attempts),sum(a.latency_ms for a in attempts),digest(output) if output is not None else ''),output

class CoalitionScheduler:
    def schedule(self,proposals:Sequence[OrganProposal],frames:Sequence[Mapping[str,Any]]):
        completed=set(); held=set(); waves=[]; observed=set(); defects=set(); previous_fields=set(); final_seen=False
        for seq,frame in enumerate(frames,1):
            fields=set(frame); frame_defects=[]
            if not previous_fields.issubset(fields): frame_defects.append('FIELD_REGRESSION')
            if final_seen: frame_defects.append('FRAME_AFTER_FINAL')
            if frame.get('authority_effect')!='NONE': frame_defects.append('AUTHORITY_EFFECT_NOT_NONE')
            if frame.get('generated_manifestation') is not True: frame_defects.append('GENERATED_MANIFESTATION_NOT_MARKED')
            final=bool(frame.get('final')); final_seen|=final; previous_fields=fields; observed|=fields; defects.update(frame_defects)
            ready=[p for p in proposals if p.organ_id not in completed and p.dependencies.issubset(completed) and p.required_fields.issubset(observed) and p.activation>0]; ready.sort(key=lambda p:(-p.priority,-p.activation,p.organ_id)); selected=[]; locks=set()
            for p in ready:
                if p.locks.isdisjoint(locks):selected.append(p);locks.update(p.locks)
                else:held.add(p.organ_id)
            completed.update(p.organ_id for p in selected); state=CoalitionState.RETURNING if final else CoalitionState.ACTIVE if selected else CoalitionState.FORMING; waves.append(CoalitionWave(seq,tuple(p.organ_id for p in selected),tuple(sorted(observed)),state,tuple(frame_defects)))
        if not final_seen:defects.add('FINAL_FRAME_MISSING')
        return_capable=any(p.organ_id in completed and p.return_capable for p in proposals)
        if not return_capable:defects.add('RETURN_ORGAN_NOT_COMPLETED')
        complete=final_seen and return_capable; state=CoalitionState.DISSOLVED if complete and not defects else CoalitionState.HOLD
        return CoalitionReceipt(tuple(waves),tuple(sorted(completed)),tuple(sorted(held)),state,complete,tuple(sorted(defects)))

class V7Runtime:
    def __init__(self,baml_root,recordings_root): self.revisions=RevisionJournal(); self.revisions.scan(baml_root); self.fixtures=FixtureStore(recordings_root); self.validator=BoundaryValidator()
    def validate(self):
        recordings=[]
        for name in self.fixtures.list():
            try:f=self.fixtures.load(name);recordings.append({'filename':name,'status':'PASS','digest':f.digest,'external_witness':f.external_witness})
            except Exception as exc:recordings.append({'filename':name,'status':'FAIL','error':str(exc)})
        return {'revision_journal':'PASS' if self.revisions.verify() else 'FAIL','recordings':recordings,'production_status':'HOLD','authority_effect':'NONE'}
