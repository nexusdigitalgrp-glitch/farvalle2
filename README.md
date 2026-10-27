# Farvalle 2 — novo site da Faculdade Regional do Valle

Site estático independente do site atual (farvalle.edu.br, Next.js/Vercel) — não altera nada no projeto existente.
Inspirado na estrutura de portais universitários (mackenzie.br/universidade): barra de acesso rápido, menu com submenus,
destaques rotativos, cartões de entrada, cursos, formas de ingresso, notícias, serviços, campus com mapa e rodapé institucional.
Identidade: verde institucional (#17382a) sobre fundos brancos; laranja da marca só em acentos/CTA; Montserrat + Caveat (locais).

## Páginas (16)
Início · A Farvalle · Cursos · Enfermagem · Fisioterapia · Pedagogia · Processo Seletivo · Inscreva-se ·
Vida Acadêmica (publicações institucionais) · Notícias (+3 matérias reais do site atual) · Contato (mapa interativo) · Privacidade · 404.

## Build
```
python3 build.py            # dist/ com links .html (prévia local)
python3 build.py --limpo    # dist/ com URLs limpas (/cursos/enfermagem/) para publicar
python3 build.py --limpo --site=https://farvalle.edu.br --base=/subpasta   # opcional
python3 -m http.server 3700 --directory dist
```
Checagens (Playwright): `scripts/check-links.mjs`, `check-nav.mjs`, `check-titulos.mjs`, `check-responsive.mjs` (320–5120 px).
Prévia para artefato: `python3 scripts/preview.py` → `preview/`.

## Formulário de inscrição
Mesmos campos do site atual (nome, celular, e-mail, cidade, como conheceu, forma de ingresso, curso, redação quando Vestibular Online).
Na prévia o envio é simulado. Para ligar o envio real, coloque no `<form>` o atributo `data-api` com a URL da rota que envia
pelo Resend para secad@farvalle.edu.br (ex.: a rota `/api/inscricao/email` do projeto atual, com CORS liberado para o domínio novo),
ou hospede este site no mesmo domínio da API.

## Dados a confirmar com a faculdade
Horário de atendimento da secretaria; turno/coordenação dos cursos; documentos de calendário e regulamentos (hoje apontam para o
portal/secretaria); fotos definitivas (as atuais são as artes do layout aprovado em 2026, recortadas).

## Mapa
Leaflet 1.9.4 local + tiles do OpenStreetMap (zoom 16–18) em `src/assets/mapa/` — funciona na prévia e no site publicado, sem serviços externos.
