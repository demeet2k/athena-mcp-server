from __future__ import annotations
import json, math

DERIVATIONAL_MODES={"DERIVATION","PROJECTION","EMBEDDING","ISOMORPHISM","APPROXIMATION"}
ALL_MODES=DERIVATIONAL_MODES|{"LOOKUP"}

class TransformProgramError(ValueError): pass

def _get(value,path):
    cur=value
    for key in path:
        if isinstance(cur,dict): cur=cur[key]
        elif isinstance(cur,list) and isinstance(key,int): cur=cur[key]
        else: raise TransformProgramError(f"cannot traverse {key!r} in {type(cur).__name__}")
    return cur

def evaluate(expr,x,depth=0):
    if depth>32: raise TransformProgramError("program nesting limit exceeded")
    if not isinstance(expr,dict) or 'op' not in expr: raise TransformProgramError("expression must be an object with op")
    op=expr['op']
    if op=='identity': return x
    if op=='const': return expr.get('value')
    if op=='get': return _get(x,expr.get('path',[]))
    if op=='object': return {k:evaluate(v,x,depth+1) for k,v in expr.get('fields',{}).items()}
    if op=='array': return [evaluate(v,x,depth+1) for v in expr.get('items',[])]
    if op=='coalesce':
        for v in expr.get('args',[]):
            try:
                y=evaluate(v,x,depth+1)
                if y is not None:return y
            except (KeyError,IndexError,TransformProgramError): pass
        return None
    if op in {'add','sub','mul','div','mod','pow','min','max'}:
        args=[evaluate(v,x,depth+1) for v in expr.get('args',[])]
        if not args: raise TransformProgramError(f"{op} requires args")
        if op=='add': return sum(args)
        if op=='sub':
            if len(args)!=2:raise TransformProgramError('sub requires 2 args')
            return args[0]-args[1]
        if op=='mul':
            out=1
            for a in args:out*=a
            return out
        if op=='div':
            if len(args)!=2:raise TransformProgramError('div requires 2 args')
            return args[0]/args[1]
        if op=='mod':
            if len(args)!=2:raise TransformProgramError('mod requires 2 args')
            return args[0]%args[1]
        if op=='pow':
            if len(args)!=2:raise TransformProgramError('pow requires 2 args')
            return args[0]**args[1]
        return min(args) if op=='min' else max(args)
    if op in {'floor','ceil','round','abs'}:
        v=evaluate(expr['arg'],x,depth+1)
        return {'floor':math.floor,'ceil':math.ceil,'round':round,'abs':abs}[op](v)
    if op=='concat': return ''.join(str(evaluate(v,x,depth+1)) for v in expr.get('args',[]))
    raise TransformProgramError(f"unsupported op {op}")

def validate_program(program):
    # Evaluation against a sentinel catches syntax/shape errors only for programs not requiring real keys.
    if not isinstance(program,dict) or 'op' not in program: raise TransformProgramError('program must contain op')
    return True

def _numeric_leaves(v,prefix=()):
    out={}
    if isinstance(v,(int,float)) and not isinstance(v,bool):out[prefix]=float(v)
    elif isinstance(v,dict):
        for k,x in v.items():out.update(_numeric_leaves(x,prefix+(str(k),)))
    elif isinstance(v,list):
        for i,x in enumerate(v):out.update(_numeric_leaves(x,prefix+(i,)))
    return out

def compare(actual,target,metric=None):
    metric=metric or {'type':'EXACT'}; typ=str(metric.get('type','EXACT')).upper()
    if typ=='EXACT':
        same=json.dumps(actual,sort_keys=True,separators=(',',':'),ensure_ascii=False)==json.dumps(target,sort_keys=True,separators=(',',':'),ensure_ascii=False)
        return {'type':'EXACT','metric':0.0 if same else 1.0,'equal':same,'defect':None if same else {'actual':actual,'target':target}}
    if typ=='NUMERIC_L2':
        a=_numeric_leaves(actual);b=_numeric_leaves(target);keys=sorted(set(a)&set(b),key=str)
        if not keys:return {'type':'NUMERIC_L2','metric':None,'status':'N/A_NO_COMMON_NUMERIC_FIELDS'}
        sq=sum((a[k]-b[k])**2 for k in keys)
        return {'type':'NUMERIC_L2','metric':math.sqrt(sq),'fields':[list(k) for k in keys]}
    if typ=='FIELD_MISMATCH':
        if not isinstance(actual,dict) or not isinstance(target,dict):return {'type':'FIELD_MISMATCH','metric':None,'status':'N/A_NON_OBJECT'}
        keys=sorted(set(actual)|set(target));bad=[k for k in keys if actual.get(k)!=target.get(k)]
        return {'type':'FIELD_MISMATCH','metric':len(bad)/len(keys) if keys else 0.0,'mismatched':bad}
    raise TransformProgramError(f"unsupported metric {typ}")
