# Glossary

**AQM kernel**
: A deterministic artifact system where objects are canonically serialized, content‑hashed, and stored in a Merkle store, enabling replay verification.

**Tile**
: The fundamental AQM unit: seed + payload + obligations/certs + ledger anchors + explicit dependencies.

**Merkle store**
: Content‑addressed store keyed by hash; supports dependency closure and replay verification.

**Ledger**
: Append‑only deterministic event list (no wall‑clock timestamps).

**Lens**
: A scoring module returning a log score and diagnostics for a candidate Theta.

**Theta (Θ)**
: A parameter record. In Q‑PHI, Θ is Planet Nine orbital + physical parameters (`PlanetNineTheta`).

**Extreme TNO**
: A trans‑Neptunian object that meets some “extreme” selection (e.g., large semimajor axis and perihelion distance). The selection rule strongly affects inference.

**varpi (ϖ)**
: Longitude of perihelion, computed as Ω + ω.

**RA/Dec**
: Equatorial right ascension and declination.

**Posterior**
: The weighted set of elite samples returned by Q‑PHI.

**Containment radius**
: The angular radius around the posterior mean direction containing a given fraction of posterior weight.
