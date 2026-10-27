#!/usr/bin/env python3
"""Gera a pasta preview/ (cópia de dist/) para publicar como artefato claude.ai:
- links externos e mailto passam pela casca (o iframe do artefato não pode abrir janelas);
- casca (preview/_shell.html → publicada como página do artefato) com modos Desktop/Tablet/Celular/Livre,
  tela cheia mantendo a proporção e sem barra de rolagem visível.
Uso: python3 scripts/preview.py
"""
import pathlib, shutil, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DIST = RAIZ / "dist"
PREV = RAIZ / "preview"

MAPA_RE = re.compile(r'<iframe class="mapa-frame"[^>]*></iframe>')
MAPA_IMG = ('<a class="mapa-frame mapa-frame-img" href="https://www.google.com/maps/dir/?api=1&destination=-13.0306631,-39.5988695" target="_blank" rel="noopener noreferrer">'
            '<img src="assets/img/mapa.jpg" srcset="assets/img/mapa.jpg 1x, assets/img/mapa@2x.jpg 2x" alt="Mapa com a localização da MS Barbearia Premium" loading="lazy" decoding="async">'
            '<span class="mapa-aviso">Prévia: no site publicado este mapa é interativo (Google Maps)</span></a>')

INTERCEPT = (
    '<script>document.addEventListener("click",function(e){var a=e.target&&e.target.closest?e.target.closest("a[href]"):null;'
    'if(!a||window.parent===window)return;var u=a.getAttribute("href")||"";'
    'if(/^mailto:/.test(u)||(/^https?:/.test(u)&&(a.target==="_blank"||new URL(a.href).origin!==location.origin))){'
    'e.preventDefault();e.stopPropagation();window.parent.postMessage({fvOpen:a.href},"*")}},true);</script>'
)

SHELL = r'''<meta charset="utf-8">
<title>Farvalle 2 — Prévia</title>
<style>
  :root { --bg: #0b0b0c; --fg: #e8ecf5; --muted: #aab3c7; --accent: #C9993B; --bar: 38px; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #070708; color-scheme: dark } }
  :root[data-theme="dark"] { --bg: #070708; color-scheme: dark }
  html, body { height: 100%; }
  body { margin: 0; background: var(--bg); color: var(--fg); font: 500 13px/1.3 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; overflow: hidden; }
  .bar { height: var(--bar); flex: 0 0 auto; display: flex; align-items: center; gap: 12px; padding: 0 12px; padding-top: env(safe-area-inset-top, 0px); }
  .bar b { color: var(--accent); letter-spacing: .04em; text-transform: uppercase; font-size: 11px; }
  .bar span { color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; flex: 1; }
  .seg { display: flex; gap: 2px; background: rgba(255,255,255,.08); padding: 3px; border-radius: 999px; }
  .seg button { border: 0; background: transparent; color: var(--muted); font: inherit; font-size: 12px; padding: 4px 10px; border-radius: 999px; cursor: pointer; white-space: nowrap; }
  .seg button[aria-pressed="true"] { background: var(--accent); color: #fff; }
  .seg button:focus-visible { outline: 2px solid #fff; outline-offset: 1px; }
  .stage { flex: 1 1 auto; position: relative; overflow: hidden; background: #0b0b0c; }
  iframe { position: absolute; top: 0; left: 0; border: 0; background: #0b0b0c; transform-origin: 0 0; }
  .toast { position: absolute; left: 50%; bottom: 14px; transform: translateX(-50%); background: #1a1a1d; color: #fff; padding: 10px 14px; border-radius: 10px; font-size: 13px; box-shadow: 0 10px 30px rgba(0,0,0,.45); display: none; max-width: calc(100% - 32px); border: 1px solid rgba(255,255,255,.12); }
  .toast a { color: #7dd3fc; font-weight: 700; }
  @media (max-width: 560px) { .bar span { display: none; } .seg button { padding: 4px 8px; } }
</style>
<div class="bar">
  <b>Prévia</b>
  <span>Farvalle 2 · proposta de novo site pela Nexus Digital Group · ainda não publicado</span>
  <div class="seg" role="group" aria-label="Modo de visualização">
    <button type="button" data-mode="desktop">Desktop</button>
    <button type="button" data-mode="tablet">Tablet</button>
    <button type="button" data-mode="mobile">Celular</button>
    <button type="button" data-mode="free" title="Ocupa a largura real da janela: redimensione para ver o site se adaptar">Livre</button>
  </div>
</div>
<div class="stage">
  <iframe id="site" src="home.html" title="Prévia do site Farvalle 2"></iframe>
  <div class="toast" id="toast" role="status"></div>
</div>
<script>
  (function () {
    var stage = document.querySelector('.stage'), frame = document.getElementById('site'), toast = document.getElementById('toast');
    var buttons = Array.prototype.slice.call(document.querySelectorAll('.seg button'));
    var KEY = 'ms-preview-mode', mode = 'desktop';
    try { mode = localStorage.getItem(KEY) || 'desktop'; } catch (e) {}
    if (!buttons.some(function (b) { return b.dataset.mode === mode; })) mode = 'desktop';
    function layout() {
      var w = stage.clientWidth, h = stage.clientHeight;
      var target = mode === 'desktop' ? 1366 : mode === 'tablet' ? 1024 : mode === 'mobile' ? 390 : w;
      if (mode === 'free') { frame.style.width = w + 'px'; frame.style.height = h + 'px'; frame.style.transform = 'none'; }
      else {
        var scale = mode === 'mobile' ? Math.min(w / target, h / 780) : w / target;
        var left = Math.round((w - target * scale) / 2);
        frame.style.width = target + 'px'; frame.style.height = Math.round(h / scale) + 'px';
        frame.style.transform = 'translateX(' + left + 'px) scale(' + scale + ')';
      }
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.mode === mode)); });
    }
    function set(m) { mode = m; try { localStorage.setItem(KEY, m); } catch (e) {} layout(); }
    buttons.forEach(function (b) { b.addEventListener('click', function () { set(b.dataset.mode); }); });
    window.addEventListener('resize', layout);
    layout();
    var timer;
    function aviso(html) { toast.innerHTML = html; toast.style.display = 'block'; clearTimeout(timer); timer = setTimeout(function () { toast.style.display = 'none'; }, 9000); }
    window.addEventListener('message', function (e) {
      var url = e.data && e.data.fvOpen; if (typeof url !== 'string') return;
      if (/^mailto:/.test(url)) {
        var end = url.replace(/^mailto:/, '').split('?')[0];
        aviso('No site publicado este botão abre o seu e-mail: <a href="' + url.replace(/"/g, '&quot;') + '">escrever para ' + end + '</a>');
        return;
      }
      if (!/^https?:\/\//.test(url)) return;
      var win = null; try { win = window.open(url, '_blank'); if (win) { try { win.opener = null; } catch (e2) {} } } catch (err) {}
      if (win === null) aviso('Este link abre fora da prévia: <a href="' + url + '" target="_blank" rel="noopener noreferrer">abrir ' + url.replace(/^https?:\/\/([^\/]+).*$/, '$1') + '</a>');
    });
  })();
</script>
'''


def main():
    if PREV.exists():
        shutil.rmtree(PREV)
    shutil.copytree(DIST, PREV)
    # "index.html" é nome reservado no artefato: a página inicial vira home.html
    (PREV / "index.html").rename(PREV / "home.html")
    n = 0
    for p in PREV.glob("*.html"):
        s = p.read_text(encoding="utf-8")
        s = MAPA_RE.sub(MAPA_IMG, s).replace('href="index.html"', 'href="home.html"').replace("</head>", INTERCEPT + "</head>", 1)
        p.write_text(s, encoding="utf-8")
        n += 1
    (PREV / "_shell.html").write_text(SHELL, encoding="utf-8")
    arquivos = sorted(str(f.relative_to(PREV)) for f in PREV.rglob("*") if f.is_file() and f.name != "_shell.html")
    (PREV / "_files.txt").write_text("\n".join(arquivos))
    print(f"preview: {n} páginas com interceptador; {len(arquivos)} arquivos para publicar")


if __name__ == "__main__":
    main()
