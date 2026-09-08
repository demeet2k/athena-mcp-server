# Windows continuity contract

Prompt-runtime writes persist the exact UTF-8 representation supplied to the
commit operation. Host newline translation must not change candidate envelopes,
body strings or evidence bytes. The candidate reader accepts historical LF and
CRLF metadata envelopes while preserving the body exactly; it does not rewrite
the carrier merely by reading it.

Rehydration receipts store repository-relative paths with `/`. Verification uses
the same serialization on Windows and POSIX hosts. A valid local receipt must
not become an integrity hold because of an operating-system path separator;
content, chain, ancestry and stale-head checks remain enforced.

SQLite tests use owned paths without an open temporary-file handle. Connections
must close before fixture cleanup. Cold-process acceptance reads stdout through
a queue-fed thread and drains stderr separately, retaining a bounded diagnostic
tail. A monotonic response deadline prevents unrelated output from extending a
request indefinitely, and process shutdown releases the readers and pipes.

CI includes the complete runtime unittest discovery suite on Python 3.12 on
Windows, alongside Linux and the selected Wiki compatibility lane. The main
workflow's promotion-receipt job waits for the full Windows job. A test-suite
pass qualifies its declared runtime behavior; it is not an independent research
result or proof of improved successor decisions.
