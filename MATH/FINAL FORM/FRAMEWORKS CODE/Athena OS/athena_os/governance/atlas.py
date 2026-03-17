"""
ATHENA OS - Governance Atlas
============================
The 256-space for governance domains.

GOVERNANCE 16 ARCHETYPES (Parent[Influence]):

FIRE CLAN (Enforcement dominates):
    Fire[Fire]   = Enforcement (Direct action)
    Fire[Water]  = Monitoring (Evidence flow)
    Fire[Air]    = Interpretation (Legal doctrine)
    Fire[Earth]  = Judiciary (Review/audit)

WATER CLAN (Evidence dominates):
    Water[Fire]  = Investigation (Active probing)
    Water[Water] = Surveillance (Continuous monitoring)
    Water[Air]   = Intelligence (Pattern analysis)
    Water[Earth] = Records (Chain of custody)

AIR CLAN (Interpretation dominates):
    Air[Fire]    = Emergency Powers (Crisis doctrine)
    Air[Water]   = Reporting (Transparency)
    Air[Air]     = Definitions (Legal interpretation)
    Air[Earth]   = Precedent (Judicial review)

EARTH CLAN (Constraint dominates):
    Earth[Fire]  = Sanctions (Penalty enforcement)
    Earth[Water] = Compliance (Ongoing audit)
    Earth[Air]   = Standards (Regulatory framework)
    Earth[Earth] = Constitution (Fundamental law)

256 FULL ADDRESS:
    T_Gov[i, j, k, ℓ] = Parent[i,j] + Flavor[k] + Refinement[ℓ]
    
Where:
    k = Flavor (what gets applied):
        ?? Fire: enforcement/action
        ?? Water: reporting/transparency
        ?? Air: interpretation/doctrine
        ?? Earth: constraint/audit
    
    ℓ = Refinement (how it manifests):
        ?? Fire: threshold/trigger
        ?? Water: time profile/feedback
        ?? Air: channel/jurisdiction
        ?? Earth: lock/precedent/appeal
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set


# =============================================================================
# GOVERNANCE ELEMENTS
# =============================================================================

class GovElement(Enum):
    """The four governance elements."""
    FIRE = 0    # Enforcement, action, penalty
    WATER = 1   # Evidence, flow, transparency
    AIR = 2     # Interpretation, doctrine, meaning
    EARTH = 3   # Constraint, audit, precedent
    
    @property
    def symbol(self) -> str:
        symbols = {
            GovElement.FIRE: "??",
            GovElement.WATER: "??",
            GovElement.AIR: "??",
            GovElement.EARTH: "??"
        }
        return symbols[self]
    
    @property
    def domain(self) -> str:
        domains = {
            GovElement.FIRE: "Enforcement",
            GovElement.WATER: "Evidence",
            GovElement.AIR: "Interpretation",
            GovElement.EARTH: "Constraint"
        }
        return domains[self]
    
    @property
    def short(self) -> str:
        return self.name[0]


# =============================================================================
# GOVERNANCE ADDRESS
# =============================================================================

@dataclass(frozen=True)
class GovAddress:
    """
    A 4-tuple address T_Gov[i, j, k, ℓ] in governance 256-space.
    
    - i: Primary element (parent)
    - j: Influence element
    - k: Flavor element (what gets applied)
    - ℓ: Refinement element (how it manifests)
    """
    
    primary: GovElement      # i
    influence: GovElement    # j
    flavor: GovElement       # k
    refinement: GovElement   # ℓ
    
    def as_tuple(self) -> Tuple[int, int, int, int]:
        """Return as integer tuple."""
        return (
            self.primary.value,
            self.influence.value,
            self.flavor.value,
            self.refinement.value
        )
    
    def to_int(self) -> int:
        """Convert to single integer 0-255."""
        i, j, k, l = self.as_tuple()
        return i * 64 + j * 16 + k * 4 + l
    
    @classmethod
    def from_int(cls, n: int) -> 'GovAddress':
        """Create from integer 0-255."""
        n = n % 256
        l = n % 4
        n //= 4
        k = n % 4
        n //= 4
        j = n % 4
        n //= 4
        i = n % 4
        return cls(
            primary=GovElement(i),
            influence=GovElement(j),
            flavor=GovElement(k),
            refinement=GovElement(l)
        )
    
    def short_string(self) -> str:
        """Short string like 'FWAE'."""
        return (
            self.primary.short +
            self.influence.short +
            self.flavor.short +
            self.refinement.short
        )
    
    def archetype_name(self) -> str:
        """Get the 16-archetype name."""
        names = {
            (GovElement.FIRE, GovElement.FIRE): "Enforcement",
            (GovElement.FIRE, GovElement.WATER): "Monitoring",
            (GovElement.FIRE, GovElement.AIR): "Interpretation",
            (GovElement.FIRE, GovElement.EARTH): "Judiciary",
            (GovElement.WATER, GovElement.FIRE): "Investigation",
            (GovElement.WATER, GovElement.WATER): "Surveillance",
            (GovElement.WATER, GovElement.AIR): "Intelligence",
            (GovElement.WATER, GovElement.EARTH): "Records",
            (GovElement.AIR, GovElement.FIRE): "Emergency",
            (GovElement.AIR, GovElement.WATER): "Reporting",
            (GovElement.AIR, GovElement.AIR): "Definitions",
            (GovElement.AIR, GovElement.EARTH): "Precedent",
            (GovElement.EARTH, GovElement.FIRE): "Sanctions",
            (GovElement.EARTH, GovElement.WATER): "Compliance",
            (GovElement.EARTH, GovElement.AIR): "Standards",
            (GovElement.EARTH, GovElement.EARTH): "Constitution",
        }
        return names.get((self.primary, self.influence), "Unknown")
    
    def flavor_meaning(self) -> str:
        """Get meaning of flavor component."""
        meanings = {
            GovElement.FIRE: "enforcement/action",
            GovElement.WATER: "reporting/transparency",
            GovElement.AIR: "interpretation/doctrine",
            GovElement.EARTH: "constraint/audit"
        }
        return meanings[self.flavor]
    
    def refinement_meaning(self) -> str:
        """Get meaning of refinement component."""
        meanings = {
            GovElement.FIRE: "threshold/trigger",
            GovElement.WATER: "time profile/feedback",
            GovElement.AIR: "channel/jurisdiction",
            GovElement.EARTH: "lock/precedent/appeal"
        }
        return meanings[self.refinement]


# =============================================================================
# GOVERNANCE ARCHETYPE CATALOG
# =============================================================================

@dataclass
class GovArchetype:
    """One of the 16 governance archetypes."""
    
    primary: GovElement
    influence: GovElement
    name: str
    description: str
    pcp_focus: str  # Which PCP component is central
    
    def address_pattern(self) -> Tuple[GovElement, GovElement]:
        return (self.primary, self.influence)


GOV_ARCHETYPE_CATALOG = [
    # Fire clan (Enforcement)
    GovArchetype(GovElement.FIRE, GovElement.FIRE, "Enforcement",
                "Direct action, penalty execution", "Proof"),
    GovArchetype(GovElement.FIRE, GovElement.WATER, "Monitoring",
                "Evidence collection, surveillance", "Evidence"),
    GovArchetype(GovElement.FIRE, GovElement.AIR, "Interpretation",
                "Legal doctrine application", "Spec"),
    GovArchetype(GovElement.FIRE, GovElement.EARTH, "Judiciary",
                "Review, appeal, audit", "Appeal"),
    
    # Water clan (Evidence)
    GovArchetype(GovElement.WATER, GovElement.FIRE, "Investigation",
                "Active probing, discovery", "Evidence"),
    GovArchetype(GovElement.WATER, GovElement.WATER, "Surveillance",
                "Continuous monitoring", "AuditLog"),
    GovArchetype(GovElement.WATER, GovElement.AIR, "Intelligence",
                "Pattern analysis, synthesis", "Decision"),
    GovArchetype(GovElement.WATER, GovElement.EARTH, "Records",
                "Chain of custody, provenance", "AuditLog"),
    
    # Air clan (Interpretation)
    GovArchetype(GovElement.AIR, GovElement.FIRE, "Emergency",
                "Crisis powers, rapid response", "Decision"),
    GovArchetype(GovElement.AIR, GovElement.WATER, "Reporting",
                "Transparency, disclosure", "Evidence"),
    GovArchetype(GovElement.AIR, GovElement.AIR, "Definitions",
                "Legal interpretation, meaning", "Spec"),
    GovArchetype(GovElement.AIR, GovElement.EARTH, "Precedent",
                "Judicial review, case law", "Proof"),
    
    # Earth clan (Constraint)
    GovArchetype(GovElement.EARTH, GovElement.FIRE, "Sanctions",
                "Penalty enforcement, deterrence", "Proof"),
    GovArchetype(GovElement.EARTH, GovElement.WATER, "Compliance",
                "Ongoing audit, verification", "AuditLog"),
    GovArchetype(GovElement.EARTH, GovElement.AIR, "Standards",
                "Regulatory framework", "Spec"),
    GovArchetype(GovElement.EARTH, GovElement.EARTH, "Constitution",
                "Fundamental law, meta-rules", "Spec"),
]


def get_gov_archetype(primary: GovElement, 
                     influence: GovElement) -> Optional[GovArchetype]:
    """Get archetype by elements."""
    for arch in GOV_ARCHETYPE_CATALOG:
        if arch.primary == primary and arch.influence == influence:
            return arch
    return None


# =============================================================================
# GOVERNANCE DOMAIN TAXONOMY
# =============================================================================

class GovDomain(Enum):
    """Major governance domains."""
    CORPORATE = "corporate"
    REGULATORY = "regulatory"
    JUDICIAL = "judicial"
    LEGISLATIVE = "legislative"
    EXECUTIVE = "executive"
    FINANCIAL = "financial"
    MEDICAL = "medical"
    TECHNICAL = "technical"


@dataclass
class DomainMapping:
    """Mapping of governance address to specific domain concepts."""
    
    address: GovAddress
    domain: GovDomain
    concept: str
    pcp_template: str
    
    def full_description(self) -> str:
        return f"{self.domain.value}/{self.concept}: {self.pcp_template}"


# Example domain mappings
DOMAIN_MAPPINGS = [
    # Corporate governance
    DomainMapping(
        GovAddress(GovElement.EARTH, GovElement.EARTH, 
                  GovElement.EARTH, GovElement.EARTH),
        GovDomain.CORPORATE,
        "Board oversight",
        "Fiduciary duty compliance"
    ),
    DomainMapping(
        GovAddress(GovElement.WATER, GovElement.EARTH,
                  GovElement.WATER, GovElement.EARTH),
        GovDomain.CORPORATE,
        "Financial reporting",
        "Audit trail verification"
    ),
    
    # Regulatory governance
    DomainMapping(
        GovAddress(GovElement.EARTH, GovElement.AIR,
                  GovElement.EARTH, GovElement.EARTH),
        GovDomain.REGULATORY,
        "Compliance standards",
        "Regulatory requirement check"
    ),
    
    # AI governance
    DomainMapping(
        GovAddress(GovElement.AIR, GovElement.EARTH,
                  GovElement.AIR, GovElement.EARTH),
        GovDomain.TECHNICAL,
        "AI safety audit",
        "Safety constraint verification"
    ),
]


# =============================================================================
# GOVERNANCE CLASSIFIER
# =============================================================================

class GovClassifier:
    """Classifies governance phenomena into the 256-atlas."""
    
    @staticmethod
    def classify(description: str) -> GovAddress:
        """
        Classify a governance phenomenon.
        
        Uses keyword matching to determine address.
        """
        desc = description.lower()
        
        # Determine primary (what type of governance)
        if any(k in desc for k in ['enforce', 'penalty', 'punish', 'sanction']):
            primary = GovElement.FIRE
        elif any(k in desc for k in ['evidence', 'monitor', 'surveill', 'record']):
            primary = GovElement.WATER
        elif any(k in desc for k in ['interpret', 'define', 'doctrine', 'meaning']):
            primary = GovElement.AIR
        elif any(k in desc for k in ['constrain', 'audit', 'comply', 'standard']):
            primary = GovElement.EARTH
        else:
            primary = GovElement.EARTH  # Default
        
        # Determine influence (secondary aspect)
        if any(k in desc for k in ['action', 'execute', 'implement']):
            influence = GovElement.FIRE
        elif any(k in desc for k in ['flow', 'continuous', 'ongoing']):
            influence = GovElement.WATER
        elif any(k in desc for k in ['analysis', 'review', 'interpret']):
            influence = GovElement.AIR
        elif any(k in desc for k in ['permanent', 'lock', 'binding']):
            influence = GovElement.EARTH
        else:
            influence = primary  # Default to same
        
        # Determine flavor (what gets applied)
        if any(k in desc for k in ['trigger', 'threshold', 'crisis']):
            flavor = GovElement.FIRE
        elif any(k in desc for k in ['report', 'transparency', 'disclose']):
            flavor = GovElement.WATER
        elif any(k in desc for k in ['jurisdiction', 'authority', 'scope']):
            flavor = GovElement.AIR
        elif any(k in desc for k in ['precedent', 'appeal', 'binding']):
            flavor = GovElement.EARTH
        else:
            flavor = GovElement.EARTH
        
        # Determine refinement (how it manifests)
        if any(k in desc for k in ['immediate', 'urgent', 'emergency']):
            refinement = GovElement.FIRE
        elif any(k in desc for k in ['periodic', 'cycle', 'feedback']):
            refinement = GovElement.WATER
        elif any(k in desc for k in ['channel', 'route', 'escalate']):
            refinement = GovElement.AIR
        elif any(k in desc for k in ['final', 'irrevocable', 'permanent']):
            refinement = GovElement.EARTH
        else:
            refinement = GovElement.EARTH
        
        return GovAddress(primary, influence, flavor, refinement)
    
    @staticmethod
    def describe(address: GovAddress) -> Dict[str, str]:
        """Get full description of an address."""
        return {
            "code": address.short_string(),
            "archetype": address.archetype_name(),
            "flavor": address.flavor_meaning(),
            "refinement": address.refinement_meaning(),
            "primary": f"{address.primary.symbol} {address.primary.domain}",
            "influence": f"{address.influence.symbol} {address.influence.domain}",
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_gov_atlas() -> bool:
    """Validate governance atlas module."""
    
    # Test GovAddress
    addr = GovAddress(
        primary=GovElement.EARTH,
        influence=GovElement.AIR,
        flavor=GovElement.WATER,
        refinement=GovElement.EARTH
    )
    assert addr.short_string() == "EAWE"
    assert addr.archetype_name() == "Standards"
    
    # Test round-trip
    n = addr.to_int()
    addr2 = GovAddress.from_int(n)
    assert addr == addr2
    
    # Test all 256 addresses
    for i in range(256):
        a = GovAddress.from_int(i)
        assert a.to_int() == i
    
    # Test archetype catalog
    assert len(GOV_ARCHETYPE_CATALOG) == 16
    
    arch = get_gov_archetype(GovElement.EARTH, GovElement.EARTH)
    assert arch is not None
    assert arch.name == "Constitution"
    
    # Test classifier
    addr = GovClassifier.classify("regulatory compliance audit")
    assert addr.primary == GovElement.EARTH
    
    desc = GovClassifier.describe(addr)
    assert "archetype" in desc
    
    return True


if __name__ == "__main__":
    print("Validating Governance Atlas...")
    assert validate_gov_atlas()
    print("✓ Governance Atlas validated")
    
    # Demo
    print("\n=== Governance 256-Atlas Demo ===")
    
    print("\n16 Governance Archetypes:")
    for arch in GOV_ARCHETYPE_CATALOG:
        print(f"  {arch.primary.short}{arch.influence.short} = {arch.name}: {arch.description}")
    
    print("\nClassification Examples:")
    examples = [
        "Enforce sanctions immediately",
        "Ongoing compliance monitoring with periodic reporting",
        "Interpret regulatory standards for AI safety",
        "Constitutional judicial review with binding precedent"
    ]
    
    for ex in examples:
        addr = GovClassifier.classify(ex)
        desc = GovClassifier.describe(addr)
        print(f"\n'{ex}'")
        print(f"  → {desc['code']} ({desc['archetype']})")
        print(f"  → Flavor: {desc['flavor']}")
        print(f"  → Refinement: {desc['refinement']}")
