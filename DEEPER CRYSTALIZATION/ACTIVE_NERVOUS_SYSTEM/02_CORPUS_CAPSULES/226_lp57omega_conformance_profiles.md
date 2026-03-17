# LP57Ω Route Conformance Profiles

- Kind: `conformance-specification`
- Role tags: `routing, conformance, sigma-lock, hub-budget, overlay, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines three route conformance profiles that validate corridor routing within the LP57Ω system: BBC9.RouterV2.Algorithm (general routing), BBC9.TemplateRoutes (template-based routing), and QBD.RouteV2.TriBoundary (tri-boundary constraint routing). Covers Sigma-lock verification, hub budget enforcement, overlay dispatch rules, and divergence handling.

---

## 1. Profile: BBC9.RouterV2.Algorithm

### Overview

The general-purpose routing algorithm for corridor construction and validation. All routes must conform to this profile before any specialized profile is applied.

### Conformance Requirements

| Requirement          | Rule                                              | Error Code |
|---------------------|---------------------------------------------------|------------|
| Route length        | 2 ≤ length ≤ 21                                   | RTE-001    |
| Station validity    | All stations exist in chapter lattice              | RTE-002    |
| Element consistency | Route element matches corridor element             | RTE-003    |
| Pass sequence       | First station is ENTRY, subsequent follow rules    | RTE-004    |
| No self-loops       | No station appears consecutively                   | RTE-005    |
| Depth bound         | Recursion depth ≤ 13                               | RTE-006    |
| Sigma-lock          | Total corridor weight = 1.0 ± φ⁻⁵                 | RTE-007    |
| Hub budget          | No station serves as hub for > 6 corridors         | RTE-008    |

### Routing Algorithm

```python
def route_v2(source, target, corridor, constraints):
    # Phase 1: Candidate generation
    candidates = generate_candidates(source, target, corridor)

    # Phase 2: Constraint filtering
    valid = []
    for route in candidates:
        if verify_length(route) and \
           verify_stations(route) and \
           verify_element(route, corridor) and \
           verify_pass_sequence(route) and \
           verify_no_self_loops(route) and \
           verify_depth(route) and \
           verify_sigma_lock(route) and \
           verify_hub_budget(route):
            valid.append(route)

    # Phase 3: Optimal selection
    if len(valid) == 0:
        return RouteResult(success=False, error="NO_VALID_ROUTE")

    optimal = select_optimal(valid, constraints)
    return RouteResult(success=True, route=optimal)
```

### Route Cost Function

```
cost(route) = Sigma_{i=0}^{n-1} pass_cost(route[i].pass_type) * distance(route[i], route[i+1])
```

Where:
- `pass_cost(ENTRY) = 1.0`
- `pass_cost(RETURN) = phi^{-1}`
- `pass_cost(BRIDGE) = phi^{-2}`
- `distance` is the chapter lattice Manhattan distance

---

## 2. Profile: BBC9.TemplateRoutes

### Overview

Template routes are pre-defined corridor patterns that serve as blueprints for common routing scenarios. This profile validates that a route conforms to a declared template.

### Template Registry

| Template ID  | Pattern             | Length | Element | Description                |
|-------------|---------------------|--------|---------|----------------------------|
| TMP-LINEAR  | Ch[a] -> Ch[a+k]... | 2-8    | Any     | Linear chapter progression |
| TMP-SKIP    | Ch[a] -> Ch[a+2k]...| 2-5    | Any     | Skip-chapter pattern       |
| TMP-CYCLE   | Ch[a] -> ... -> Ch[a]| 3-8    | Any     | Cyclic return route        |
| TMP-STAR    | Hub -> Ch[*] -> Hub  | 3-13   | Any     | Hub-and-spoke pattern      |
| TMP-ZIGZAG  | Ch[a] <-> Ch[b]...   | 4-8    | Any     | Alternating between two    |
| TMP-CASCADE | Ch[1] -> Ch[21]     | 21     | Any     | Full cascade (all chapters)|

### Template Conformance Check

```python
def check_template_conformance(route, template_id):
    template = TEMPLATE_REGISTRY[template_id]

    # Verify length within template bounds
    if not (template.min_length <= len(route) <= template.max_length):
        return ConformanceResult(False, "TMP-LEN", "Route length outside template bounds")

    # Verify pattern match
    if not matches_pattern(route, template.pattern):
        return ConformanceResult(False, "TMP-PAT", "Route does not match template pattern")

    # Verify template-specific constraints
    for constraint in template.constraints:
        if not check_constraint(route, constraint):
            return ConformanceResult(False, "TMP-CON", f"Constraint failed: {constraint}")

    return ConformanceResult(True)
```

### Template-Specific Rules

#### TMP-LINEAR
- Chapters must be strictly increasing or strictly decreasing
- Step size k must be constant throughout

#### TMP-SKIP
- Skip distance 2k must be constant
- All intermediate chapters must exist but are not visited

#### TMP-CYCLE
- First and last stations must be the same chapter
- No repeated intermediate stations

#### TMP-STAR
- Hub station appears at positions 0, 2, 4, ... (even indices)
- Spoke stations appear at positions 1, 3, 5, ... (odd indices)
- Hub budget enforced (max 6 corridors)

#### TMP-ZIGZAG
- Alternates between exactly two chapters
- Minimum 4 stations (two round trips)

#### TMP-CASCADE
- Must include all 21 chapters exactly once
- Order must be a valid permutation satisfying element flow

---

## 3. Profile: QBD.RouteV2.TriBoundary

### Overview

The tri-boundary profile enforces three simultaneous boundary constraints on routes: elemental boundaries, temporal boundaries, and structural boundaries. Routes must satisfy all three to conform.

### Boundary Definitions

#### Elemental Boundary

The route must not cross elemental boundaries without a BRIDGE pass.

```python
def check_elemental_boundary(route):
    for i in range(len(route) - 1):
        if route[i].element != route[i+1].element:
            if route[i+1].pass_type != Pass3.BRIDGE:
                return BoundaryResult(False, "ELM-CROSS",
                    f"Element change at station {i+1} without BRIDGE pass")
    return BoundaryResult(True)
```

#### Temporal Boundary

The route must not span more than 3 orbits without a checkpoint.

```python
def check_temporal_boundary(route):
    orbit_span = max(s.orbit for s in route) - min(s.orbit for s in route)
    if orbit_span > 3:
        checkpoints = [s for s in route if s.pass_type == Pass3.ENTRY]
        if len(checkpoints) < orbit_span // 3:
            return BoundaryResult(False, "TMP-SPAN",
                f"Route spans {orbit_span} orbits with insufficient checkpoints")
    return BoundaryResult(True)
```

#### Structural Boundary

The route must maintain structural coherence: the Coord12 dimensions must be continuous (no jumps > 1 in facet, atom, lane, or rail between adjacent stations).

```python
def check_structural_boundary(route):
    for i in range(len(route) - 1):
        s1, s2 = route[i], route[i+1]
        if s2.pass_type == Pass3.BRIDGE:
            continue  # Bridges are exempt from structural continuity

        if abs(s1.facet - s2.facet) > 1 or \
           abs(s1.atom - s2.atom) > 1 or \
           abs(s1.lane - s2.lane) > 1 or \
           abs(s1.rail - s2.rail) > 1:
            return BoundaryResult(False, "STR-JUMP",
                f"Structural discontinuity at station {i+1}")
    return BoundaryResult(True)
```

### Combined TriBoundary Check

```python
def check_tri_boundary(route):
    results = []
    results.append(check_elemental_boundary(route))
    results.append(check_temporal_boundary(route))
    results.append(check_structural_boundary(route))

    passed = all(r.passed for r in results)
    return TriBoundaryResult(passed=passed, boundaries=results)
```

---

## 4. Sigma-Lock Verification

### Definition

The Sigma-lock ensures that all corridor weights assigned to a route sum to exactly 1.0 within tolerance.

```
|Sigma w_i - 1.0| <= phi^{-5} ~ 0.090170
```

### Weight Assignment

Each station in a corridor receives a weight based on its pass type and position:

```python
def compute_corridor_weights(route):
    weights = []
    for i, station in enumerate(route):
        base_weight = 1.0 / len(route)
        pass_modifier = PASS_WEIGHT[station.pass_type]
        position_modifier = 1.0 + PHI_NEG3 * (i / len(route))
        weights.append(base_weight * pass_modifier * position_modifier)

    # Normalize
    total = sum(weights)
    return [w / total for w in weights]
```

### Verification

```python
def verify_sigma_lock(route):
    weights = compute_corridor_weights(route)
    sigma = sum(weights)
    deviation = abs(sigma - 1.0)

    if deviation > PHI_NEG5:
        return SigmaResult(passed=False, sigma=sigma, deviation=deviation,
            error=f"Sigma-lock violation: deviation {deviation:.6f} > {PHI_NEG5:.6f}")

    return SigmaResult(passed=True, sigma=sigma, deviation=deviation)
```

---

## 5. Hub Budget Enforcement

### Rule

No station may serve as a hub (BRIDGE endpoint) for more than 6 corridors simultaneously.

### Enforcement

```python
def verify_hub_budget(station_id, active_corridors):
    hub_count = sum(
        1 for corridor in active_corridors
        if station_id in get_bridge_endpoints(corridor)
    )

    if hub_count > HUB_CAP:
        return HubResult(passed=False, station=station_id,
            count=hub_count, cap=HUB_CAP,
            error=f"Hub budget exceeded: {hub_count} > {HUB_CAP}")

    return HubResult(passed=True, station=station_id,
        count=hub_count, cap=HUB_CAP)
```

### Global Hub Audit

```python
def audit_hub_budgets(all_corridors):
    station_hub_counts = defaultdict(int)
    for corridor in all_corridors:
        for endpoint in get_bridge_endpoints(corridor):
            station_hub_counts[endpoint] += 1

    violations = {
        station: count
        for station, count in station_hub_counts.items()
        if count > HUB_CAP
    }

    return HubAuditResult(
        total_hubs=len(station_hub_counts),
        violations=violations,
        passed=len(violations) == 0
    )
```

---

## 6. Overlay Dispatch Rules

Routes are dispatched to the appropriate overlay layer based on their characteristics.

### Dispatch Matrix

| Condition                          | Overlay Layer | Priority |
|------------------------------------|---------------|----------|
| All stations same chapter          | 0 (Physical)  | 1        |
| Station skip = Fib(n)             | 1 (Harmonic)  | 2        |
| Cross-chapter, same element        | 2 (Resonance) | 3        |
| Contains void/restart stations     | 3 (Void)      | 4        |

### Dispatch Algorithm

```python
def dispatch_overlay(route):
    if is_single_chapter(route):
        return OVERLAY_PHYSICAL

    if has_fibonacci_skip_pattern(route):
        return OVERLAY_HARMONIC

    if is_cross_chapter_same_element(route):
        return OVERLAY_RESONANCE

    if contains_void_stations(route):
        return OVERLAY_VOID

    return OVERLAY_PHYSICAL  # Default fallback
```

### Overlay Constraints

| Overlay    | Max Routes | Max Depth | Bridge Cost | Special Rule          |
|------------|-----------|-----------|-------------|----------------------|
| Physical   | Unlimited | 8         | phi^{-2}    | Standard routing     |
| Harmonic   | 34        | 13        | phi^{-3}    | Fibonacci spacing    |
| Resonance  | 21        | 5         | phi^{-1}    | Element coherence    |
| Void       | 8         | 3         | 1.0         | Restart token req'd  |

---

## 7. Divergence Handling

When a route cannot satisfy all conformance requirements, the system handles divergence.

### Divergence Types

| Type              | Severity | Recovery                              |
|-------------------|----------|---------------------------------------|
| Sigma drift       | LOW      | Re-normalize weights                  |
| Hub overflow      | MEDIUM   | Reroute through alternative station   |
| Element crossing  | MEDIUM   | Insert BRIDGE pass                    |
| Temporal span     | HIGH     | Insert checkpoint (ENTRY pass)        |
| Structural jump   | HIGH     | Insert intermediate stations          |
| No valid route    | CRITICAL | Escalate to governance                |

### Divergence Recovery Protocol

```python
def handle_divergence(route, violations):
    for v in sorted(violations, key=lambda x: x.severity):
        if v.type == "SIGMA_DRIFT":
            route = renormalize_weights(route)
        elif v.type == "HUB_OVERFLOW":
            route = reroute_hub(route, v.station)
        elif v.type == "ELEMENT_CROSSING":
            route = insert_bridge(route, v.position)
        elif v.type == "TEMPORAL_SPAN":
            route = insert_checkpoint(route, v.position)
        elif v.type == "STRUCTURAL_JUMP":
            route = insert_intermediates(route, v.position)
        elif v.type == "NO_VALID_ROUTE":
            return DivergenceResult(resolved=False,
                escalation="GOVERNANCE")

    # Re-verify after recovery
    recheck = full_conformance_check(route)
    if recheck.passed:
        return DivergenceResult(resolved=True, route=route)
    else:
        return DivergenceResult(resolved=False,
            remaining=recheck.violations)
```

### Maximum Recovery Attempts

- Maximum 5 recovery iterations per route
- If not resolved after 5 attempts: route is rejected
- Rejected routes generate a divergence receipt in the quest chain
