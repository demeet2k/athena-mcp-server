from __future__ import annotations
def _types(t): return t if isinstance(t,list) else [t]
def _ok(v,t):
    if t=='null': return v is None
    if t=='object': return isinstance(v,dict)
    if t=='array': return isinstance(v,list)
    if t=='string': return isinstance(v,str)
    if t=='integer': return isinstance(v,int) and not isinstance(v,bool)
    if t=='number': return isinstance(v,(int,float)) and not isinstance(v,bool)
    if t=='boolean': return isinstance(v,bool)
    return True
def validate(schema,value,path='$'):
    if not isinstance(schema,dict): return
    if 'type' in schema and not any(_ok(value,t) for t in _types(schema['type'])): raise ValueError(f'{path}: expected {schema["type"]}')
    if isinstance(value,dict):
        for k in schema.get('required',[]):
            if k not in value: raise ValueError(f'{path}: missing required field {k}')
        props=schema.get('properties',{})
        if schema.get('additionalProperties') is False:
            extra=set(value)-set(props)
            if extra: raise ValueError(f'{path}: unexpected fields {sorted(extra)}')
        for k,v in value.items():
            if k in props: validate(props[k],v,f'{path}.{k}')
    if isinstance(value,list):
        if len(value)<schema.get('minItems',0): raise ValueError(f'{path}: too few items')
        if 'maxItems' in schema and len(value)>schema['maxItems']: raise ValueError(f'{path}: too many items')
        if 'items' in schema:
            for i,x in enumerate(value): validate(schema['items'],x,f'{path}[{i}]')
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        if 'minimum' in schema and value<schema['minimum']: raise ValueError(f'{path}: below minimum')
        if 'maximum' in schema and value>schema['maximum']: raise ValueError(f'{path}: above maximum')
