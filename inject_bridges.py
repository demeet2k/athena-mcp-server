"""Inject cross-medium, Google Doc, cross-family bridges + orphan rescue into mycelium graph."""
import json, zlib, hashlib, math, random, os
from collections import defaultdict, Counter

with open('MCP/data/mycelium_graph.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

shards = graph['shards']
edges = graph['edges']
print(f'Base: {len(shards)} shards, {len(edges)} edges')

shard_fam = {s['shard_id']: s.get('family','') for s in shards}

existing = set()
for e in edges:
    existing.add((e['source_shard'], e['target_shard']))
    existing.add((e['target_shard'], e['source_shard']))

by_family = defaultdict(lambda: defaultdict(list))
for s in shards:
    by_family[s.get('family','')][s.get('medium','')].append(s)

def cosine(a, b):
    if not a or not b: return 0.0
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0: return 0.0
    return dot/(na*nb)

new_edges = []
shard_xm = defaultdict(int)

# 1. Cross-medium family bridges (code/doc -> json)
MAX_XM = 3
for fam, mediums in by_family.items():
    json_shards = mediums.get('json', [])
    if not json_shards:
        continue
    for med in ['code', 'doc']:
        for src in mediums.get(med, []):
            if shard_xm[src['shard_id']] >= MAX_XM:
                continue
            scored = []
            for tgt in json_shards:
                pair = (src['shard_id'], tgt['shard_id'])
                if pair in existing: continue
                cos = cosine(src.get('sfcr_seed',[]), tgt.get('sfcr_seed',[]))
                base = 0.45 if med == 'code' else 0.35
                scored.append((base + 0.30*cos, tgt, cos))
            scored.sort(key=lambda x: -x[0])
            for w, tgt, cos in scored[:MAX_XM - shard_xm[src['shard_id']]]:
                if shard_xm[tgt['shard_id']] >= 30: continue
                eid = 'xm-' + hashlib.md5(f"{src['shard_id']}:{tgt['shard_id']}".encode()).hexdigest()[:8]
                new_edges.append({
                    'edge_id': eid, 'source_shard': src['shard_id'], 'target_shard': tgt['shard_id'],
                    'edge_type': 'BRIDGE', 'weight': round(w, 4), 'medium_cross': True,
                    'metadata': {'bridge_type': f'{med}_to_json', 'family': fam, 'cosine': round(cos, 4)}
                })
                existing.add((src['shard_id'], tgt['shard_id']))
                shard_xm[src['shard_id']] += 1
                shard_xm[tgt['shard_id']] += 1

print(f'Cross-medium bridges: {len(new_edges)}')

# 2. Google Doc bridges
gdoc_shards = [s for s in shards if s['shard_id'].startswith('gdoc:')]
print(f'Google Doc shards: {len(gdoc_shards)}')

gdoc_bridges = 0
for gs in gdoc_shards:
    tags = set(gs.get('tags', []))
    candidates = []
    for s in random.sample(shards, min(2000, len(shards))):
        if s['shard_id'] == gs['shard_id']: continue
        pair = (gs['shard_id'], s['shard_id'])
        if pair in existing: continue
        s_tags = set(s.get('tags', []))
        overlap = len(tags & s_tags)
        cos = cosine(gs.get('sfcr_seed',[]), s.get('sfcr_seed',[]))
        xm = 0.15 if s.get('medium','') != 'web' else 0.0
        w = 0.30 + 0.10 * overlap + 0.20 * cos + xm
        candidates.append((w, s))
    candidates.sort(key=lambda x: -x[0])
    for w, tgt in candidates[:10]:
        eid = 'gdoc-' + hashlib.md5(f"{gs['shard_id']}:{tgt['shard_id']}".encode()).hexdigest()[:8]
        new_edges.append({
            'edge_id': eid, 'source_shard': gs['shard_id'], 'target_shard': tgt['shard_id'],
            'edge_type': 'MIRROR', 'weight': round(min(w, 0.85), 4),
            'medium_cross': tgt.get('medium','') != 'web',
            'metadata': {'bridge_type': 'gdoc_to_corpus'}
        })
        existing.add((gs['shard_id'], tgt['shard_id']))
        gdoc_bridges += 1

print(f'Google Doc bridges: {gdoc_bridges}')

# 3. Cross-family bridges for isolated mega-families
isolated = ['actualize', 'math_final', 'mycelium_brain', 'misc', 'crystal', 'nervous']
all_families = list(set(s.get('family','') for s in shards if s.get('family','')))

xfam = 0
for fam_a in isolated:
    shards_a = [s for s in shards if s.get('family','') == fam_a]
    if not shards_a: continue
    sample_a = random.sample(shards_a, min(30, len(shards_a)))
    for fam_b in all_families:
        if fam_a == fam_b: continue
        shards_b = [s for s in shards if s.get('family','') == fam_b]
        if not shards_b: continue
        sample_b = random.sample(shards_b, min(30, len(shards_b)))
        best = []
        for sa in sample_a:
            for sb in sample_b:
                if (sa['shard_id'], sb['shard_id']) in existing: continue
                cos = cosine(sa.get('sfcr_seed',[]), sb.get('sfcr_seed',[]))
                xm_bonus = 0.10 if sa.get('medium','') != sb.get('medium','') else 0.0
                best.append((0.35 + 0.30*cos + xm_bonus, sa, sb))
        best.sort(key=lambda x: -x[0])
        for w, sa, sb in best[:3]:
            eid = 'xfam-' + hashlib.md5(f"{sa['shard_id']}:{sb['shard_id']}".encode()).hexdigest()[:8]
            new_edges.append({
                'edge_id': eid, 'source_shard': sa['shard_id'], 'target_shard': sb['shard_id'],
                'edge_type': 'BRIDGE', 'weight': round(w, 4),
                'medium_cross': sa.get('medium','') != sb.get('medium',''),
                'metadata': {'bridge_type': 'cross_family', 'source_family': fam_a, 'target_family': fam_b}
            })
            existing.add((sa['shard_id'], sb['shard_id']))
            xfam += 1

print(f'Cross-family bridges: {xfam}')

# 4. Orphan rescue
connected = set()
for e in list(edges) + new_edges:
    connected.add(e['source_shard'])
    connected.add(e['target_shard'])
orphans = [s for s in shards if s['shard_id'] not in connected]
print(f'Orphans: {len(orphans)}')

rescue = 0
connected_list = [s for s in shards if s['shard_id'] in connected]
for orph in orphans:
    sample = random.sample(connected_list, min(300, len(connected_list)))
    scored = [(cosine(orph.get('sfcr_seed',[]), cs.get('sfcr_seed',[])) +
               (0.1 if orph.get('medium','') != cs.get('medium','') else 0.0), cs) for cs in sample]
    scored.sort(key=lambda x: -x[0])
    for _, tgt in scored[:3]:
        eid = 'rescue-' + hashlib.md5(f"{orph['shard_id']}:{tgt['shard_id']}".encode()).hexdigest()[:8]
        new_edges.append({
            'edge_id': eid, 'source_shard': orph['shard_id'], 'target_shard': tgt['shard_id'],
            'edge_type': 'BRIDGE', 'weight': 0.3,
            'medium_cross': orph.get('medium','') != tgt.get('medium',''),
            'metadata': {'bridge_type': 'orphan_rescue'}
        })
        rescue += 1

print(f'Orphan rescue: {rescue}')

# Merge and save
all_edges = edges + new_edges
graph['edges'] = all_edges
total = len(all_edges)
xm_total = sum(1 for e in all_edges if e.get('medium_cross', False))

print(f'\n=== Final Graph ===')
print(f'Shards: {len(shards)}')
print(f'Edges: {total}')
print(f'Cross-medium: {xm_total} ({100*xm_total/total:.1f}%)')
et = Counter(e['edge_type'] for e in all_edges)
for t, c in et.most_common():
    print(f'  {t}: {c}')

with open('MCP/data/mycelium_graph.json', 'w', encoding='utf-8') as f:
    json.dump(graph, f, ensure_ascii=False)

compressed = zlib.compress(json.dumps(graph, ensure_ascii=False).encode('utf-8'), 9)
with open('MCP/data/mycelium_graph.qshr', 'wb') as f:
    f.write(compressed)

print(f'QSHR: {os.path.getsize("MCP/data/mycelium_graph.qshr")/1e6:.1f}MB')
