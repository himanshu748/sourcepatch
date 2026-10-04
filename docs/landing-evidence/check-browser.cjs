const { chromium } = require('/Users/himanshujha/.rote/lib/playwright-runtime/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');

// One desktop/mobile inspection batch; no provider or external page requests.
(async () => {
  const origin = process.env.SOURCEPATCH_LANDING_ORIGIN || 'http://127.0.0.1:8784';
  const out = process.env.SOURCEPATCH_LANDING_EVIDENCE_DIR ? path.resolve(process.env.SOURCEPATCH_LANDING_EVIDENCE_DIR) : __dirname;
  await fs.mkdir(out, { recursive: true });
  const confirmation = process.env.SOURCEPATCH_LANDING_CONFIRMATION === '1';
  const browser = await chromium.launch({ headless: true, executablePath: '/Users/himanshujha/Library/Caches/ms-playwright/chromium-1243/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, permissions: ['clipboard-read', 'clipboard-write'] });
  const retainedContexts = [context];
  const page = await context.newPage();
  const errors = [], consoleIssues = [], external = [], checks = [];
  const inspectNetwork = async ctx => ctx.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.origin !== origin) { external.push(url.href); return route.abort(); }
    return route.continue();
  });
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (['error', 'warning'].includes(message.type())) consoleIssues.push({ type: message.type(), text: message.text() }); });
  await inspectNetwork(context);
  try {
    await page.goto(origin + '/', { waitUntil: 'networkidle' });
    assert.equal(page.url(), origin + '/');
    assert.match(await page.title(), /^SourcePatch — Keep the knowledge/);
    assert.match(await page.locator('h1').innerText(), /Keep the knowledge/);
    assert((await page.locator('body').innerText()).length > 2000);
    assert.equal(await page.locator('nextjs-portal, vite-error-overlay, #webpack-dev-server-client-overlay').count(), 0);
    checks.push('Expected page identity, meaningful nonblank content, and no framework overlay');
    await page.locator('.citation-button').first().waitFor();
    assert.equal(await page.locator('.citation-button').count(), 5);
    assert.equal(await page.locator('#candidate-list .candidate').count(), 3);
    assert.match(await page.locator('.fixture-note').innerText(), /No live SerpApi request verified/);
    checks.push('Five fixture destinations, three Python candidates, visible live-verification disclosure');
    const bounds = async () => page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth }));
    const readEvidence = async () => page.evaluate(() => {
      const selectors = ['.fixture-note', '.record-stamp', '.destination-label', '.destination code', '.evidence-pair', '.record-caution', '.badge', '.record-meta', '.original-reference > span', '.original-reference code', '.review-notice', '.candidate-header > span', '.candidate-title h5', '.candidate-title > span', '.candidate > code', '.candidate > p', '.candidate-reasons li', '.query-details', '.record-footer', '.patch-proof > p', '.demo-video figcaption', '.live-note', '.truth-ledger > div', '.sidebar-note', '.citation-button .host', '.row-meta .occurrences'];
      return selectors.flatMap(selector => Array.from(document.querySelectorAll(selector)).filter(node => node.getBoundingClientRect().height > 0).map(node => ({ selector, fontSize: parseFloat(getComputedStyle(node).fontSize), overflow: node.scrollWidth > node.clientWidth + 1 })));
    });
    const desktop = await bounds();
    assert(desktop.scroll <= desktop.width, JSON.stringify(desktop));
    const desktopEvidence = await readEvidence();
    assert(desktopEvidence.every(row => row.fontSize >= 14), JSON.stringify(desktopEvidence.filter(row => row.fontSize < 14)));
    assert(desktopEvidence.every(row => !row.overflow), JSON.stringify(desktopEvidence.filter(row => row.overflow)));
    await page.screenshot({ path: path.join(out, 'desktop-first-viewport.png') });
    await page.screenshot({ path: path.join(out, 'desktop.png'), fullPage: true });
    if (confirmation) {
      await page.locator('#evidence-record').evaluate(node => node.scrollIntoView({ block: 'start', behavior: 'instant' }));
      await page.screenshot({ path: path.join(out, 'desktop-evidence.png') });
    }

    await page.locator('#citation-search').fill('fetch');
    assert.equal(await page.locator('.citation-button').count(), 1);
    await page.keyboard.press('Tab');
    const focus = await page.evaluate(() => ({ tag: document.activeElement.tagName, outline: getComputedStyle(document.activeElement).outlineStyle, width: getComputedStyle(document.activeElement).outlineWidth }));
    assert.equal(focus.tag, 'BUTTON');
    assert.equal(focus.outline, 'solid');
    assert.equal(focus.width, '3px');
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#citation-title').innerText(), 'Abort a fetch request');
    assert.match(await page.locator('#review-notice').innerText(), /Two candidates share the highest score/);
    assert.equal(await page.locator('#candidate-list .candidate').count(), 2);
    assert.deepEqual(await page.locator('.candidate-title > span').allTextContents(), ['91 / 100', '91 / 100']);
    assert.equal(await page.locator('.citation-button').getAttribute('aria-pressed'), 'true');
    await page.locator('.query-details summary').click();
    assert.match(await page.locator('#discovery-query').innerText(), /site:developer.mozilla.org/);
    await page.locator('.query-details summary').click();
    checks.push('Keyboard search/selection with visible 3px focus; equal-score ambiguity and exact query exposed');

    await page.locator('#citation-search').fill('<img src=x onerror=alert(1)>');
    assert.equal(await page.locator('.citation-button').count(), 0);
    assert.match(await page.locator('#search-status').innerText(), /No fixture citations match/);
    assert.equal(await page.locator('#citation-title').innerText(), 'Abort a fetch request');
    checks.push('Hostile/no-match search is literal and recoverable; current evidence preserved');

    await page.locator('#citation-search').fill('');
    await page.getByRole('button', { name: /Python dataclasses/ }).click();
    assert.equal(await page.locator('#candidate-list .candidate').count(), 0);
    assert.match(await page.locator('#review-notice').innerText(), /not a live HTTP observation/);
    await page.getByRole('button', { name: /private team dashboard/ }).click();
    assert.match(await page.locator('#review-notice').innerText(), /blocked before any request/);
    assert.equal(await page.locator('#candidate-list .candidate').count(), 0);
    checks.push('Reachable and blocked destinations have truthful no-candidate states');

    for (const asset of ['demo-output/sourcepatch.diff', 'demo-output/provenance.json', 'demo-output/guide.patched.md', 'docs/demo-script.md', 'assets/sourcepatch-fixture-labelled.mp4']) {
      const response = await context.request.get(origin + '/' + asset);
      assert.equal(response.status(), 200, asset);
      if (asset.endsWith('provenance.json')) {
        const report = await response.json();
        assert.equal(report.mode, 'fixture');
        assert.equal(report.changes[0].approved_by_user, false);
      }
    }
    checks.push('Portable sample diff/provenance/Markdown/walkthrough/video links return 200; hypothetical approval preserved');

    const media = await page.locator('video').evaluate(video => ({ preload: video.preload, autoplay: video.autoplay, controls: video.controls, paused: video.paused }));
    assert.deepEqual(media, { preload: 'none', autoplay: false, controls: true, paused: true });
    checks.push('Real fixture video has controls, no autoplay, and no media preload');
    await page.locator('#copy-command').click();
    await page.waitForFunction(() => document.querySelector('#copy-status').textContent.startsWith('Command copied'));
    assert.equal(await page.evaluate(() => navigator.clipboard.readText()), 'python3 -m sourcepatch');
    checks.push('Local launch command copies accurately to the clipboard');

    await page.emulateMedia({ reducedMotion: 'reduce' });
    assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior), 'auto');
    await page.getByRole('button', { name: /Python pathlib/ }).click();
    await page.setViewportSize({ width: 390, height: 844 });
    await page.evaluate(() => scrollTo(0, 0));
    const mobile = await bounds();
    assert(mobile.scroll <= mobile.width, JSON.stringify(mobile));
    const mobileEvidence = await readEvidence();
    assert(mobileEvidence.every(row => row.fontSize >= 14), JSON.stringify(mobileEvidence.filter(row => row.fontSize < 14)));
    assert(mobileEvidence.every(row => !row.overflow), JSON.stringify(mobileEvidence.filter(row => row.overflow)));
    checks.push('Meaningful evidence/disclosure text is at least 14px at both widths; measured evidence elements wrap without horizontal clipping');
    await page.screenshot({ path: path.join(out, 'mobile-first-viewport.png') });
    await page.screenshot({ path: path.join(out, 'mobile.png'), fullPage: true });
    if (confirmation) {
      await page.locator('#evidence-record').evaluate(node => node.scrollIntoView({ block: 'start', behavior: 'instant' }));
      await page.screenshot({ path: path.join(out, 'mobile-evidence.png') });
    }
    await page.locator('#citation-search').fill('pandas');
    await page.getByRole('button', { name: /pandas DataFrame/ }).click();
    assert.equal(await page.locator('#citation-title').innerText(), 'pandas DataFrame');
    checks.push('390px mobile has no page overflow and functional search/selection; reduced-motion scrolling is static');

    const fallback = await browser.newContext({ viewport: { width: 1440, height: 1000 }, javaScriptEnabled: false });
    retainedContexts.push(fallback);
    await inspectNetwork(fallback);
    const staticPage = await fallback.newPage();
    await staticPage.goto(origin + '/', { waitUntil: 'networkidle' });
    assert.equal(await staticPage.locator('#candidate-list .candidate').count(), 3);
    assert(await staticPage.locator('.search-control').isHidden());
    assert(await staticPage.locator('noscript').isVisible());
    assert.equal(await staticPage.locator('h1').count(), 1);
    checks.push('JavaScript-disabled page retains real Python evidence, disclosures, artifacts, and readable navigation');

    assert.deepEqual(errors, []);
    assert.deepEqual(consoleIssues, []);
    assert.deepEqual(external, []);
    const screenshots = ['desktop.png', 'mobile.png', 'desktop-first-viewport.png', 'mobile-first-viewport.png'];
    if (confirmation) screenshots.push('desktop-evidence.png', 'mobile-evidence.png');
    const receipt = { checkedAt: new Date().toISOString(), origin, status: 'passed', inspectionRounds: confirmation ? 2 : 1, confirmationRounds: confirmation ? 1 : 0, browserAvailability: 'Absent', fallbackReason: 'Browser plugin not available; Browser/IAB tools and browser skill absent from this Mac session', flowUnderTest: 'Landing loads -> select fixture citation -> evidence, caveats and disclosures remain readable on desktop/mobile', viewports: { desktop, mobile }, evidenceTypography: { desktop: desktopEvidence, mobile: mobileEvidence }, checks, focus, media, pageErrors: errors, consoleIssues, externalRequests: external, screenshots, notRun: ['Complete screen-reader audit', 'Live SerpApi integration', 'Public deployment', 'Final hackathon submission', 'Impeccable CLI detector (launcher unavailable)'] };
    await fs.writeFile(path.join(out, 'browser-receipt.json'), JSON.stringify(receipt, null, 2) + '\n');
    console.log(JSON.stringify(receipt, null, 2));
  } finally {
    // Preserve the owned browser, every context and the Playwright driver.
    // Do not exit or close them after verification; leave this process idle.
    console.log('Verification finished. Owned browser, contexts and driver retained idle; no automatic cleanup.');
    setInterval(() => { void browser; void retainedContexts; }, 60000);
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
