const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
const [,, pageName, w, h, out, full] = process.argv;
const b = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROMIUM });
const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
await p.goto(`http://127.0.0.1:3700/${pageName}`, { waitUntil: 'networkidle' });
await p.evaluate(async () => { document.querySelectorAll('img[loading="lazy"]').forEach(i => { i.loading = 'eager'; }); for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))); await new Promise(r => setTimeout(r, 300)); });
await p.waitForTimeout(800);
await p.screenshot({ path: out, fullPage: full === 'full' });
await b.close();
