"""
parsers -- Tokenisation and morphological parsing for the Athena Process Language.

Pipeline:
    raw EVA text
      -> eva_tokenizer.tokenize()      -> list[RawToken]
      -> vml_slot_parser.parse()        -> list[ParsedToken]
      -> ambiguity.resolve()            -> list[ParsedToken]  (candidates ranked & selected)

Exports:
    eva_tokenizer:    tokenize(), split_eva_line()
    vml_slot_parser:  SlotParser, parse_token()
    ambiguity:        AmbiguityEnvelope, resolve_candidates()
"""

from athena_process_compiler.parsers.eva_tokenizer import tokenize, split_eva_line
from athena_process_compiler.parsers.vml_slot_parser import SlotParser, parse_token
from athena_process_compiler.parsers.ambiguity import AmbiguityEnvelope, resolve_candidates
