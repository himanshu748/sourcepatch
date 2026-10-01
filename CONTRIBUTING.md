# Contributing to SourcePatch

1. Read README.md and SECURITY.md before making a change.
2. Use Python 3.11+ and the standard library. The application must run without installing dependencies.
3. Write a failing unittest for changed behavior first, verify that it fails for the intended reason, implement the smallest fix, then run the full suite: `python -m unittest discover -s tests -v`.
4. Never add credentials, actual private documents, personal data, network-dependent tests, or generated claims of live verification.
5. Preserve exact source text outside explicitly approved link destinations. Do not introduce automatic repairs or in-place source writes.
6. Treat every URL and API result as untrusted. All live requests must go through the network policy.
7. UI changes must preserve keyboard access, visible focus, 4.5:1 body text contrast, fixture labels and mobile usability. Check both desktop and mobile.
8. Explain behavior, test evidence, and known limitations in your change. Keep scope small; do not change unrelated projects.
