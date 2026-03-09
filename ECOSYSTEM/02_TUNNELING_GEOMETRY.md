# TUNNELING GEOMETRY - ELEMENTAL TRANSPORT GRAPH

## 1. Axes and Oppositions

Definition 1.1 (Primary Axes).
The state space uses three orthogonal axes with elemental oppositions:
- X axis: Earth (-X) vs Air (+X)
- Y axis: Water (-Y) vs Fire (+Y)
- Z axis: Void (-Z) vs Aether (+Z)

Definition 1.2 (Opposition Meaning).
- Earth vs Air: Structure vs Possibility
- Water vs Fire: Flow vs Compression
- Void vs Aether: Nullity vs Unity

## 2. Six-Face State Space

Definition 2.1 (Faces).
The 6 faces are {Earth, Air, Water, Fire, Void, Aether}.

Definition 2.2 (Adjacency).
Each face is adjacent to four others and not adjacent to its opposite.

Adjacency set example:
- Earth adjacent to Water, Fire, Void, Aether.
- Air adjacent to Water, Fire, Void, Aether.
- Water adjacent to Earth, Air, Void, Aether.
- Fire adjacent to Earth, Air, Void, Aether.
- Aether adjacent to Earth, Air, Water, Fire.
- Void adjacent to Earth, Air, Water, Fire.

## 3. Transport Graph

Definition 3.1 (Transport Graph).
Let G = (V, E) where V are the 6 faces and E are the 12 adjacency edges.
Opposite faces have no edges.

## 4. Anti-Tunnel Rules

Definition 4.1 (Anti-Tunnel).
A direct transition between opposites is forbidden. All opposite transitions require at least two steps.

Table 4.2 (Opposites and Min Steps).
- Earth <-> Air: min steps = 2
- Water <-> Fire: min steps = 2
- Void <-> Aether: min steps = 2

Valid midpoints for any opposite pair are the four non-opposites.

## 5. Tunneling Definition

Definition 5.1 (Tunnel).
A tunnel is a length-2 path between opposites via any valid midpoint.
Example:
- Earth -> Water -> Air
- Water -> Aether -> Fire

Definition 5.2 (Tunnel Family).
Each opposition admits exactly 4 distinct midpoints, hence 4 tunnel families.

## 6. Operational Consequences

- Opposites never touch directly.
- Hybrid states are the transport midpoints.
- Transport constraints are structural invariants and must be obeyed by any routing or hybridization algorithm.

## 7. Compatibility
This geometry is the foundation for both hybridization selection and agent transport protocols.
