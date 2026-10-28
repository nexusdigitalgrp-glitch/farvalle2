/* Farvalle 2 — comportamento do site (sem dependências além do Leaflet no contato) */
(function () {
  /* Sombra do cabeçalho ao rolar */
  var topo = document.getElementById("topo");
  function sombra() { if (topo) topo.classList.toggle("rolou", window.scrollY > 8); }
  window.addEventListener("scroll", sombra, { passive: true }); sombra();

  /* Submenus do desktop: abrem no clique/teclado (hover é por CSS) */
  document.querySelectorAll(".nav .tem-sub").forEach(function (box) {
    var btn = box.querySelector(".sub-btn");
    if (!btn) return;
    function abrir(v) { box.classList.toggle("aberto", v); btn.setAttribute("aria-expanded", String(v)); }
    btn.addEventListener("click", function () { abrir(!box.classList.contains("aberto")); });
    document.addEventListener("click", function (e) { if (!box.contains(e.target)) abrir(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") abrir(false); });
  });

  /* Menu do celular */
  var hamb = document.querySelector(".hamb");
  var painel = document.getElementById("menu-mobile");
  if (hamb && painel) {
    function fechar() { painel.classList.remove("aberto"); hamb.setAttribute("aria-expanded", "false"); hamb.setAttribute("aria-label", "Abrir menu"); document.body.style.overflow = ""; }
    hamb.addEventListener("click", function () {
      var abrir = !painel.classList.contains("aberto");
      painel.classList.toggle("aberto", abrir);
      hamb.setAttribute("aria-expanded", String(abrir));
      hamb.setAttribute("aria-label", abrir ? "Fechar menu" : "Abrir menu");
      document.body.style.overflow = abrir ? "hidden" : "";
    });
    painel.addEventListener("click", function (e) { if (e.target.closest("a")) fechar(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") fechar(); });
    window.addEventListener("resize", function () { if (window.innerWidth > 1040) fechar(); });
  }

  /* Hero: destaques rotativos com setas e pontos */
  document.querySelectorAll("[data-hero]").forEach(function (h) {
    var slides = h.querySelectorAll(".hero-slide"), pontos = h.querySelectorAll(".hero-pontos button");
    var atual = 0, timer, pausado = false;
    function ir(i) {
      atual = (i + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle("ativo", k === atual); });
      pontos.forEach(function (p, k) { if (k === atual) p.setAttribute("aria-current", "true"); else p.removeAttribute("aria-current"); });
    }
    function agendar() { clearInterval(timer); timer = setInterval(function () { if (!pausado && !document.hidden) ir(atual + 1); }, 6500); }
    h.querySelector("[data-hero-ant]").addEventListener("click", function () { ir(atual - 1); agendar(); });
    h.querySelector("[data-hero-prox]").addEventListener("click", function () { ir(atual + 1); agendar(); });
    pontos.forEach(function (p, k) { p.addEventListener("click", function () { ir(k); agendar(); }); });
    h.addEventListener("mouseenter", function () { pausado = true; });
    h.addEventListener("mouseleave", function () { pausado = false; });
    var x0 = null;
    h.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    h.addEventListener("touchend", function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 50) { ir(atual + (dx < 0 ? 1 : -1)); agendar(); } x0 = null; }, { passive: true });
    agendar();
  });

  /* Fileiras que rolam lateralmente: setas, barra de progresso, teclado e arrasto com o mouse */
  document.querySelectorAll("[data-trilho]").forEach(function (t) {
    var nav = t.nextElementSibling;
    if (!nav || !nav.classList.contains("trilho-nav")) return;
    var barra = nav.querySelector(".trilho-barra i"), ant = nav.querySelector("[data-ant]"), prox = nav.querySelector("[data-prox]");
    function passo() { var f = t.firstElementChild; return f ? f.getBoundingClientRect().width + 20 : t.clientWidth; }
    function atualizar() {
      var max = t.scrollWidth - t.clientWidth;
      if (max <= 2) { nav.style.display = "none"; return; }
      nav.style.display = "";
      barra.style.width = Math.max(8, t.clientWidth / t.scrollWidth * 100) + "%";
      barra.style.transform = "translateX(" + (t.scrollLeft / t.clientWidth * 100) + "%)";
      ant.disabled = t.scrollLeft < 2;
      prox.disabled = t.scrollLeft >= max - 2;
    }
    ant.addEventListener("click", function () { t.scrollBy({ left: -passo(), behavior: "smooth" }); });
    prox.addEventListener("click", function () { t.scrollBy({ left: passo(), behavior: "smooth" }); });
    t.addEventListener("scroll", atualizar, { passive: true });
    window.addEventListener("resize", atualizar);
    /* arrastar com o mouse no desktop */
    var arrastando = false, sx = 0, sl = 0;
    t.addEventListener("mousedown", function (e) { arrastando = true; sx = e.pageX; sl = t.scrollLeft; t.style.scrollSnapType = "none"; });
    window.addEventListener("mouseup", function () { if (arrastando) { arrastando = false; t.style.scrollSnapType = ""; } });
    t.addEventListener("mousemove", function (e) { if (!arrastando) return; e.preventDefault(); t.scrollLeft = sl - (e.pageX - sx); });
    t.addEventListener("click", function (e) { if (Math.abs(t.scrollLeft - sl) > 6 && arrastando === false && e.target.closest("a")) { /* clique após arrasto: deixa passar */ } }, true);
    atualizar();
    setTimeout(atualizar, 300);
  });

  /* Celular/tablet: o botão "ver todos" do cabeçalho da seção vai para depois da fileira */
  document.querySelectorAll(".sec-cab-linha .sec-cab-btn").forEach(function (b) {
    var sec = b.closest(".wrap"); if (!sec) return;
    var nav = sec.querySelector(".trilho-nav"); if (!nav) return;
    var ver = document.createElement("div"); ver.className = "ver-todos"; var c = b.cloneNode(true); c.classList.remove("sec-cab-btn"); ver.appendChild(c);
    nav.insertAdjacentElement("afterend", ver);
    function ajustar() { ver.style.display = window.innerWidth <= 960 ? "" : "none"; }
    window.addEventListener("resize", ajustar); ajustar();
  });

  /* Mapa interativo (Leaflet com tiles locais do OpenStreetMap) */
  var mapaEl = document.getElementById("mapa-interativo");
  if (mapaEl && window.L) {
    var lat = parseFloat(mapaEl.dataset.lat), lon = parseFloat(mapaEl.dataset.lon);
    var css = document.querySelector('link[rel="stylesheet"][href*="site.css"]');
    var base = css ? css.getAttribute("href").replace(/assets\/css\/site\.css.*$/, "") : "";
    var mapa = L.map(mapaEl, { center: [lat, lon], zoom: 17, minZoom: 16, maxZoom: 18, scrollWheelZoom: false, zoomControl: true, attributionControl: true });
    mapa.attributionControl.setPrefix(false);
    L.tileLayer(base + "assets/mapa/{z}/{x}/{y}.png", { minZoom: 16, maxZoom: 18, attribution: "&copy; OpenStreetMap contributors", errorTileUrl: "" }).addTo(mapa);
    mapa.setMaxBounds(L.latLngBounds([lat - 0.012, lon - 0.016], [lat + 0.012, lon + 0.016]));
    var pino = L.divIcon({ className: "mapa-pino", html: '<span class="mapa-pino-onda"></span><span class="mapa-pino-ponto"></span>', iconSize: [44, 44], iconAnchor: [22, 22], popupAnchor: [0, -22] });
    L.marker([lat, lon], { icon: pino, title: mapaEl.dataset.nome }).addTo(mapa)
      .bindPopup("<b>" + mapaEl.dataset.nome + "</b><br>" + mapaEl.dataset.end).openPopup();
    mapaEl.addEventListener("click", function () { mapa.scrollWheelZoom.enable(); }, { once: true });
  }

  /* Formulário de inscrição */
  var form = document.getElementById("form-inscricao");
  if (form) {
    var ingresso = document.getElementById("ingresso"), bloco = document.getElementById("bloco-redacao"), texto = document.getElementById("texto-redacao"), contador = document.getElementById("contador");
    var erro = document.getElementById("form-erro"), ok = document.getElementById("form-ok"), curso = document.getElementById("course");
    /* pré-seleção vinda da URL (?curso=enfermagem&ingresso=Nota%20do%20ENEM) */
    try {
      var q = new URLSearchParams(location.search);
      if (q.get("curso") && curso) { Array.prototype.forEach.call(curso.options, function (o) { if (o.dataset.slug === q.get("curso")) curso.value = o.value; }); }
      if (q.get("ingresso") && ingresso) ingresso.value = q.get("ingresso");
    } catch (e) {}
    function redacao() { var v = ingresso.value === "Vestibular Online"; bloco.hidden = !v; if (texto) texto.required = v; }
    ingresso.addEventListener("change", redacao); redacao();
    if (texto && contador) {
      texto.addEventListener("input", function () { var n = texto.value.trim() ? texto.value.trim().split(/\s+/).length : 0; contador.textContent = n + (n === 1 ? " palavra" : " palavras"); });
    }
    /* máscara simples do celular */
    var tel = form.querySelector('[name="tel"]');
    if (tel) tel.addEventListener("input", function () {
      var d = tel.value.replace(/\D/g, "").slice(0, 11), s = d;
      if (d.length > 2) s = "(" + d.slice(0, 2) + ") " + d.slice(2);
      if (d.length > 7) s = "(" + d.slice(0, 2) + ") " + d.slice(2, 7) + "-" + d.slice(7);
      tel.value = s;
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      erro.hidden = true;
      var faltas = [];
      form.querySelectorAll("[required]").forEach(function (c) {
        var campo = c.closest(".campo") || c.closest(".campo-check");
        var vazio = c.type === "checkbox" ? !c.checked : !c.value.trim();
        var invalido = vazio || (c.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(c.value)) || (c.name === "tel" && c.value.replace(/\D/g, "").length < 10) || (c.name === "text" && c.value.trim().split(/\s+/).length < 20);
        if (campo) campo.classList.toggle("invalido", invalido);
        if (invalido) faltas.push(c);
      });
      if (faltas.length) {
        erro.textContent = faltas.length === 1 && faltas[0].name === "text" ? "A redação precisa ter pelo menos 20 palavras." : "Preencha corretamente todos os campos destacados para enviar a inscrição.";
        erro.hidden = false; faltas[0].focus(); return;
      }
      var dados = {};
      new FormData(form).forEach(function (v, k) { dados[k] = v; });
      var btn = form.querySelector('button[type="submit"]'); btn.disabled = true; btn.querySelector("span").textContent = "Enviando…";
      /* Envio: a API real (Resend → secretaria) é ligada na publicação; na prévia o envio é simulado. */
      var api = form.dataset.api;
      var p = api ? fetch(api, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(dados) }).then(function (r) { if (!r.ok) throw new Error("http " + r.status); }) : new Promise(function (res) { setTimeout(res, 900); });
      p.then(function () { form.classList.add("enviado"); ok.hidden = false; ok.focus(); window.scrollTo({ top: form.getBoundingClientRect().top + window.scrollY - 120, behavior: "smooth" }); })
       .catch(function () { erro.textContent = "Não foi possível enviar agora. Tente novamente em instantes ou fale com a secretaria pelo WhatsApp."; erro.hidden = false; btn.disabled = false; btn.querySelector("span").textContent = "Enviar inscrição"; });
    });
  }

  /* Números: contagem animada ao aparecer */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, txt = el.textContent.trim(), m = txt.match(/^(\d+)(%?)$/);
        io.unobserve(el);
        if (!m) return;
        var alvo = parseInt(m[1], 10), suf = m[2], t0 = performance.now();
        (function anima(t) { var k = Math.min(1, (t - t0) / 900); el.textContent = Math.round(alvo * (1 - Math.pow(1 - k, 3))) + suf; if (k < 1) requestAnimationFrame(anima); })(t0);
      });
    }, { threshold: .4 });
    document.querySelectorAll(".numero strong").forEach(function (el) { io.observe(el); });
  }
})();
