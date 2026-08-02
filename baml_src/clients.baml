client<llm> KC144Primary {
  provider openai
  retry_policy KC144Exponential
  options {
    model env.KC144_BAML_MODEL
    api_key env.OPENAI_API_KEY
  }
}

client<llm> KC144Secondary {
  provider anthropic
  retry_policy KC144Constant
  options {
    model env.KC144_BAML_FALLBACK_MODEL
    api_key env.ANTHROPIC_API_KEY
  }
}

client<llm> KC144Fallback {
  provider fallback
  options {
    strategy [
      KC144Primary
      KC144Secondary
    ]
  }
}

retry_policy KC144Constant {
  max_retries 1
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy KC144Exponential {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 3000
  }
}
