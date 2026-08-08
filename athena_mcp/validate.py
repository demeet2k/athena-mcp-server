from __future__ import annotations

import json
import re


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

def _canonical(v):
    try:return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    except (TypeError,ValueError):return repr(v)

def validate(schema,value,path='$'):
    if not isinstance(schema,dict): return

    # Composition/value constraints are enforced before structural descent so a
    # schema declaration cannot silently become documentation-only.
    if 'const' in schema and value != schema['const']:
        raise ValueError(f'{path}: expected constant {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: expected one of {schema["enum"]!r}')
    if 'oneOf' in schema:
        matches=0; errors=[]
        for branch in schema['oneOf']:
            try: validate(branch,value,path); matches+=1
            except ValueError as exc: errors.append(str(exc))
        if matches != 1: raise ValueError(f'{path}: expected exactly one oneOf match, got {matches}')
    if 'anyOf' in schema:
        matched=False
        for branch in schema['anyOf']:
            try: validate(branch,value,path); matched=True; break
            except ValueError: pass
        if not matched: raise ValueError(f'{path}: did not match anyOf')

    if 'type' in schema and not any(_ok(value,t) for t in _types(schema['type'])):
        raise ValueError(f'{path}: expected {schema["type"]}')

    if isinstance(value,dict):
        for k in schema.get('required',[]):
            if k not in value: raise ValueError(f'{path}: missing required field {k}')
        if 'minProperties' in schema and len(value)<schema['minProperties']: raise ValueError(f'{path}: too few properties')
        if 'maxProperties' in schema and len(value)>schema['maxProperties']: raise ValueError(f'{path}: too many properties')
        props=schema.get('properties',{})
        if schema.get('additionalProperties') is False:
            extra=set(value)-set(props)
            if extra: raise ValueError(f'{path}: unexpected fields {sorted(extra)}')
        for k,v in value.items():
            if k in props: validate(props[k],v,f'{path}.{k}')

    if isinstance(value,list):
        if len(value)<schema.get('minItems',0): raise ValueError(f'{path}: too few items')
        if 'maxItems' in schema and len(value)>schema['maxItems']: raise ValueError(f'{path}: too many items')
        if schema.get('uniqueItems'):
            seen=set()
            for i,x in enumerate(value):
                key=_canonical(x)
                if key in seen: raise ValueError(f'{path}[{i}]: duplicate item')
                seen.add(key)
        if 'items' in schema:
            for i,x in enumerate(value): validate(schema['items'],x,f'{path}[{i}]')

    if isinstance(value,str):
        if 'minLength' in schema and len(value)<schema['minLength']: raise ValueError(f'{path}: shorter than minLength')
        if 'maxLength' in schema and len(value)>schema['maxLength']: raise ValueError(f'{path}: longer than maxLength')
        if 'pattern' in schema and re.search(schema['pattern'],value) is None: raise ValueError(f'{path}: does not match pattern')

    if isinstance(value,(int,float)) and not isinstance(value,bool):
        if 'minimum' in schema and value<schema['minimum']: raise ValueError(f'{path}: below minimum')
        if 'maximum' in schema and value>schema['maximum']: raise ValueError(f'{path}: above maximum')
        if 'exclusiveMinimum' in schema and value<=schema['exclusiveMinimum']: raise ValueError(f'{path}: not above exclusiveMinimum')
        if 'exclusiveMaximum' in schema and value>=schema['exclusiveMaximum']: raise ValueError(f'{path}: not below exclusiveMaximum')
