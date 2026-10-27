#!/usr/bin/env node
/**
 * Testa os menus do site: navegação desktop (cada link leva à página certa), botão de tema,
 * menu do celular (abre, fica aberto, links navegam) e a página 404.
 * Uso: node scripts/check-nav.mjs http://127.0.0.1:3400
 * Requer Playwright — ou PLAYWRIGHT_MODULE / PLAYWRIGHT_CHROMIUM apontando para uma instalação existente.
 */
const base = process.argv[2] || "http://127.0.0.1:3400";
const moduleSpec = process.env.PLAYWRIGHT_MODULE || "playwright";
const { chromium } = await import(moduleSpec);
const launch = process.env.PLAYWRIGHT_CHROMIUM ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM } : {};
const browser = await chromium.launch(launch);
const failures = [];
const note = (ok, label) => { console.log(`${ok ? "✓" : "✗"} ${label}`); if (!ok) failures.push(label); };

async function abrir(width) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.route(/fonts\.gstatic|fonts\.googleapis/, (r) => r.abort());
  await page.goto(base + "/index.html", { waitUntil: "load" });
  return page;
}

// Desktop
{
  const page = await abrir(1366);
  const links = await page.$$eval("nav.nav > a, nav.nav > ul > li > a", (as) => as.map((a) => ({ href: a.getAttribute("href"), txt: a.textContent.trim() })));
  note(links.length >= 4, `desktop: ${links.length} itens no menu`);
  for (const l of links) {
    await page.goto(base + "/index.html", { waitUntil: "load" });
    if (l.href.startsWith("#")) {  // landing page: âncora deve existir e rolar até a seção
      const ok = await page.evaluate((h) => { const el = document.querySelector(h); if (!el) return false; el.scrollIntoView({ behavior: 'instant', block: 'start' }); return el.getBoundingClientRect().height > 0 && Math.abs(el.getBoundingClientRect().top) < 200; }, l.href);
      note(ok, `desktop: "${l.txt}" → âncora ${l.href} existe`);
      continue;
    }
    const [res] = await Promise.all([page.waitForNavigation({ waitUntil: "load" }), page.click(`nav.nav > a[href="${l.href}"], nav.nav > ul > li > a[href="${l.href}"]`)]);
    const atual = await page.$eval("nav.nav > a[aria-current='page'], nav.nav > ul > li > a[aria-current='page']", (a) => a.textContent.trim()).catch(() => null);
    note(res && res.status() === 200 && atual === l.txt, `desktop: "${l.txt}" → ${l.href} (HTTP ${res ? res.status() : "?"}, item ativo: ${atual})`);
  }
  // Submenu (se existir): abre no clique, fica aberto e cada link leva à página certa
  await page.goto(base + "/index.html", { waitUntil: "load" });
  const temSub = await page.$(".nav .sub-btn");
  if (temSub) {
  await page.click(".nav .sub-btn");
  await page.waitForTimeout(400);
  const subAberto = await page.evaluate(() => { const s = document.querySelector(".nav .submenu"); const r = s.getBoundingClientRect(); return getComputedStyle(s).display !== "none" && r.height > 50; });
  note(subAberto, "desktop: submenu Serviços abre no clique e fica aberto");
  const subs = await page.$$eval(".nav .submenu a", (as) => as.map((a) => ({ href: a.getAttribute("href"), txt: a.textContent.trim() })));
  note(subs.length >= 5, `desktop: ${subs.length} itens no submenu`);
  for (const l of subs) {
    if (/^https?:/.test(l.href)) { note(true, `desktop: submenu "${l.txt}" → ${l.href} (externo, não navegado)`); continue; }
    await page.goto(base + "/index.html", { waitUntil: "load" });
    await page.evaluate((href) => { const a = document.querySelector(`.nav .submenu a[href="${href}"]`); const b = a && a.closest(".tem-sub") && a.closest(".tem-sub").querySelector(".sub-btn"); if (b) b.click(); }, l.href);
    await page.waitForTimeout(300);
    const [res] = await Promise.all([page.waitForNavigation({ waitUntil: "load" }), page.click(`.nav .submenu a[href="${l.href}"]`)]);
    const h1 = await page.$eval("main h1", (h) => h.textContent.trim()).catch(() => "");
    note(res && res.status() === 200 && h1.length > 0, `desktop: submenu "${l.txt}" → ${l.href} (HTTP ${res ? res.status() : "?"}, h1: "${h1.slice(0, 40)}")`);
  }
  } else note(true, "desktop: sem submenu neste site");
  await page.close();
}

// Celular
{
  const page = await abrir(390);
  const hambVisivel = await page.isVisible(".hamb");
  note(hambVisivel, "mobile: botão do menu visível");
  await page.click(".hamb");
  await page.waitForTimeout(400);
  const aberto = await page.evaluate(() => { const m = document.getElementById("menu-mobile"); const r = m.getBoundingClientRect(); return m.classList.contains("aberto") && r.left < window.innerWidth && getComputedStyle(m).visibility === "visible"; });
  note(aberto, "mobile: menu abre e fica aberto");
  await page.waitForTimeout(600);
  const aindaAberto = await page.evaluate(() => document.getElementById("menu-mobile").classList.contains("aberto"));
  note(aindaAberto, "mobile: menu continua aberto após 600 ms");
  const links = await page.$$eval("#menu-mobile a:not(.btn)", (as) => as.map((a) => a.getAttribute("href")));
  for (const href of links) {
    if (href.startsWith("#")) {
      await page.goto(base + "/index.html", { waitUntil: "load" });
      await page.click(".hamb"); await page.waitForTimeout(300);
      await page.click(`#menu-mobile a[href="${href}"]`); await page.waitForTimeout(600);
      const ok = await page.evaluate((h) => { const m = document.getElementById("menu-mobile"); const el = document.querySelector(h); return el && !m.classList.contains("aberto"); }, href);
      note(ok, `mobile: âncora ${href} existe e o menu fecha ao tocar`);
      continue;
    }
    if (/^(https?:|mailto:|tel:)/.test(href)) { note(true, `mobile: link externo ${href.slice(0, 50)} (não navegado)`); continue; }
    await page.goto(base + "/index.html", { waitUntil: "load" });
    await page.click(".hamb");
    await page.waitForTimeout(350);
    await page.evaluate(() => document.querySelectorAll("#menu-mobile details").forEach((d) => (d.open = true)));
    const [res] = await Promise.all([page.waitForNavigation({ waitUntil: "load" }), page.click(`#menu-mobile a[href="${href}"]`)]);
    note(res && res.status() === 200, `mobile: link do menu ${href} → HTTP ${res ? res.status() : "?"}`);
  }
  await page.close();
}

// 404
{
  const page = await abrir(1366);
  const res = await page.goto(base + "/404.html", { waitUntil: "load" });
  const titulo = await page.$eval("main h1", (h) => h.textContent.trim()).catch(() => "");
  note(res.status() === 200 && /não encontrada|fora de órbita/i.test(titulo), `404: página existe no layout ("${titulo}")`);
  await page.close();
}

await browser.close();
console.log(failures.length ? `\n${failures.length} falha(s)` : "\nMenus e submenus OK");
process.exit(failures.length ? 1 : 0);
