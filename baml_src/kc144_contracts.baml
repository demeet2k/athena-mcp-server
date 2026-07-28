enum StewardshipState {
  RESEARCH_ONLY
  PAUSE
  REFUSE
}

enum AuthorityEffect {
  NONE
}

class SourceSpan {
  source_id string @assert(nonempty_source_id, {{ this|length > 0 }})
  span_id string @assert(nonempty_span_id, {{ this|length > 0 }})
  lineage_id string @assert(nonempty_lineage_id, {{ this|length > 0 }})
  text string @assert(nonempty_text, {{ this|length > 0 }})
  quality float @assert(valid_quality, {{ this >= 0 and this <= 1 }})
}

class QueryContract {
  query_id string @assert(nonempty_query_id, {{ this|length > 0 }})
  literal string @assert(nonempty_literal, {{ this|length > 0 }})
  intents string[]
  exact_addresses int[]
  requires_sources bool
  requires_execution bool
  requires_audit bool
  route_budget int @assert(positive_route_budget, {{ this > 0 }})
  claim_ceiling StewardshipState
  authority_effect AuthorityEffect
}

class OrganActivationDelta {
  organ_id string
  activation float @assert(valid_activation, {{ this >= 0 and this <= 1 }})
  evidence_span_ids string[]
  defects string[]
  final bool
  authority_effect AuthorityEffect
}

class StreamingBoundaryState {
  sequence int @assert(nonnegative_sequence, {{ this >= 0 }})
  deltas OrganActivationDelta[]
  observed_fields string[]
  final bool
  generated_manifestation bool
  return_required bool
  authority_effect AuthorityEffect
  @@assert(generated_output_is_marked, {{ this.generated_manifestation }})
  @@assert(return_is_required, {{ this.return_required }})
}

function CompileQueryContract(
  raw_query: string,
  known_addresses: string[]
) -> QueryContract {
  client KC144Fallback
  prompt #"
    {{ _.role("system") }}
    Compile a KC144 query contract.

    Constitutional rules:
    - SOURCE is not SUMMARY.
    - RELEVANCE is not EVIDENCE.
    - EXECUTION is not DESCRIPTION.
    - ROUTE WEIGHT is not TRUTH.
    - authority_effect must be NONE.
    - claim_ceiling may never exceed RESEARCH_ONLY.
    - Do not invent exact addresses.

    {{ _.role("user") }}
    Query: {{ raw_query }}
    Known addresses: {{ known_addresses }}
    {{ ctx.output_format }}
  "#
}

function StreamOrganBoundary(
  query: QueryContract,
  source_spans: SourceSpan[],
  active_organs: string[]
) -> StreamingBoundaryState {
  client KC144Fallback
  prompt #"
    {{ _.role("system") }}
    Produce a typed incremental organ-boundary state.
    Partial streamed fields are provisional and are not evidence.
    Preserve exact source span IDs, defects and return behavior.
    generated_manifestation and return_required must be true.
    authority_effect must be NONE.

    {{ _.role("user") }}
    Query: {{ query }}
    Source spans: {{ source_spans }}
    Active organs: {{ active_organs }}
    {{ ctx.output_format }}
  "#
}

test query_contract_source_audit {
  functions [CompileQueryContract]
  args {
    raw_query "Search sources, execute the route, audit contradictions, and return."
    known_addresses ["H06", "B21", "I06", "I09", "M12"]
  }
}

test streaming_boundary_contract {
  functions [StreamOrganBoundary]
  args {
    query {
      query_id "Q-STREAM-001"
      literal "Stream source-grounded organ activation."
      intents ["SELF_OBSERVATION", "SOURCE_GROUNDING"]
      exact_addresses [6, 86, 89, 144]
      requires_sources true
      requires_execution true
      requires_audit true
      route_budget 24
      claim_ceiling RESEARCH_ONLY
      authority_effect NONE
    }
    source_spans [{
      source_id "github:BoundaryML/baml"
      span_id "recording:stream"
      lineage_id "github:BoundaryML/baml"
      text "Streaming returns partial typed values and a final typed response."
      quality 0.95
    }]
    active_organs ["SOURCE", "AUDIT", "RETURN"]
  }
}
