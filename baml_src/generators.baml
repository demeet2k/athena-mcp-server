generator python_client {
  output_type "python/pydantic"
  output_dir "../generated"
  default_client_mode "sync"
  version "0.223.0"
}

generator typescript_client {
  output_type "typescript"
  output_dir "../generated/typescript"
  default_client_mode "async"
  version "0.223.0"
}
