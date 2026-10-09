'use strict';
const $ = (id) => document.getElementById(id);
const state = {config: null, analysis: null, selected: 0, candidate: null, decisions: {}, exported: null, busy: false, revision: 0};

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function error(message = '') { $('error').textContent = message; $('error').hidden = !message; }
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed. Try again.');
  return data;
}
function approvedCount() { return Object.values(state.decisions).filter((x) => typeof x === 'string').length; }
function clearExport() { state.revision++; state.exported = null; $('export-content').hidden = true; $('diff').textContent = ''; }
function changedSource() {
  state.analysis = null; state.decisions = {}; state.candidate = null; clearExport();
  $('document-name').textContent = 'Untitled guide';
  render();
}
function badge(citation) {
  const decision = state.decisions[citation.id];
  if (typeof decision === 'string') return element('span', 'badge approved', 'Approved');
  if (decision === null) return element('span', 'badge', 'Skipped');
  const check = citation.check;
  const labels = {broken: `${check.status} · Broken`, healthy: `${check.status} · Reachable`, blocked: 'Blocked', uncertain: 'Uncertain', unavailable: 'No fixture'};
  return element('span', 'badge ' + check.state, labels[check.state] || 'Not checked');
}
function renderQueue() {
  const queue = $('queue'); queue.replaceChildren();
  const citations = state.analysis?.citations || [];
  $('queue-count').textContent = `${citations.length} sources`;
  citations.forEach((citation, index) => {
    const button = element('button', 'queue-item');
    button.type = 'button';
    button.setAttribute('aria-current', index === state.selected ? 'true' : 'false');
    button.append(element('h3', '', citation.label));
    let host = citation.url;
    try { host = new URL(citation.url).hostname; } catch (_) { /* Show safe plain text for malformed URLs. */ }
    button.append(element('p', 'queue-domain', host));
    const meta = element('div', 'queue-meta');
    meta.append(badge(citation), element('span', '', citation.occurrences > 1 ? `${citation.occurrences} references` : '1 reference'));
    button.append(meta);
    button.addEventListener('click', () => {
      if (state.busy) return;
      state.selected = index;
      state.candidate = typeof state.decisions[citation.id] === 'string' ? state.decisions[citation.id] : null;
      renderQueue(); renderReview();
    });
    queue.append(button);
  });
}
function renderReview() {
  const panel = $('review'); panel.replaceChildren(); panel.classList.remove('just-approved');
  const citations = state.analysis?.citations || [];
  if (!citations.length) {
    const empty = element('div', 'empty-state');
    empty.append(element('h2', '', state.analysis ? 'No external citations found' : 'Start with a document'));
    empty.append(element('p', '', state.analysis ? 'SourcePatch looks for Markdown links and reference definitions. Code, images, local anchors and unsupported syntax remain untouched.' : 'Paste a Markdown guide or load the authored sample. Inspect it to begin a careful, source-by-source review.'));
    const edit = element('button', 'secondary', 'Open source editor'); edit.addEventListener('click', () => {$('source-panel').open = true; $('source').focus();}); empty.append(edit); panel.append(empty); return;
  }
  const citation = citations[state.selected];
  const top = element('div', 'review-top');
  const title = element('div'); title.append(element('h2', '', citation.label), element('p', '', `${citation.occurrences} reference${citation.occurrences === 1 ? '' : 's'} in this document · ${state.analysis.mode === 'fixture' ? 'Synthetic fixture evidence' : 'Live inspection evidence'}`));
  top.append(title, badge(citation)); panel.append(top, element('div', 'old-url', citation.url), element('p', 'review-detail', citation.check.detail));
  const context = element('section', 'original-context');
  context.append(element('h3', 'section-label', 'Original context'), element('blockquote', '', citation.context)); panel.append(context);
  renderDiscovery(panel, citation);
  if (citation.ambiguous) panel.append(element('p', 'warning', 'Two close matches. The scores are too similar to name a clear lead. Compare the purpose of each page before choosing.'));
  if (typeof state.decisions[citation.id] === 'string') {
    panel.append(element('p', 'approved-note', 'Replacement approved for export. Your source file is still unchanged.'));
  } else if (state.decisions[citation.id] === null) {
    panel.append(element('p', 'approved-note', 'Skipped. This citation will remain exactly as it is.'));
  }
  if (!citation.candidates.length) {
    const empty = element('div', 'empty-state');
    const messages = {
      healthy: ['This source can stay', 'The fixture marks this citation as reachable. A successful HTTP response alone does not verify content or meaning.'],
      blocked: ['A boundary worth keeping', 'Private addresses and non-standard ports are outside this workbench. This URL was rejected before any request or search.'],
      unavailable: ['Bring your own public guide', 'This URL has no authored fixture. Fixture mode never guesses its status. Use live mode with an existing key to inspect public citations.'],
      uncertain: ['No reliable verdict yet', 'A timeout, access restriction or server error is not proof of a broken citation. SourcePatch leaves this link alone.'],
      broken: ['No candidate to approve', citation.search_note || 'No useful search result was returned. The citation remains unchanged.']
    };
    let [heading, body] = messages[citation.check.state] || messages.uncertain;
    if (citation.check.state === 'healthy' && state.analysis.mode === 'live') body = 'The site returned a successful HTTP response. Content and fragment anchors still need human review.';
    empty.append(element('h2', '', heading), element('p', '', body)); panel.append(empty);
    const skip = element('button', 'secondary', state.decisions[citation.id] === null ? 'Undo decision' : 'Leave citation unchanged');
    skip.addEventListener('click', () => { if (state.busy) return; if (state.decisions[citation.id] === null) delete state.decisions[citation.id]; else state.decisions[citation.id] = null; clearExport(); render(); });
    panel.append(skip); renderSearchDetails(panel, citation); return;
  }
  const heading = element('div', 'candidate-heading'); heading.append(element('h3', '', 'Possible new homes'), element('span', '', 'Rank scores are heuristics, not certainty')); panel.append(heading);
  const list = element('div', 'candidate-list');
  citation.candidates.forEach((candidate, index) => {
    const label = element('label', 'candidate' + (state.candidate === candidate.url ? ' selected' : ''));
    const radio = document.createElement('input'); radio.type = 'radio'; radio.name = 'candidate'; radio.value = candidate.url; radio.checked = state.candidate === candidate.url; radio.setAttribute('aria-label', `Select ${candidate.title}`);
    const main = element('div', 'candidate-main');
    const row = element('div', 'candidate-top'); row.append(element('span', 'candidate-title', candidate.title), element('span', 'score', `Rank score ${candidate.score} / 100`));
    const link = element('a', 'candidate-url', candidate.url); link.href = candidate.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; link.setAttribute('aria-label', `Open candidate ${index + 1} in a new tab`); link.addEventListener('click', (event) => event.stopPropagation());
    const reasons = element('div', 'candidate-reasons');
    reasons.append(element('span', candidate.same_host ? 'host-mark' : '', candidate.same_host ? 'Same hostname' : 'Different hostname'), element('span', '', candidate.reasons[1]));
    main.append(row, link, element('p', 'candidate-snippet', candidate.snippet), reasons);
    main.append(element('span', 'evidence-label', candidate.evidence ? `${candidate.evidence.origin === 'authored_fixture' ? 'Authored offline fixture' : 'Directly inspected page'} · ${candidate.evidence.state}` : 'Heuristic inference · page not inspected'));
    if (candidate.warning) main.append(element('p', 'candidate-warning', candidate.warning));
    label.append(radio, main); list.append(label);
    radio.addEventListener('change', () => {
      if (state.busy) return;
      state.candidate = candidate.url;
      list.querySelectorAll('.candidate').forEach((el) => el.classList.toggle('selected', el.querySelector('input').checked));
      $('approve').disabled = !canApprove(citation);
      renderEvidence(citation);
    });
  });
  panel.append(list);
  const evidencePanel = element('section', 'evidence-panel'); evidencePanel.id = 'page-evidence'; panel.append(evidencePanel);
  renderEvidence(citation);
  const actions = element('div', 'review-actions'); actions.append(element('p', '', 'Check the page yourself. Search results do not establish equivalent meaning.'));
  const buttons = element('div');
  const skip = element('button', 'text-button', Object.hasOwn(state.decisions, citation.id) ? 'Undo decision' : 'Skip this source');
  skip.addEventListener('click', () => {
    if (state.busy) return;
    if (Object.hasOwn(state.decisions, citation.id)) delete state.decisions[citation.id];
    else state.decisions[citation.id] = null;
    state.candidate = null; clearExport(); render();
  });
  const approve = element('button', 'primary', typeof state.decisions[citation.id] === 'string' ? 'Update approval' : 'Approve replacement'); approve.id = 'approve'; approve.disabled = !canApprove(citation);
  approve.addEventListener('click', () => {
    if (state.busy || !canApprove(citation)) return;
    state.decisions[citation.id] = state.candidate;
    clearExport(); render(); $('review').classList.add('just-approved');
  });
  buttons.append(skip, approve); actions.append(buttons); panel.append(actions);
  renderSearchDetails(panel, citation);
}
function renderSearchDetails(panel, citation) {
  renderHistory(panel, citation);
  if (!citation.query) return;
  const details = element('details', 'query-details');
  details.append(element('summary', '', 'Inspect search query & evidence source'), element('code', '', citation.query), element('p', '', citation.search_note));
  const receipt = citation.search_evidence;
  if (receipt) {
    details.append(element('p', '', `${receipt.provider} ${receipt.engine} · HTTP ${receipt.response_status} · ${receipt.result_count} eligible results · ${receipt.cache_hit ? 'Reused in-memory response; no new provider request' : 'New provider response'} · Retrieved ${receipt.retrieved_at}`));
    if (receipt.search_id) details.append(element('p', '', `Provider search ID: ${receipt.search_id}`));
    details.append(element('p', '', 'A response receipt records discovery; it does not verify candidate meaning. The receipt is included with approved changes in provenance JSON.'));
  }
  panel.append(details);
}
function canApprove(citation) {
  const candidate = citation.candidates.find(c => c.url === state.candidate);
  return !state.busy && candidate && state.decisions[citation.id] !== state.candidate && (candidate.evidence?.state === 'related' || (state.config.evidence_version !== 2 && !candidate.evidence));
}
function setBusyControls() {
  for (const id of ['inspect', 'load-sample', 'clear-source', 'source']) $(id).disabled = state.busy || !state.config;
  $('workspace').setAttribute('aria-busy', String(state.busy));
  for (const node of [...$('queue').querySelectorAll('button'), ...$('review').querySelectorAll('button'), ...$('review').querySelectorAll('input')]) {
    if (node.id !== 'approve') node.disabled = state.busy;
  }
  const c = state.analysis?.citations[state.selected];
  if (c && $('approve')) $('approve').disabled = !canApprove(c);
}
async function extendAnalysis(path, citation, fields) {
  if (state.busy || !state.analysis) return;
  const aid = state.analysis.analysis_id;
  state.busy = true; clearExport(); setBusyControls(); error();
  $('summary').textContent = path.includes('verify') ? 'Inspecting bounded candidate content…' : 'Running the requested search strategy…';
  try {
    const result = await api(path, {analysis_id: aid, citation_id: citation.id, ...fields});
    if (state.analysis?.analysis_id !== aid) return;
    state.analysis = result;
    state.selected = result.citations.findIndex(c => c.id === citation.id);
    delete state.decisions[citation.id];
  } catch (err) { error(err.message); }
  finally { state.busy = false; render(); }
}
function renderDiscovery(panel, citation) {
  if (citation.check.state !== 'broken') return;
  const controls = element('section', 'discovery-controls');
  controls.append(element('h3', 'section-label', 'Candidate discovery'));
  controls.append(element('p', '', `Searches requested: ${state.analysis.summary.searches} / ${state.analysis.summary.search_budget}. Additional strategies run only when you choose them. Failed provider attempts use allowance; cache hits do not.`));
  const buttons = element('div', 'strategy-buttons');
  for (const [strategy, title] of [['publisher', 'Publisher search'], ['broad', 'Cross-domain search'], ['identifier', 'Identifier search'], ['scholar', 'Google Scholar']]) {
    const button = element('button', 'secondary', title);
    button.addEventListener('click', () => extendAnalysis('/api/discover', citation, {strategy}));
    buttons.append(button);
  }
  controls.append(buttons); panel.append(controls);
}
function renderHistory(panel, citation) {
  if (!citation.search_history?.length) return;
  const history = element('details', 'search-history');
  history.append(element('summary', '', `Search strategy history · ${citation.search_history.length} requests`));
  for (const entry of citation.search_history) {
    const row = element('section', 'history-row');
    row.append(element('h4', '', `${entry.strategy} / ${entry.engine} · ${entry.origin === 'authored_fixture' ? 'Authored offline fixture' : 'Live provider attempt'}`), element('code', '', entry.query), element('p', '', entry.note));
    if (entry.receipt) row.append(element('pre', '', JSON.stringify(entry.receipt, null, 2)));
    history.append(row);
  }
  panel.append(history);
}
function renderEvidence(citation) {
  const panel = $('page-evidence'); if (!panel) return;
  panel.replaceChildren(element('h3', 'section-label', 'Evidence review'));
  const candidate = citation.candidates.find(c => c.url === state.candidate);
  if (!candidate) { panel.append(element('p', '', 'Select a candidate to inspect its page evidence. No candidate is automatically approved.')); return; }
  panel.append(element('h4', 'section-label', 'Candidate URL'), element('code', 'evidence-url', candidate.url));
  panel.append(element('h4', 'section-label', 'Source metadata'), element('p', '', `${candidate.title} · ${candidate.same_host ? 'Same hostname; publisher identity still needs review' : 'Different hostname; verify publisher identity'}`));
  if (candidate.publication) panel.append(element('p', '', candidate.publication));
  const e = candidate.evidence;
  if (!e) {
    panel.append(element('p', 'warning', 'Page not inspected. Inspect this candidate before approving it. Search snippets and rank scores are only discovery clues.'));
    const button = element('button', 'primary', state.analysis.mode === 'fixture' ? 'Inspect authored page fixture' : 'Inspect candidate page');
    button.id = 'verify-candidate';
    button.addEventListener('click', () => extendAnalysis('/api/candidates/verify', citation, {candidate_id: candidate.id}));
    panel.append(button); return;
  }
  if (!e.retrieval.observed && (candidate.evidence_history?.length || 0) < 2) {
    const retry = element('button', 'secondary', 'Retry failed page fetch');
    retry.id = 'verify-candidate';
    retry.addEventListener('click', () => extendAnalysis('/api/candidates/verify', citation, {candidate_id: candidate.id, retry: true}));
    panel.append(retry);
  }
  if (candidate.evidence_history?.length) panel.append(element('p', 'warning', `${candidate.evidence_history.length} earlier failed page fetches retained in provenance. No automatic retries.`));
  panel.append(element('h4', 'section-label', 'Retrieved page evidence'));
  panel.append(element('p', 'evidence-label', `${e.origin === 'authored_fixture' ? 'Authored offline fixture — no network request' : 'Direct candidate retrieval'} · ${e.state}`));
  panel.append(element('p', '', `${e.retrieval.observed ? `HTTP ${e.retrieval.status} · ${e.retrieval.bytes} bytes` : 'No HTTP response observed'} · ${e.retrieval.retrieved_at}`));
  if (e.retrieval.final_url) panel.append(element('code', 'evidence-url', `Final URL: ${e.retrieval.final_url}`));
  panel.append(element('p', '', `Page title: ${e.title || 'Unavailable'}`), element('p', '', `Headings: ${e.headings.join(' / ') || 'Unavailable'}`));
  for (const excerpt of e.excerpts) panel.append(element('blockquote', '', excerpt));
  panel.append(element('p', '', `Anchor: ${e.anchor.fragment || '(none requested)'} · ${e.anchor.state}`));
  if (e.content_sha256) panel.append(element('code', 'evidence-url', `Response SHA256: ${e.content_sha256}`));
  panel.append(element('h4', 'section-label', 'Relevance reasons — heuristic inference'), element('p', '', candidate.reason_codes.join(' · ')));
  panel.append(element('h4', 'section-label', 'Warnings'));
  for (const warning of e.warnings) panel.append(element('p', 'warning', warning));
  panel.append(element('p', '', 'Human approval control is below. Related content does not establish semantic equivalence.'));
}
function render() {
  renderQueue(); renderReview();
  const a = state.analysis; const count = approvedCount();
  $('summary').textContent = a ? `${a.summary.total} citations · ${a.summary.broken} need review · ${count} approved` : 'Source changed · inspect to begin';
  $('export-status').textContent = count ? `${count} replacement${count === 1 ? '' : 's'} approved. Export a URL-only patch with its evidence.` : 'No replacements approved yet. Your source is unchanged.';
  setBusyControls();
  $('preview').disabled = !a || Object.keys(state.decisions).length === 0 || state.busy;
}
async function inspect() {
  if (state.busy || !state.config) return;
  state.busy = true; setBusyControls(); error();
  try {
    for (const id of ['inspect', 'load-sample', 'clear-source', 'source']) $(id).disabled = true;
    $('inspect').textContent = 'Inspecting…'; $('summary').textContent = state.config.mode === 'fixture' ? 'Reading authored fixtures…' : 'Checking public URLs and searching; this can take a few minutes…';
    const result = await api('/api/analyze', {source: $('source').value});
    state.analysis = result; state.selected = 0; state.candidate = null; state.decisions = {}; clearExport();
    $('source-panel').open = result.citations.length === 0;
    render();
  } catch (err) { error(err.message); }
  finally {
    state.busy = false;
    for (const id of ['inspect', 'load-sample', 'clear-source', 'source']) $(id).disabled = false;
    $('inspect').textContent = 'Inspect citations →';
    $('preview').disabled = !state.analysis || Object.keys(state.decisions).length === 0;
    setBusyControls();
  }
}
async function preview() {
  if (!state.analysis || state.busy) return;
  const analysisId = state.analysis.analysis_id; const decisions = JSON.stringify(state.decisions); const revision = state.revision;
  $('preview').disabled = true; error();
  try {
    const output = await api('/api/export', {analysis_id: analysisId, decisions: state.decisions, require_evidence: state.config.evidence_version === 2});
    if (state.revision !== revision || state.analysis?.analysis_id !== analysisId || JSON.stringify(state.decisions) !== decisions) return;
    state.exported = output; $('diff').textContent = output.diff || 'No changes approved.'; $('export-content').hidden = false;
    $('export-content').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'nearest'});
  } catch (err) { error(err.message); }
  finally { $('preview').disabled = !state.analysis || Object.keys(state.decisions).length === 0; }
}
function download(name, content, type) {
  if (!state.exported) return;
  const url = URL.createObjectURL(new Blob([content], {type}));
  const link = document.createElement('a'); link.href = url; link.download = name; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
$('about-button').addEventListener('click', () => { const open = $('about-panel').hidden; $('about-panel').hidden = !open; $('about-button').setAttribute('aria-expanded', String(open)); });
$('source').addEventListener('input', changedSource);
$('inspect').addEventListener('click', inspect);
$('preview').addEventListener('click', preview);
$('load-sample').addEventListener('click', () => { $('source').value = state.config.sample; changedSource(); $('document-name').textContent = 'field-guide.md'; if (state.config.mode === 'fixture') inspect(); });
$('clear-source').addEventListener('click', () => {$('source').value = ''; changedSource(); $('source-panel').open = true; $('source').focus();});
$('download-diff').addEventListener('click', () => download('sourcepatch.diff', state.exported?.diff, 'text/plain'));
$('download-markdown').addEventListener('click', () => download('guide.patched.md', state.exported?.markdown, 'text/markdown'));
$('download-report').addEventListener('click', () => download('provenance.json', JSON.stringify(state.exported?.provenance, null, 2), 'application/json'));
(async () => {
  try {
    state.config = await api('/api/config'); $('source').value = state.config.sample;
    for (const id of ['inspect', 'load-sample', 'clear-source', 'source']) $(id).disabled = false;
    if (state.config.mode === 'fixture') await inspect();
    else {
      $('mode-title').textContent = 'Live mode'; $('mode-description').textContent = `Public URL checks and SerpApi queries. At most ${state.config.process_search_budget} attempted SerpApi calls per process. Review candidate meaning yourself.`;
      $('footer-mode').textContent = 'Live inspection · Key stays in process memory';
      $('source-panel').open = true; render();
    }
  } catch (err) { error('Could not load the local workbench. Restart the server and refresh.'); }
})();
