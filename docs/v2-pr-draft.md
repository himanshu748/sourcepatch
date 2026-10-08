# Add bounded candidate-content evidence to SourcePatch

The current workbench ranks search snippets without retrieving candidate content. This change adds explicit, server-owned candidate inspection with safe HTML retrieval, bounded excerpts, hashes, fragment checks and lexical relevance reasons. Inspected insufficient candidates cannot be exported; existing uninspected explicit approvals remain compatible and visibly unverified.

Additional publisher, cross-domain, identifier and Scholar discovery uses allowlisted SerpApi parameters, normalized engine-aware caching and sanitized receipts under the existing attempted-call cap. The dependency-free UI adds original context, strategy history, evidence review and abstention exports. Source spans, network policy and explicit decisions remain intact.

Validation: 110 Python tests; compilation/JS syntax; all three original UI harness modes plus 12 V2 assertions; focused desktop/390px browser checks; reproducible 13-case authored/recorded benchmark. A fresh public candidate page was retrieved using historical live discovery. No new live SerpApi/Scholar proof is claimed because an existing key was unavailable. Existing submitted V1 is preserved; no portal change.

This description is prepared locally. No pull request was created because GitHub CLI authentication is invalid.
