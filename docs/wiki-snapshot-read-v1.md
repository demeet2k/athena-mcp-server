# Committed Wiki object reading

Wiki ingestion, draft validation, historical review, committed query and source retrieval share `read_snapshot`. Its result remains a complete path-to-content map: semantic files are UTF-8 strings and immutable raw carriers are bytes. Readset hashes and caller-visible source identities are unchanged.

The reader uses two Git processes for a nonempty snapshot. `ls-tree -r -l -z --full-tree` enumerates paths, object identities, modes and sizes. All paths and modes are validated, case collisions rejected, and the existing 8 MB aggregate limit checked before any content is requested. Repeated object identities are read once, while every path still contributes its size to the limit.

`cat-file --batch` then returns the requested blobs. Parsing uses each exact byte length, so embedded NULs, newlines and CRLFs do not delimit content. Every response header must match its requested object ID, blob type and declared size. The reader checks the trailing delimiter, recomputes each Git blob identity from the bytes, and rejects omitted, substituted, malformed or trailing data. Empty files are valid. An empty snapshot does not start the batch process.

Neither the default reader nor the hardened historical readers honor Git replacement objects or inherited Git environment redirects. Reading does not apply text conversion, checkout files, import observations or execute code from evidence. It does not establish producer authenticity or live Drive currentness.

Validation includes a real Git fixture with 33 files, binary delimiters, Unicode paths and a replacement ref; deterministic malformed-response and aggregate-size cases; and the existing ingestion, draft, review, query and source suites. The two-process property is checked directly instead of imposing a platform-dependent wall-time threshold.

Format references: [Git ls-tree output](https://git-scm.com/docs/git-ls-tree#_output_format) and [Git cat-file batch output](https://git-scm.com/docs/git-cat-file#_batch_output).
