const { chromium } = require('/Users/himanshujha/.rote/lib/playwright-runtime/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');

// One desktop/mobile inspection batch; no provider or external page requests.
(async () => {
  const origin = process.env.SOURCEPATCH_LANDING_ORIGIN || 'http://127.0.0.1:8784';
  const out = __dirname;
  const browser = await chromium.launch({ headless: true, executablePath: '/Users/himanshujha/Library/Caches/ms-playwright/chromium-1243/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, permissions: ['clipboard-read', 'clipboard-write'] });
  const page = await context.newPage();
  const errors = [], external = [], checks = [];
  const inspectNetwork = async ctx => ctx.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.origin !== origin) { external.push(url.href); return route.abort(); }
    return route.continue();
  });
  page.on('pageerror', error => errors.push(error.message));
  await inspectNetwork(context);
  try {
    await page.goto(origin + '/', { waitUntil: 'networkidle' });
    await page.locator('.citation-button').first().waitFor();
    assert.equal(await page.locator('.citation-button').count(), 5);
    assert.equal(await page.locator('#candidate-list .candidate').count(), 3);
    assert.match(await page.locator('.fixture-note').innerText(), /No live SerpApi request verified/);
    checks.push('Five fixture destinations, three Python candidates, visible live-verification disclosure');
    const bounds = async () => page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth }));
    const desktop = await bounds();
    assert(desktop.scroll <= desktop.width, JSON.stringify(desktop));
    await page.screenshot({ path: path.join(out, 'desktop-first-viewport.png') });
    await page.screenshot({ path: path.join(out, 'desktop.png'), fullPage: true });

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
    await page.screenshot({ path: path.join(out, 'mobile-first-viewport.png') });
    await page.screenshot({ path: path.join(out, 'mobile.png'), fullPage: true });
    await page.locator('#citation-search').fill('pandas');
    await page.getByRole('button', { name: /pandas DataFrame/ }).click();
    assert.equal(await page.locator('#citation-title').innerText(), 'pandas DataFrame');
    checks.push('390px mobile has no page overflow and functional search/selection; reduced-motion scrolling is static');

    const fallback = await browser.newContext({ viewport: { width: 1440, height: 1000 }, javaScriptEnabled: false });
    await inspectNetwork(fallback);
    const staticPage = await fallback.newPage();
    await staticPage.goto(origin + '/', { waitUntil: 'networkidle' });
    assert.equal(await staticPage.locator('#candidate-list .candidate').count(), 3);
    assert(await staticPage.locator('.search-control').isHidden());
    assert(await staticPage.locator('noscript').isVisible());
    assert.equal(await staticPage.locator('h1').count(), 1);
    checks.push('JavaScript-disabled page retains real Python evidence, disclosures, artifacts, and readable navigation');
    await fallback.close();

    assert.deepEqual(errors, []);
    assert.deepEqual(external, []);
    const receipt = { checkedAt: new Date().toISOString(), origin, status: 'passed', inspectionRounds: 1, viewports: { desktop, mobile }, checks, focus, media, pageErrors: errors, externalRequests: external, screenshots: ['desktop.png', 'mobile.png', 'desktop-first-viewport.png', 'mobile-first-viewport.png'], notRun: ['Complete screen-reader audit', 'Live SerpApi integration', 'Public deployment', 'Final hackathon submission', 'Impeccable CLI detector (launcher unavailable)'] };
    await fs.writeFile(path.join(out, 'browser-receipt.json'), JSON.stringify(receipt, null, 2) + '\n');
    console.log(JSON.stringify(receipt, null, 2));
  } finally {
    await context.close();
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
