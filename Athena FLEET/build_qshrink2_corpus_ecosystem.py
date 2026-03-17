from __future__ import annotations

import json

from qshrink2_corpus_runtime import build_outputs


def main() -> None:
    result = build_outputs()
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
