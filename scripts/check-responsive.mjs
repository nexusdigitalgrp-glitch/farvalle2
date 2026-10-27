#!/usr/bin/env node
/**
 * Regra: TODO site deve ser responsivo. Este teste abre cada página em várias larguras
 * (de 320px a 2560px) e falha se houver rolagem horizontal ou elemento saindo da tela.
 *
 * Uso: node scripts/check-responsive.mjs http://127.0.0.1:3000 [/rota /rota2 ...]
 * Requer Playwright — ou PLAYWRIGHT_MODULE / PLAYWRIGHT_CHROMIUM apontando para uma instalação existente.
 * Sai com código 1 se alguma página estourar a largura em alguma resolução.
 */
const base = process.argv[2] || "http://127.0.0.1:3000";
const routes = process.argv.length > 3
  ? process.argv.slice(3)
  : ["/index.html", "/servicos.html", "/especialidades.html", "/odontologia.html", "/exames.html", "/fisioterapia.html", "/nutricao.html", "/unidades.html", "/sobre.html", "/contato.html", "/privacidade.html", "/404.html"];
const widths = [320, 360, 390, 430, 540, 600, 700, 768, 820, 900, 1024, 1100, 1180, 1200, 1280, 1366, 1440, 1600, 1920, 2560, 3840, 5120];

const moduleSpec = process.env.PLAYWRIGHT_MODULE || "playwright";
const { chromium } = await import(moduleSpec);
const launch = process.env.PLAYWRIGHT_CHROMIUM ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM } : {};
const browser = await chromium.launch(launch);
const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
await page.route(/fonts\.gstatic|google\.com/, (r) => r.abort());

let failures = 0;
for (const route of routes) {
  await page.setViewportSize({ width: 1366, height: 900 });
  const res = await page.goto(base + route, { waitUntil: "load" });
  if (!res || res.status() >= 400 && route !== "/404.html") {
    console.log(`✗ ${route}: HTTP ${res ? res.status() : "sem resposta"}`);
    failures++;
    continue;
  }
  const problems = [];
  for (const width of widths) {
    await page.setViewportSize({ width, height: 900 });
    await page.waitForTimeout(120);
    const r = await page.evaluate(() => {
      const cw = document.documentElement.clientWidth;
      const out = [];
      for (const el of document.querySelectorAll("body *")) {
        const b = el.getBoundingClientRect();
        // Ignora o que está oculto (ex.: painel do menu mobile fechado, fora da tela de propósito)
        const visible = typeof el.checkVisibility === "function" ? el.checkVisibility({ visibilityProperty: true, opacityProperty: true }) : true;
        if (!visible || b.width === 0 || getComputedStyle(el).position === "fixed") continue;
        // Partes internas de um SVG e elementos dentro de um pai com overflow hidden/clip/auto/scroll (recorte ou carrossel) não geram rolagem da página
        if (el.ownerSVGElement) continue;
        let clipped = false;
        for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
          const ov = getComputedStyle(a).overflowX;
          if (ov === "hidden" || ov === "clip" || ov === "auto" || ov === "scroll") { clipped = true; break; }
        }
        if (clipped) continue;
        if (b.right > cw + 1 || b.left < -1) {
          const cls = (el.className?.baseVal ?? el.className ?? "").toString().slice(0, 40);
          out.push(`${el.tagName.toLowerCase()}.${cls} (${Math.round(b.left)}–${Math.round(b.right)})`);
        }
      }
      return { scrollWidth: document.documentElement.scrollWidth, clientWidth: cw, out: out.slice(0, 5) };
    });
    if (r.scrollWidth > r.clientWidth || r.out.length) problems.push({ width, ...r });
  }
  if (problems.length) {
    failures++;
    console.log(`✗ ${route}: estoura a largura em ${problems.map((p) => p.width + "px").join(", ")}`);
    for (const p of problems) console.log(`    ${p.width}px → scroll ${p.scrollWidth}/${p.clientWidth}; ${p.out.join("; ")}`);
  } else {
    console.log(`✓ ${route}: ok em ${widths.length} larguras (${widths[0]}–${widths[widths.length - 1]}px)`);
  }
}
await browser.close();
console.log(failures ? `\n${failures} página(s) com problema de responsividade` : "\nResponsividade OK");
process.exit(failures ? 1 : 0);
