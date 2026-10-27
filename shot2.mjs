const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
const [,, pageName, w, h, out, sel] = process.argv;
const b = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROMIUM });
const p = await b.newPage({ viewport: { width: +w, height: +h } });
await p.goto(`http://127.0.0.1:3700/${pageName}`, { waitUntil: 'networkidle' });
await p.locator(sel).first().scrollIntoViewIfNeeded();
await p.waitForTimeout(1200);
await p.screenshot({ path: out });
await b.close();
