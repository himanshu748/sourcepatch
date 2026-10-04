'use strict';

// The landing page only reads deterministic authored fixture data. It never
// checks a URL, calls a search provider, approves a candidate, or changes source.
(() => {
  const fixture = window.SOURCEPATCH_FIXTURE;
  if (!fixture || fixture.mode !== 'fixture' || fixture.live_verified !== false) return;

  const citations = fixture.citations;
  const list = document.querySelector('#citation-list');
  const search = document.querySelector('#citation-search');
  const searchStatus = document.querySelector('#search-status');
  const candidateList = document.querySelector('#candidate-list');
  const reviewNotice = document.querySelector('#review-notice');
  let selectedId = citations[0].id;

  const make = (tag, className, value) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  };
  const badgeText = citation => citation.check.state === 'blocked'
    ? 'Blocked' : `${citation.check.status} · Fixture`;

  function renderEvidence(citation) {
    selectedId = citation.id;
    document.querySelector('#citation-title').textContent = citation.label;
    const status = document.querySelector('#citation-status');
    status.textContent = badgeText(citation);
    status.className = `badge ${citation.check.state}`;
    document.querySelector('#citation-context').textContent = `${citation.occurrences} reference${citation.occurrences === 1 ? '' : 's'} in this document · Synthetic fixture evidence`;
    document.querySelector('#original-url').textContent = citation.url;
    reviewNotice.classList.toggle('ambiguous', citation.ambiguous);
    reviewNotice.textContent = citation.ambiguous
      ? 'Two candidates share the highest score. The title alone cannot resolve the author’s intent. Read both pages before deciding.'
      : citation.check.state === 'blocked'
        ? 'This local address is outside the public-URL boundary. It was blocked before any request. No replacement was invented.'
        : citation.check.state === 'healthy'
          ? 'The authored fixture marks this destination as reachable. It needs no replacement in this sample. This is not a live HTTP observation.'
          : 'These results suggest possible replacements. A matching hostname and title do not establish equivalent meaning.';

    candidateList.replaceChildren();
    for (const candidate of citation.candidates) {
      const row = make('div', 'candidate');
      const title = make('div', 'candidate-title');
      title.append(make('h5', '', candidate.title), make('span', '', `${candidate.score} / 100`));
      const reasons = make('ul', 'candidate-reasons');
      candidate.reasons.slice(0, 2).forEach(reason => reasons.append(make('li', '', reason)));
      row.append(title, make('code', '', candidate.url), make('p', '', candidate.snippet), reasons);
      candidateList.append(row);
    }
    if (!citation.candidates.length) {
      candidateList.append(make('p', 'empty-candidates', citation.check.state === 'blocked'
        ? 'No search was run for this address. Public-only validation protects the local workbench’s request boundary.'
        : 'No search was needed for this authored example. SourcePatch discovers replacements only after a 404 or 410 status.'));
    }
    document.querySelector('#discovery-query').textContent = citation.query || 'No discovery query';
    document.querySelector('#discovery-note').textContent = citation.search_note || 'No network or provider request was made.';
    for (const button of list.querySelectorAll('button')) {
      button.setAttribute('aria-pressed', String(button.dataset.citationId === selectedId));
    }
  }

  function renderLedger() {
    const term = search.value.trim().toLocaleLowerCase();
    const visible = citations.filter(c => `${c.label} ${c.url} ${c.check.state}`.toLocaleLowerCase().includes(term));
    list.replaceChildren();
    for (const citation of visible) {
      const button = make('button', 'citation-button');
      button.type = 'button';
      button.dataset.citationId = citation.id;
      button.setAttribute('aria-pressed', String(citation.id === selectedId));
      button.setAttribute('aria-controls', 'evidence-record');
      const meta = make('span', 'row-meta');
      meta.append(make('span', `badge ${citation.check.state}`, badgeText(citation)), make('span', 'occurrences', `${citation.occurrences} reference${citation.occurrences === 1 ? '' : 's'}`));
      button.append(make('strong', '', citation.label), make('span', 'host', new URL(citation.url).hostname), meta);
      button.addEventListener('click', () => renderEvidence(citation));
      list.append(button);
    }
    searchStatus.hidden = !term;
    searchStatus.textContent = visible.length
      ? `${visible.length} citation${visible.length === 1 ? '' : 's'} match. Select one to inspect its evidence.`
      : 'No fixture citations match. Try “Python”, “fetch”, or clear your search. The current evidence remains below.';
  }

  document.querySelector('.search-control').hidden = false;
  list.hidden = false;
  search.addEventListener('input', renderLedger);
  renderLedger();
  renderEvidence(citations[0]);

  const copy = document.querySelector('#copy-command');
  if (navigator.clipboard?.writeText) {
    copy.hidden = false;
    copy.addEventListener('click', async () => {
      const status = document.querySelector('#copy-status');
      try {
        await navigator.clipboard.writeText('python3 -m sourcepatch');
        status.textContent = 'Command copied. Run it from the cloned repository.';
      } catch {
        status.textContent = 'Clipboard unavailable. Select and copy the command above.';
      }
    });
  }
})();
