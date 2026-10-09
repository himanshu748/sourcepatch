# Add evidence-gated citation review and a verified live V2 workflow

Broken citations previously relied on search snippets. V2 adds explicit bounded page inspection, title/headings/excerpts/hashes, fragment and identifier checks, evidence-aware ranking, and publisher/broad/identifier/Scholar discovery. The browser requires related page evidence before approval; strict export rejects uninspected replacements. Failed transports permit two explicit retries while retaining every failed observation and existing budgets.

The public landing now leads with an actual SerpApi → page inspection → approval → exact two-URL patch run and a 100-second recording with Deepgram Aura 2 Thalia narration. Input typo and agent-operated alternative-source review are disclosed. Fixtures remain separate; failures and the earlier abstention are preserved. No runtime LLM or application dependencies were added.

Validation: 114 Python tests in the full suite, original UI modes and 19 V2 assertions, compile/JS syntax, static evidence equality, actual live browser export and exact two-destination comparison. A Python 3.11/3.13 CI matrix is included. The small 13-case authored/recorded benchmark is not a production accuracy claim. Submitted V1 is preserved and the portal remains unchanged.
