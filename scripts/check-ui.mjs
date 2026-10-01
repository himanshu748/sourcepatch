/** Dependency-free DOM-contract checks, NOT a rendered browser or layout test. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';

const registered = [];
let focused;
class Node {
  constructor(tag = 'div') { this.tagName = tag; this.children = []; this.listeners = {}; this.attrs = {}; this.className = ''; this._text = ''; this.hidden = false; this.disabled = false; this.open = false; registered.push(this); }
  set textContent(value) { this._text = String(value ?? ''); this.children = []; }
  get textContent() { return this._text + this.children.map(n => n.textContent).join(''); }
  set innerHTML(_) { throw Error('Unsafe HTML rendering is forbidden'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ''; this.children = nodes; }
  setAttribute(k, v) { this.attrs[k] = v; }
  getAttribute(k) { return this.attrs[k] ?? null; }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  async emit(type) { for (const fn of this.listeners[type] || []) await fn({stopPropagation() {}}); }
  async click() { if (!this.disabled) await this.emit('click'); }
  focus() { focused = this; }
  scrollIntoView() {}
  get classList() { const node = this; return {add(name) { this.toggle(name, true); }, remove(name) { this.toggle(name, false); }, toggle(name, on) { const values = new Set(node.className.split(/\s+/).filter(Boolean)); if (on) values.add(name); else values.delete(name); node.className = [...values].join(' '); }}; }
  querySelectorAll(selector) { const matches = n => selector.startsWith('.') ? n.className.split(/\s+/).includes(selector.slice(1)) : n.tagName === selector; return this.children.flatMap(n => [...(matches(n) ? [n] : []), ...n.querySelectorAll(selector)]); }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}
const html = fs.readFileSync('web/index.html', 'utf8');
for (const match of html.matchAll(/<([a-z]+)[^>]*\bid="([^"]+)"[^>]*>/g)) { const node = new Node(match[1]); node.id = match[2]; node.hidden = match[0].includes(' hidden'); node.disabled = match[0].includes(' disabled'); }
const doc = {getElementById: id => registered.findLast(n => n.id === id), createElement: tag => new Node(tag)};
const fixture = JSON.parse(execFileSync('python', ['-c', 'import json; from sourcepatch.fixtures import SAMPLE; from sourcepatch.engine import analyze; print(json.dumps({"sample":SAMPLE,"analysis":analyze(SAMPLE)}))'], {encoding:'utf8'}));
const config = {mode:'fixture', sample:fixture.sample};
const exports = [];
const delayed = process.argv.includes('--delayed-config');
let releaseConfig;
const configGate = new Promise(resolve => { releaseConfig = resolve; });
const sandbox = {document:doc, URL, Blob, console, Object, setTimeout, matchMedia:()=>({matches:true}), fetch:async (path, options) => {
  let body;
  if (path === '/api/config') { if (delayed) await configGate; body = config; }
  else if (path === '/api/analyze') { const source = JSON.parse(options.body).source; body = JSON.parse(execFileSync('python', ['-c','import sys,json; from sourcepatch.engine import analyze; print(json.dumps(analyze(sys.stdin.read())))'], {input:source,encoding:'utf8'})); body.analysis_id='local-dom-test'; }
  else if (path === '/api/export') { exports.push(JSON.parse(options.body)); body = {markdown:'patched',diff:'--- a/guide.md\n+++ b/guide.md\n- old\n+ new\n',provenance:{mode:'fixture'}}; }
  else throw Error('Unexpected request ' + path);
  return {ok:true, json:async()=>body};
}};
vm.createContext(sandbox); vm.runInContext(fs.readFileSync('web/app.js','utf8'),sandbox);
const $ = doc.getElementById;
if (delayed) {
  assert.equal($('inspect').disabled, true, 'Inspect stays disabled while config is pending');
  assert.equal($('load-sample').disabled, true, 'Sample loading stays disabled while config is pending');
  await assert.doesNotReject(vm.runInContext('inspect()', sandbox), 'An early direct call must be safe');
  assert.equal(vm.runInContext('state.busy', sandbox), false, 'Early inspection cannot strand busy state');
  releaseConfig();
}
for (let i=0;i<8;i++) await new Promise(resolve=>setImmediate(resolve));
assert.equal($('queue').children.length,5,'fixture queue renders all five citations');
assert.match($('summary').textContent,/5 citations.*0 approved/);
assert.equal($('approve').disabled,true,'approval requires explicit choice');
assert.equal($('preview').disabled,true,'export requires approval');
const select = async index => {const radios=$('review').querySelectorAll('input'); radios.forEach((r,i)=>r.checked=i===index); await radios[index].emit('change');};
await select(0); assert.equal($('approve').disabled,false); await $('approve').click();
assert.match($('summary').textContent,/1 approved/); assert.equal($('preview').disabled,false);
await $('preview').click(); assert.equal($('export-content').hidden,false); assert.match($('diff').textContent,/--- a\/guide/);
assert.equal(Object.keys(exports[0].decisions).length,1);
await $('queue').children[1].click(); assert.match($('review').textContent,/Two close matches/); assert.equal($('approve').disabled,true);
await select(1); await $('approve').click(); assert.match($('summary').textContent,/2 approved/); assert.equal($('export-content').hidden,true,'a new approval invalidates the cached export');
await $('queue').children[0].click(); assert.equal($('approve').disabled,true,'same approved choice cannot be counted twice');
const undo=$('review').querySelectorAll('button').find(n=>n.textContent==='Undo decision'); await undo.click(); assert.match($('summary').textContent,/1 approved/);
await $('queue').children[4].click(); assert.match($('review').textContent,/boundary worth keeping/);
$('source').value='[<img src=x onerror=alert(1)>](https://example.org/test)'; await $('source').emit('input');
assert.equal($('preview').disabled,true,'editing source invalidates decisions'); assert.equal($('queue').children.length,0);
await $('inspect').click(); assert.equal($('queue').children.length,1); assert.match($('queue').textContent,/<img src=x onerror=alert\(1\)>/,'untrusted label stays literal text');
await $('clear-source').click(); assert.equal($('source').value,''); assert.equal(focused,$('source'));
await $('inspect').click(); assert.match($('review').textContent,/No external citations found/);
await $('load-sample').click(); for(let i=0;i<6;i++) await new Promise(resolve=>setImmediate(resolve));
assert.match($('summary').textContent,/5 citations.*0 approved/);
await $('about-button').click(); assert.equal($('about-panel').hidden,false); await $('about-button').click(); assert.equal($('about-panel').hidden,true);
assert.equal($('error').hidden,true,'no application errors from actual app.js execution');
console.log(`PASS: ${delayed ? 32 : 28} DOM-contract assertions (fixture load, choice, approval, ambiguity, export, undo, blocked source, stale input, hostile label, empty state, reload, about panel${delayed ? ', delayed configuration' : ''}).`);
console.log('Scope: executes real app.js against a small DOM-contract harness. No browser layout, CSS, keyboard behavior or visual verification claimed.');
