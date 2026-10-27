#!/usr/bin/env node
/**
 * Verificador de links do site.
 * Rastreia todas as páginas internas a partir de uma URL base e confere que cada link
 * (href de <a>, src de <img>/<script>, href de <link>) responde com status 2xx/3xx.
 *
 * Uso: node scripts/check-links.mjs http://127.0.0.1:3100 [--external]
 *   --external  também testa links externos (http/https de outros domínios)
 *
 * Sai com código 1 se houver qualquer link quebrado.
 */
const base = process.argv[2] || "http://127.0.0.1:3100";
const checkExternal = process.argv.includes("--external");
const origin = new URL(base).origin;

const seen = new Set();
const queue = ["/"];
const broken = [];
const ok = new Set();

function normalize(href, from) {
  try {
    const url = new URL(href, from);
    url.hash = "";
    return url;
  } catch {
    return null;
  }
}

async function status(url) {
  try {
    const res = await fetch(url, { redirect: "manual", headers: { "user-agent": "nexus-link-check" } });
    return res.status;
  } catch (error) {
    return `ERR ${error.message}`;
  }
}

while (queue.length) {
  const path = queue.shift();
  if (seen.has(path)) continue;
  seen.add(path);
  const pageUrl = origin + path;
  const res = await fetch(pageUrl, { headers: { "user-agent": "nexus-link-check" } });
  if (!res.ok) {
    broken.push({ from: "(crawl)", href: path, status: res.status });
    continue;
  }
  const html = await res.text();
  const refs = [...html.matchAll(/(?:href|src)="([^"]+)"/g)]
    .map((m) => m[1].replace(/&amp;/g, "&"))
    .filter((h) => !h.startsWith("data:"));
  for (const href of new Set(refs)) {
    if (/^(mailto:|tel:|javascript:|#)/.test(href)) continue;
    const url = normalize(href, pageUrl);
    if (!url) continue;
    const key = url.href;
    if (ok.has(key)) continue;
    if (url.origin === origin) {
      if (url.pathname.startsWith("/_next/") || /\.(css|js|jpg|jpeg|png|webp|svg|woff2?|ico)$/.test(url.pathname)) {
        const s = await status(key);
        if (typeof s !== "number" || s >= 400) broken.push({ from: path, href, status: s });
        else ok.add(key);
      } else {
        const s = await status(key);
        if (typeof s !== "number" || s >= 400) broken.push({ from: path, href, status: s });
        else {
          ok.add(key);
          if (!seen.has(url.pathname)) queue.push(url.pathname);
        }
      }
    } else if (checkExternal) {
      const s = await status(key);
      if (typeof s !== "number" || s >= 400) broken.push({ from: path, href, status: s });
      else ok.add(key);
    }
  }
}

console.log(`Páginas rastreadas: ${seen.size} | links OK: ${ok.size} | quebrados: ${broken.length}`);
for (const item of broken) console.log(`  ✗ ${item.status}  ${item.href}  (em ${item.from})`);
process.exit(broken.length ? 1 : 0);
