// Títulos h1/h2 com no máximo 2 linhas no celular (390px). Uso: node check-titulos.mjs <base> [slug ...]
const moduleSpec = process.env.PLAYWRIGHT_MODULE || 'playwright';
const { chromium } = await import(moduleSpec);
const launch = process.env.PLAYWRIGHT_CHROMIUM ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM } : {};
const browser = await chromium.launch(launch);
const page = await browser.newPage({ viewport: { width: 390, height: 780 } });
await page.route(/fonts\.gstatic|fonts\.googleapis/, r => r.abort());
let bad = 0;
const paginas = process.argv.length > 3 ? process.argv.slice(3) : ['index','areas','penal','previdenciario','tributario','administrativo','civil','socios','escritorio','contato','privacidade','404'];
for (const p of paginas) {
  await page.goto((process.argv[2] || 'http://127.0.0.1:3400') + '/' + p + '.html', { waitUntil: 'load' });
  const r = await page.evaluate(() => [...document.querySelectorAll('h1, h2')].map(h => { const lh = parseFloat(getComputedStyle(h).lineHeight); return [h.textContent.trim().slice(0, 50), Math.round(h.getBoundingClientRect().height / lh)]; }));
  for (const [t, n] of r) if (n > 2) { bad++; console.log('✗', p, n, 'linhas:', t); }
}
console.log(bad ? bad + ' título(s) com mais de 2 linhas' : '✓ todos os títulos com até 2 linhas no celular (390px)');
await browser.close();
