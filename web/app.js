'use strict';
const $ = (id) => document.getElementById(id);
const state = {config: null, analysis: null, selected: 0, candidate: null, decisions: {}, exported: null, busy: false};

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
function clearExport() { state.exported = null; $('export-content').hidden = true; $('diff').textContent = ''; }
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
    renderSearchDetails(panel, citation); return;
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
    if (candidate.warning) main.append(element('p', 'candidate-warning', candidate.warning));
    label.append(radio, main); list.append(label);
    radio.addEventListener('change', () => {
      state.candidate = candidate.url;
      list.querySelectorAll('.candidate').forEach((el) => el.classList.toggle('selected', el.querySelector('input').checked));
      $('approve').disabled = state.decisions[citation.id] === state.candidate;
    });
  });
  panel.append(list);
  const actions = element('div', 'review-actions'); actions.append(element('p', '', 'Check the page yourself. Search results do not establish equivalent meaning.'));
  const buttons = element('div');
  const skip = element('button', 'text-button', Object.hasOwn(state.decisions, citation.id) ? 'Undo decision' : 'Skip this source');
  skip.addEventListener('click', () => {
    if (Object.hasOwn(state.decisions, citation.id)) delete state.decisions[citation.id];
    else state.decisions[citation.id] = null;
    state.candidate = null; clearExport(); render();
  });
  const approve = element('button', 'primary', typeof state.decisions[citation.id] === 'string' ? 'Update approval' : 'Approve replacement'); approve.id = 'approve'; approve.disabled = !state.candidate || state.decisions[citation.id] === state.candidate;
  approve.addEventListener('click', () => {
    if (!state.candidate) return;
    state.decisions[citation.id] = state.candidate;
    clearExport(); render(); $('review').classList.add('just-approved');
  });
  buttons.append(skip, approve); actions.append(buttons); panel.append(actions);
  renderSearchDetails(panel, citation);
}
function renderSearchDetails(panel, citation) {
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
function render() {
  renderQueue(); renderReview();
  const a = state.analysis; const count = approvedCount();
  $('summary').textContent = a ? `${a.summary.total} citations · ${a.summary.broken} need review · ${count} approved` : 'Source changed · inspect to begin';
  $('export-status').textContent = count ? `${count} replacement${count === 1 ? '' : 's'} approved. Export a URL-only patch with its evidence.` : 'No replacements approved yet. Your source is unchanged.';
  $('preview').disabled = !a || count === 0 || state.busy;
}
async function inspect() {
  if (state.busy || !state.config) return;
  state.busy = true; error();
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
    $('preview').disabled = !state.analysis || approvedCount() === 0;
  }
}
async function preview() {
  if (!state.analysis || state.busy) return;
  const analysisId = state.analysis.analysis_id; const decisions = JSON.stringify(state.decisions);
  $('preview').disabled = true; error();
  try {
    const output = await api('/api/export', {analysis_id: analysisId, decisions: state.decisions});
    if (state.analysis?.analysis_id !== analysisId || JSON.stringify(state.decisions) !== decisions) return;
    state.exported = output; $('diff').textContent = output.diff || 'No changes approved.'; $('export-content').hidden = false;
    $('export-content').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'nearest'});
  } catch (err) { error(err.message); }
  finally { $('preview').disabled = !state.analysis || approvedCount() === 0; }
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
