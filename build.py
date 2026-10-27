#!/usr/bin/env python3
"""Gera o site estático "Farvalle 2" (Faculdade Regional do Valle) em dist/.
Uso: python3 build.py [--limpo] [--base=/subpasta] [--site=https://dominio]
"""
import datetime, hashlib, html, json, pathlib, re, shutil, sys
from urllib.parse import quote

RAIZ = pathlib.Path(__file__).parent
SRC = RAIZ / "src"
DIST = RAIZ / "dist"
LIMPO = "--limpo" in sys.argv
BASE = next((a.split("=", 1)[1].rstrip("/") for a in sys.argv if a.startswith("--base=")), "")
SITE = next((a.split("=", 1)[1].rstrip("/") for a in sys.argv if a.startswith("--site=")), "https://farvalle.edu.br")

# ───────────── Dados institucionais (fontes: site atual farvalle.edu.br, layout aprovado 2026, e-MEC) ─────────────
NOME = "Faculdade Farvalle"
NOME_LONGO = "Farvalle — Faculdade Regional do Valle"
SIGLA = "FARVALLE"
EDICAO = "Vestibular 2026.2"
ENDERECO = "Avenida Dr. Luís Sande, 147 — Santa Rita, Valle Shopping"
CIDADE = "Amargosa/BA · CEP 45300-000"
EMAIL = "faculdade.farvalle@gmail.com"
EMAIL_SECRETARIA = "secad@farvalle.edu.br"
TELEFONE = "(75) 98870-8022"
WHATS = "5575988708022"
WHATSAPP_TEXTO = "Olá! Quero mais informações sobre os cursos da Farvalle."
INSTAGRAM = "https://www.instagram.com/farvalle/"
INSTA_USER = "@farvalle"
PORTAL = "https://educacional.usecerbrum.net/inicio.aspx"
JASMIN = "https://jasmin.farvalle.edu.br/"
EMEC = "https://emec.mec.gov.br/emec/consulta-cadastro/detalhes-ies/d96957f455f6405d14c6542552b0f6eb/MjU0Mzk="
LAT, LON = -13.0238873, -39.6063704  # Valle Shopping (OpenStreetMap)
MAPS = "https://www.google.com/maps/search/?api=1&query=" + quote("Faculdade Farvalle, Valle Shopping, Av. Dr. Luís Sande, 147, Amargosa - BA")
MAPS_ROTA = f"https://www.google.com/maps/dir/?api=1&destination={LAT},{LON}"
WAZE = f"https://waze.com/ul?ll={LAT},{LON}&navigate=yes"
HORARIO = "Segunda a sexta, das 8h às 21h · Sábado, das 8h às 12h"  # atendimento da secretaria (a confirmar)

CURSOS = [
    # slug, nome, grau, duração, turno, modalidade, tagline, resumo, sobre (2 parágrafos), para quem (4), áreas (4), cor
    dict(slug="enfermagem", nome="Enfermagem", grau="Bacharelado", duracao="10 semestres", turno="Noturno", modalidade="Presencial",
         tagline="Cuidado de pessoas para um futuro mais humano.",
         resumo="Forme-se para atuar na promoção, prevenção e recuperação da saúde, com uma formação completa e alinhada às necessidades reais da sociedade.",
         sobre=["O curso de Enfermagem da Farvalle forma profissionais capacitados para atuar em diferentes níveis de atenção à saúde, com base em conhecimento científico, prática qualificada e compromisso com o cuidado integral das pessoas.",
                "Aqui, você desenvolve competências técnicas, humanas e éticas para fazer a diferença na vida das pessoas e na sua comunidade."],
         para_quem=["Pessoas que se identificam com o cuidado e o trabalho com pessoas", "Quem busca uma profissão com grande impacto social",
                    "Interessados em atuar em hospitais, clínicas, atenção básica e saúde pública", "Quem quer construir uma carreira sólida e cheia de possibilidades"],
         areas=["Hospitais e clínicas", "Atenção básica", "Saúde pública", "Gestão em saúde"], icone="coracao"),
    dict(slug="fisioterapia", nome="Fisioterapia", grau="Bacharelado", duracao="10 semestres", turno="Noturno", modalidade="Presencial",
         tagline="Movimento, saúde e mais qualidade de vida.",
         resumo="Forme-se para promover reabilitação, prevenção e bem-estar, atuando com pessoas em todas as fases da vida.",
         sobre=["O curso de Fisioterapia da Farvalle prepara profissionais capazes de promover, manter e recuperar a funcionalidade e a qualidade de vida das pessoas, atuando em diferentes contextos da saúde e no movimento humano.",
                "Aqui, você aprende na prática, com uma visão ampla e atualizada da profissão, unindo ciência, cuidado e propósito."],
         para_quem=["Pessoas que se interessam pelo corpo humano e pelo movimento", "Quem gosta de ajudar pessoas a recuperarem sua autonomia",
                    "Interessados em atuar em clínicas, hospitais, esportes, empresas e saúde pública", "Quem busca uma carreira dinâmica e com muitas áreas de atuação"],
         areas=["Clínicas e hospitais", "Esporte e academias", "Saúde do trabalhador", "Reabilitação"], icone="movimento"),
    dict(slug="pedagogia", nome="Pedagogia", grau="Licenciatura", duracao="8 semestres", turno="Noturno", modalidade="Presencial",
         tagline="Educar e abrir caminhos para um futuro com mais oportunidades.",
         resumo="Forme-se para atuar na educação, contribuindo para o desenvolvimento de pessoas, comunidades e da sociedade.",
         sobre=["O curso de Pedagogia da Farvalle prepara educadores para atuar em diferentes espaços, contribuindo para a formação de sujeitos críticos, criativos e comprometidos com uma sociedade mais justa e inclusiva.",
                "Aqui, você desenvolve uma visão humana e transformadora da educação, com base em teoria, prática e realidade local."],
         para_quem=["Pessoas que acreditam no poder da educação", "Quem se identifica com o trabalho com crianças, jovens e comunidades",
                    "Interessados em atuar em escolas, projetos sociais, gestão educacional e muito mais", "Quem quer fazer parte da construção de um futuro com mais oportunidades"],
         areas=["Docência", "Gestão educacional", "Projetos sociais", "Concursos públicos"], icone="livro"),
]
CURSO = {c["slug"]: c for c in CURSOS}

INGRESSO = [  # formas de ingresso (as mesmas do formulário atual)
    dict(slug="vestibular-online", nome="Vestibular Online", icone="laptop", curto="Redação online",
         texto="Inscreva-se pelo site e escreva a sua redação dissertativo-argumentativa sobre o tema proposto, no próprio formulário, de onde estiver.",
         passos=["Preencha o formulário de inscrição", "Escreva a redação sobre o tema proposto", "Aguarde o contato da secretaria com o resultado"]),
    dict(slug="nota-do-enem", nome="Nota do ENEM", icone="medalha", curto="Sem prova",
         texto="Use a nota de uma edição anterior do ENEM para ingressar sem fazer a redação do vestibular.",
         passos=["Preencha o formulário escolhendo “Nota do ENEM”", "Apresente o boletim do ENEM à secretaria", "Receba a confirmação e faça a matrícula"]),
    dict(slug="transferencia-externa", nome="Transferência Externa", icone="troca", curto="Vindo de outra IES",
         texto="Já cursa Enfermagem, Fisioterapia ou Pedagogia em outra instituição? Transfira seus estudos e continue a graduação na Farvalle.",
         passos=["Preencha o formulário escolhendo “Transferência Externa”", "Envie histórico e ementas para análise de aproveitamento", "Receba o parecer e faça a matrícula"]),
    dict(slug="segunda-graduacao", nome="Segunda Graduação", icone="diploma", curto="Já é formado",
         texto="Quem já concluiu um curso superior pode ingressar como portador de diploma, com possibilidade de aproveitamento de disciplinas.",
         passos=["Preencha o formulário escolhendo “Segunda Graduação”", "Apresente diploma e histórico da primeira graduação", "Receba o parecer e faça a matrícula"]),
]

NOTICIAS = [  # conteúdo real do site atual (farvalle.edu.br/posts) — resumido
    dict(slug="vale-a-pena-comecar-em-2026-2", data="2026-07-15", data_txt="15 de julho de 2026", foto="news-1", categoria="Vestibular",
         titulo="Ainda dá tempo de começar em 2026.2",
         resumo="O ano já está avançando, mas isso não significa que você precisa deixar o sonho da faculdade para depois. Ainda dá tempo de começar em 2026.2.",
         corpo=[
             ("p", "O ano já está avançando, mas isso não significa que você precisa deixar o sonho da faculdade para depois. Se você quer construir uma nova trajetória profissional, ainda dá tempo de começar em 2026.2 na Farvalle, com oportunidades nos cursos de Enfermagem, Fisioterapia e Pedagogia."),
             ("h2", "Não espere o próximo ano para começar"),
             ("p", "É comum pensar: “Já estamos no segundo semestre, será que não é melhor esperar o próximo ano?”. Mas adiar também significa esperar mais tempo para concluir a graduação e começar uma nova etapa profissional. Ao ingressar em 2026.2, você já começa agora a construir conhecimentos, conhecer pessoas, vivenciar o ambiente acadêmico e se aproximar da profissão que escolheu."),
             ("h2", "Enfermagem: a diferença pelo cuidado"),
             ("p", "A Enfermagem é uma profissão essencial para a sociedade e está presente em diferentes momentos da vida das pessoas. Durante a graduação, o estudante desenvolve conhecimentos e competências para atuar na promoção da saúde, prevenção de doenças e assistência aos pacientes em diferentes contextos."),
             ("h2", "Fisioterapia: movimento e saúde"),
             ("p", "A Fisioterapia reúne conhecimento, cuidado e movimento com um objetivo muito importante: contribuir para a saúde, a funcionalidade e a qualidade de vida das pessoas. É uma formação para quem se interessa pelo corpo humano e deseja trabalhar com prevenção, avaliação, tratamento e reabilitação."),
             ("h2", "Pedagogia: transformar pela educação"),
             ("p", "Todo grande profissional teve professores que fizeram parte da sua trajetória. A Pedagogia prepara profissionais para atuar na educação e participar diretamente da formação e do desenvolvimento de novas gerações. Se você acredita que ensinar também é uma forma de transformar vidas, Pedagogia pode ser o seu lugar."),
             ("h2", "Vestibular 2026.2: ainda dá tempo!"),
             ("p", "O Vestibular Farvalle 2026.2 está aberto para Enfermagem, Fisioterapia e Pedagogia. Escolha o curso que combina com você, faça sua inscrição e dê o primeiro passo para uma nova história. Seu futuro não precisa esperar. Vem pra Farvalle!"),
         ]),
    dict(slug="inicio-das-atividades-2024-2", data="2024-08-07", data_txt="7 de agosto de 2024", foto="news-2", categoria="Vida acadêmica",
         titulo="2024.2: início das atividades",
         resumo="“O melhor lugar do mundo é aqui e agora.” A frase de Gilberto Gil ilustrou o começo do semestre 2024.2, com música ao vivo e palestra do Prof. Dr. Makson Reis.",
         corpo=[
             ("p", "No dia 7 de agosto de 2024 tivemos a nossa Semana de Acolhimento Pedagógico Discente, marcando também o primeiro dia letivo da Farvalle. A noite começou com música ao vivo da querida Cris Coutinho, uma artista excepcional que já é da casa."),
             ("p", "Em seguida, os alunos foram recebidos para a apresentação da equipe de trabalho. Após uma breve apresentação em que todos tiveram a palavra, iniciou-se a palestra do Professor e Dr. Makson Reis, com a temática “Novos desafios para uma educação superior de qualidade: engajamento, extensão, promoção e divulgação científica”."),
             ("p", "Foi uma palestra de muito engajamento, com informações agregadoras que enriqueceram alunos, colaboradores e convidados. Ao final da primeira noite, foi dado o início ao semestre 2024.2 com uma proposta inovadora, cheia de foco, propósito e um olhar para resultados."),
             ("p", "E citando novamente nosso querido Gilberto Gil: “O melhor lugar do mundo é aqui e agora!”"),
         ]),
    dict(slug="diversidade-e-inclusao-saude-mental", data="2024-05-21", data_txt="21 de maio de 2024", foto="news-3", categoria="Eventos",
         titulo="Diversidade e inclusão na saúde",
         resumo="Palestra com George Mariane na Câmara dos Vereadores de Amargosa reuniu alunos, docentes e convidados em torno da inclusão e do cuidado com quem cuida.",
         corpo=[
             ("p", "No dia 21 de maio de 2024 ocorreu a palestra “Diversidade e Inclusão: um olhar sobre a saúde mental dos profissionais de saúde”, com o convidado George Mariane. O evento aconteceu na Câmara dos Vereadores de Amargosa e contou com ilustres presenças e, claro, com os nossos queridos alunos."),
             ("p", "A noite foi aberta pela oradora Julia Santos, estudante de psicologia, que guiou o caminho para a bancada composta por Juvenal Fernandes dos Santos Filho (representante dos técnicos de enfermagem), Vera Suzart (mantenedora), Joseval Borges (diretor geral), João Nilton (coordenador do curso de Enfermagem) e Aiandra Bruno (professora e diretora convidada)."),
             ("p", "Entre os temas em destaque estiveram a inclusão, a gnosia e a “Modernidade Líquida”, de Zygmunt Bauman — contribuições importantes para entender a atualidade e lidar com as principais aflições que atingem os profissionais, de saúde e de todos os campos. A palestra contou com o intérprete de Libras Marcelo Maia, para levar a mensagem ao maior número de pessoas possível."),
             ("p", "Um evento maravilhoso proporcionado pela Farvalle. Não perca os próximos!"),
         ]),
]
NOTICIA = {n["slug"]: n for n in NOTICIAS}

MENU = [  # (rótulo, slug/href, submenu)
    ("Início", "index", None),
    ("A Farvalle", "a-farvalle", [("Quem somos", "a-farvalle"), ("Campus Valle Shopping", "a-farvalle#campus"), ("Valores", "a-farvalle#valores"), ("Cadastro e-MEC", EMEC)]),
    ("Cursos", "cursos", [(c["nome"], "cursos/" + c["slug"]) for c in CURSOS] + [("Todos os Cursos", "cursos")]),
    ("Processo Seletivo", "processo-seletivo", [(i["nome"], "processo-seletivo#" + i["slug"]) for i in INGRESSO] + [("Inscreva-se", "inscreva-se")]),
    ("Vida Acadêmica", "publicacoes-institucionais", [("Calendário Acadêmico", "publicacoes-institucionais#calendario"), ("Regulamentos Institucionais", "publicacoes-institucionais#regulamentos"), ("Portal do Aluno", PORTAL), ("Notícias", "noticias")]),
    ("Notícias", "noticias", None),
    ("Contato", "contato", None),
]


# ───────────── Helpers ─────────────
def url(slug):
    if slug.startswith("http") or slug.startswith("mailto") or slug.startswith("tel"):
        return slug
    frag = ""
    if "#" in slug:
        slug, frag = slug.split("#", 1)
        frag = "#" + frag
    if slug == "index":
        return ((BASE + "/") if LIMPO else "index.html") + frag
    return (f"{BASE}/{slug}/" if LIMPO else f"{slug.replace('/', '-')}.html") + frag


def wa(texto=None):
    return f"https://wa.me/{WHATS}?text={quote(texto or WHATSAPP_TEXTO)}"


def tel(numero):
    return "tel:+55" + "".join(c for c in numero if c.isdigit())


def canonica(slug):
    return SITE + ("/" if slug == "index" else "/" + slug + "/")


def versao_asset(rel):
    return hashlib.md5((SRC / rel).read_bytes()).hexdigest()[:8]


def e(s):
    return html.escape(s, quote=True)


S = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
I = {
    "arrow": f'<svg {S}><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "chev": f'<svg {S}><path d="M6 9l6 6 6-6"/></svg>',
    "chev-r": f'<svg {S}><path d="M9 6l6 6-6 6"/></svg>',
    "check": f'<svg {S}><path d="M5 12.5l4.5 4.5L19 7"/></svg>',
    "whats": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91S17.5 2 12.04 2m0 1.67c4.54 0 8.24 3.7 8.24 8.24s-3.7 8.24-8.24 8.24c-1.5 0-2.97-.41-4.24-1.18l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 0 1-1.26-4.35c0-4.54 3.7-8.24 8.24-8.24M8.53 7.33c-.16 0-.43.06-.66.31-.22.25-.87.86-.87 2.07 0 1.22.89 2.39 1 2.56.14.17 1.76 2.67 4.25 3.73.59.27 1.05.42 1.41.53.59.19 1.13.16 1.56.1.48-.07 1.46-.6 1.67-1.18.21-.58.21-1.07.15-1.18-.07-.1-.23-.16-.48-.27-.25-.14-1.47-.74-1.69-.82-.23-.08-.37-.12-.56.12-.16.25-.64.81-.78.97-.15.17-.29.19-.53.07-.26-.13-1.06-.39-2-1.23-.74-.66-1.23-1.47-1.38-1.72-.12-.24-.01-.39.11-.5.11-.11.27-.29.37-.44.13-.14.17-.25.25-.41.08-.17.04-.31-.02-.43-.06-.11-.56-1.35-.77-1.84-.2-.48-.4-.42-.56-.43-.14 0-.3-.01-.47-.01"/></svg>',
    "insta": f'<svg {S}><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".9" fill="currentColor"/></svg>',
    "map": f'<svg {S}><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "phone": f'<svg {S}><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>',
    "mail": f'<svg {S}><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    "clock": f'<svg {S}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "user": f'<svg {S}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
    "grad": f'<svg {S}><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5"/><path d="M22 9v6"/></svg>',
    "building": f'<svg {S}><rect x="4" y="3" width="16" height="18" rx="1"/><path d="M8 7h2M14 7h2M8 11h2M14 11h2M8 15h2M14 15h2M10 21v-3h4v3"/></svg>',
    "handshake": f'<svg {S}><path d="M3 11l3-4h5l2 2 3-3h5l-2 5-4 5-3 3-4-4"/><path d="M8 12l3 3M11 10l3 3"/></svg>',
    "care": f'<svg {S}><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>',
    "coracao": f'<svg {S}><path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z"/><path d="M8 11h2l1.5-3 2 6 1.5-3h1"/></svg>',
    "movimento": f'<svg {S}><circle cx="15" cy="4.5" r="1.8"/><path d="M8 21l3-7 3 2 2 5M11 14l-3-3 5-4 3 3 3-1"/></svg>',
    "livro": f'<svg {S}><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19a2 2 0 0 1 2-2h13"/><path d="M9 7h6"/></svg>',
    "laptop": f'<svg {S}><rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19h20"/></svg>',
    "medalha": f'<svg {S}><circle cx="12" cy="14" r="5"/><path d="M8.5 10L6 3h12l-2.5 7"/></svg>',
    "troca": f'<svg {S}><path d="M4 8h13l-3-3M20 16H7l3 3"/></svg>',
    "diploma": f'<svg {S}><rect x="3" y="5" width="18" height="12" rx="2"/><path d="M7 9h10M7 13h6M14 17l1 4 2-1.5L19 21l-1-4"/></svg>',
    "calendar": f'<svg {S}><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
    "file": f'<svg {S}><path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>',
    "book": f'<svg {S}><path d="M3 5h7a2 2 0 0 1 2 2v13a2 2 0 0 0-2-2H3zM21 5h-7a2 2 0 0 0-2 2v13a2 2 0 0 1 2-2h7z"/></svg>',
    "portal": f'<svg {S}><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 21h8M12 18v3M7 9h4M7 13h10"/></svg>',
    "lib": f'<svg {S}><path d="M4 20V5a1 1 0 0 1 1-1h3v16M9 20V8h3v12M13 20l2-12 3 .6-2 11.4"/></svg>',
    "chat": f'<svg {S}><path d="M4 5h16v11H9l-5 4z"/></svg>',
    "idea": f'<svg {S}><path d="M9 18h6M10 21h4M8 13a5 5 0 1 1 8 0c-.7.8-1 1.5-1 2.5H9c0-1-.3-1.7-1-2.5z"/></svg>',
    "growth": f'<svg {S}><path d="M4 19l5-6 4 3 7-9"/><path d="M15 7h5v5"/></svg>',
    "community": f'<svg {S}><circle cx="8" cy="9" r="3"/><circle cx="16" cy="9" r="3"/><path d="M2 20a6 6 0 0 1 12 0M10 20a6 6 0 0 1 12 0"/></svg>',
    "pin": f'<svg {S}><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "region": f'<svg {S}><path d="M3 7l6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 5v14M15 7v14"/></svg>',
    "shield": f'<svg {S}><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
    "star": f'<svg {S}><path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"/></svg>',
    "search": f'<svg {S}><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>',
    "x": f'<svg {S}><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "hamb": f'<svg {S}><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "waze": f'<svg {S}><path d="M4 11a8 8 0 1 1 5 7.4L5 20l1.2-3.5A8 8 0 0 1 4 11z"/><circle cx="9.5" cy="10" r=".9" fill="currentColor"/><circle cx="14.5" cy="10" r=".9" fill="currentColor"/><path d="M9 13.5c1.5 1.5 4.5 1.5 6 0"/></svg>',
    "people": f'<svg {S}><circle cx="9" cy="8" r="3.5"/><path d="M2 20a7 7 0 0 1 14 0"/><path d="M16 4a3.5 3.5 0 0 1 0 7M18 13a6 6 0 0 1 4 6"/></svg>',
    "chart": f'<svg {S}><path d="M4 20h16M7 16v-5M12 16V7M17 16v-8"/></svg>',
}


def ic(nome, classe="ic"):
    return f'<span class="{classe}" aria-hidden="true">{I[nome]}</span>'


def btn(texto, href, classe="btn btn-verde", icone="arrow", externo=False, grande=False):
    ext = ' target="_blank" rel="noopener"' if externo else ""
    g = " btn-g" if grande else ""
    return f'<a class="{classe}{g}" href="{href}"{ext}><span>{e(texto)}</span>{ic(icone, "btn-ic") if icone else ""}</a>'


def btn_whats(texto="Falar no WhatsApp", classe="btn btn-contorno", msg=None, grande=False):
    return btn(texto, wa(msg), classe, "whats", externo=True, grande=grande)


def foto(nome, alt, classe="", prioridade=False, pos=None, sizes=None, ext="jpg", w=None, h=None):
    estilo = f' style="object-position:{pos}"' if pos else ""
    dims = f' width="{w}" height="{h}"' if w and h else ""
    carga = 'fetchpriority="high" decoding="async"' if prioridade else 'loading="lazy" decoding="async"'
    return f'<img class="{classe}" src="assets/img/{nome}.{ext}" alt="{e(alt)}" {carga}{estilo}{dims}>'


def logo_img(clara=False, classe="logo-img"):
    base = "farvalle-logo-white" if clara else "farvalle-logo"
    return f'<img class="{classe}" src="assets/img/{base}.png" alt="{NOME_LONGO}" width="1601" height="252">'


# ───────────── Cabeçalho / rodapé ─────────────
def cabecalho(atual):
    itens = []
    topo_slugs = {m[1] for m in MENU}
    for rotulo, slug, sub in MENU:
        pai = bool(sub) and atual not in topo_slugs and any(atual == s[1].split("#")[0] for s in sub)
        ativo = ' aria-current="page"' if atual == slug or pai else ""
        if sub:
            lis = "".join(f'<li><a href="{url(s)}"{" target=\"_blank\" rel=\"noopener\"" if s.startswith("http") else ""}>{e(r)}</a></li>' for r, s in sub)
            itens.append(f'<li class="tem-sub"><a href="{url(slug)}"{ativo}>{e(rotulo)}</a><button class="sub-btn" type="button" aria-expanded="false" aria-label="Abrir submenu de {e(rotulo)}">{I["chev"]}</button><ul class="submenu">{lis}</ul></li>')
        else:
            itens.append(f'<li><a href="{url(slug)}"{ativo}>{e(rotulo)}</a></li>')
    # painel do celular
    mob = []
    for rotulo, slug, sub in MENU:
        if sub:
            lis = "".join(f'<li><a href="{url(s)}">{e(r)}</a></li>' for r, s in sub)
            mob.append(f'<li class="m-grupo"><details><summary><span>{e(rotulo)}</span>{I["chev"]}</summary><ul>{lis}</ul></details></li>')
        else:
            mob.append(f'<li><a href="{url(slug)}">{e(rotulo)}</a></li>')
    return f'''<a class="pular" href="#conteudo">Ir para o conteúdo</a>
<div class="barra-topo">
  <div class="wrap">
    <div class="barra-redes">
      <a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram da Farvalle">{I["insta"]}</a>
      <a href="{wa()}" target="_blank" rel="noopener" aria-label="WhatsApp da Farvalle">{I["whats"]}</a>
      <span class="barra-txt">{ic("pin","ic-s")} Amargosa, Bahia</span>
    </div>
    <nav class="barra-links" aria-label="Acesso rápido">
      <a href="{PORTAL}" target="_blank" rel="noopener">Portal do Aluno</a>
      <a href="{JASMIN}" target="_blank" rel="noopener">Acesse o Portal</a>
      <a href="{EMEC}" target="_blank" rel="noopener">e-MEC</a>
      <a href="{url('publicacoes-institucionais')}">Calendário</a>
      <a href="{url('contato')}">Contato</a>
    </nav>
  </div>
</div>
<header class="topo" id="topo">
  <div class="wrap topo-in">
    <a class="logo" href="{url('index')}" aria-label="{NOME_LONGO} — início">{logo_img()}</a>
    <nav class="nav" aria-label="Menu principal"><ul>{"".join(itens)}</ul></nav>
    <div class="topo-acoes">
      {btn("Inscreva-se", url("inscreva-se"), "btn btn-laranja btn-topo")}
      <button class="hamb" type="button" aria-expanded="false" aria-controls="menu-mobile" aria-label="Abrir menu">{I["hamb"]}{I["x"]}</button>
    </div>
  </div>
  <div class="menu-mobile" id="menu-mobile">
    <ul class="m-lista">{"".join(mob)}</ul>
    <div class="m-acoes">
      {btn("Inscreva-se", url("inscreva-se"), "btn btn-laranja")}
      {btn("Portal do Aluno", PORTAL, "btn btn-contorno", "portal", externo=True)}
      {btn_whats()}
    </div>
    <p class="m-rodape">{ic("pin","ic-s")} {e(ENDERECO)}<br>{e(CIDADE)}</p>
  </div>
</header>'''


def flutuante():
    return f'<a class="flutuante" href="{wa()}" target="_blank" rel="noopener" aria-label="Falar com a Farvalle no WhatsApp">{I["whats"]}<span>Fale com a gente</span></a>'


def rodape():
    cursos = "".join(f'<li><a href="{url("cursos/" + c["slug"])}">{e(c["nome"])}</a></li>' for c in CURSOS)
    inst = [("Início", "index"), ("A Farvalle", "a-farvalle"), ("Processo Seletivo", "processo-seletivo"), ("Inscreva-se", "inscreva-se"),
            ("Vida Acadêmica", "publicacoes-institucionais"), ("Notícias", "noticias"), ("Contato", "contato"), ("Política de Privacidade", "privacidade")]
    inst_li = "".join(f'<li><a href="{url(s)}">{e(r)}</a></li>' for r, s in inst)
    js_v = versao_asset("assets/js/site.js")
    return f'''<footer class="rodape">
  <div class="rodape-cta wrap">
    <div>
      <strong>Pronto para começar?</strong>
      <span>As inscrições do {EDICAO} estão abertas para Enfermagem, Fisioterapia e Pedagogia.</span>
    </div>
    <div class="rodape-cta-btns">{btn("Inscreva-se agora", url("inscreva-se"), "btn btn-laranja")}{btn_whats("Tirar dúvidas", "btn btn-claro")}</div>
  </div>
  <div class="wrap rodape-grade">
    <div class="rodape-marca">
      {logo_img(clara=True)}
      <p>Educação de hoje para um amanhã com mais oportunidades. Faculdade presencial no coração de Amargosa e do Recôncavo Baiano.</p>
      <div class="rodape-redes">
        <a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram">{I["insta"]}</a>
        <a href="{wa()}" target="_blank" rel="noopener" aria-label="WhatsApp">{I["whats"]}</a>
        <a href="mailto:{EMAIL}" aria-label="E-mail">{I["mail"]}</a>
      </div>
    </div>
    <nav class="rodape-col" aria-label="Institucional"><h3>Institucional</h3><ul>{inst_li}</ul></nav>
    <nav class="rodape-col" aria-label="Cursos"><h3>Cursos</h3><ul>{cursos}<li><a href="{url("cursos")}">Todos os Cursos</a></li></ul>
      <h3 class="rodape-h-2">Acesso</h3><ul><li><a href="{PORTAL}" target="_blank" rel="noopener">Portal do Aluno</a></li><li><a href="{JASMIN}" target="_blank" rel="noopener">Acesse o Portal</a></li></ul></nav>
    <div class="rodape-col rodape-contato"><h3>Contato</h3>
      <p>{ic("pin")}<span>{e(ENDERECO)}<br>{e(CIDADE)}</span></p>
      <p>{ic("phone")}<a href="{tel(TELEFONE)}">{TELEFONE}</a></p>
      <p>{ic("whats")}<a href="{wa()}" target="_blank" rel="noopener">WhatsApp {TELEFONE}</a></p>
      <p>{ic("mail")}<a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p>{ic("clock")}<span>{e(HORARIO)}</span></p>
    </div>
  </div>
  <div class="wrap rodape-base">
    <a class="rodape-emec" href="{EMEC}" target="_blank" rel="noopener"><img src="assets/img/e-mec.webp" alt="" width="1024" height="362" loading="lazy"><span>Consulte o cadastro da instituição no sistema e-MEC</span></a>
    <p>© {datetime.date.today().year} {NOME_LONGO}. Todos os direitos reservados.</p>
  </div>
</footer>
{flutuante()}
<script src="assets/js/leaflet.js" defer></script>
<script src="assets/js/site.js?v={js_v}" defer></script>'''


# ───────────── SEO ─────────────
def schema(slug, titulo, descricao):
    org = {
        "@type": ["CollegeOrUniversity", "EducationalOrganization"], "@id": SITE + "/#org", "name": NOME_LONGO, "alternateName": [SIGLA, "Faculdade Regional do Valle", NOME],
        "url": SITE + "/", "logo": SITE + "/assets/img/farvalle-logo.png", "image": SITE + "/assets/img/og.jpg", "description": descricao,
        "telephone": "+55 75 98870-8022", "email": EMAIL,
        "address": {"@type": "PostalAddress", "streetAddress": "Avenida Dr. Luís Sande, 147 — Valle Shopping", "addressLocality": "Amargosa", "addressRegion": "BA", "postalCode": "45300-000", "addressCountry": "BR"},
        "geo": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LON}, "hasMap": MAPS, "sameAs": [INSTAGRAM, EMEC],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Cursos de graduação", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Course", "name": c["nome"], "description": c["resumo"], "url": canonica("cursos/" + c["slug"]), "provider": {"@id": SITE + "/#org"},
                                               "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "onsite", "courseWorkload": c["duracao"]}}} for c in CURSOS]},
    }
    graph = [org, {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": NOME, "publisher": {"@id": SITE + "/#org"}, "inLanguage": "pt-BR"},
             {"@type": "WebPage", "@id": canonica(slug) + "#page", "url": canonica(slug), "name": titulo, "description": descricao, "isPartOf": {"@id": SITE + "/#site"}, "inLanguage": "pt-BR"}]
    if slug.startswith("cursos/"):
        c = CURSO[slug.split("/")[1]]
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "Cursos", "item": canonica("cursos")},
            {"@type": "ListItem", "position": 3, "name": c["nome"], "item": canonica(slug)}]})
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_curso(c)]})
    if slug.startswith("noticias/"):
        n = NOTICIA[slug.split("/")[1]]
        graph.append({"@type": "NewsArticle", "headline": n["titulo"], "datePublished": n["data"], "image": SITE + f"/assets/img/{n['foto']}.jpg", "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"}, "description": n["resumo"]})
    if slug == "processo-seletivo":
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_SELETIVO]})
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>"


VERIFICACAO = {"google-site-verification": "", "msvalidate.01": ""}
INDEXNOW_KEY = ""


def pagina(slug, titulo, descricao, corpo, og="assets/img/og.jpg", mapa=False):
    canon = canonica(slug)
    robots = '<meta name="robots" content="noindex, follow">' if slug == "404" else '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">'
    verif = "".join(f'\n<meta name="{k}" content="{v}">' for k, v in VERIFICACAO.items() if v)
    css_v = versao_asset("assets/css/site.css")
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
{robots}{verif}
<link rel="canonical" href="{canon}">
<meta property="og:site_name" content="{NOME}">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{canon}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:image" content="{SITE}/{og}?v=1">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NOME_LONGO} — Amargosa, BA">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo)}">
<meta name="twitter:description" content="{e(descricao)}">
<meta name="twitter:image" content="{SITE}/{og}?v=1">
<meta name="theme-color" content="#17382a">
<link rel="icon" href="assets/img/farvalle-icon.png" type="image/png">
<link rel="apple-touch-icon" href="assets/img/farvalle-icon.png">
<link rel="preload" href="assets/fonts/montserrat-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/montserrat-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
{'<link rel="stylesheet" href="assets/css/leaflet.css">' if mapa else ""}
<link rel="stylesheet" href="assets/css/site.css?v={css_v}">
{schema(slug, titulo, descricao)}
</head>
<body>
{cabecalho(slug)}
<main id="conteudo">
{corpo}
</main>
{rodape()}
</body>
</html>
'''


# ───────────── Componentes ─────────────
def secao_titulo(eyebrow, titulo, texto=None, centro=False, acento=None):
    c = " centro" if centro else ""
    ac = f'<span class="acento acento-sub">{e(acento)}</span>' if acento else ""
    t = f"<p>{e(texto)}</p>" if texto else ""
    return f'<div class="sec-cab{c}"><span class="eyebrow">{e(eyebrow)}</span><h2>{e(titulo)}</h2>{ac}{t}</div>'


def trilho_nav():
    return f'<div class="trilho-nav"><button type="button" data-ant aria-label="Anterior">{I["chev-r"]}</button><div class="trilho-barra"><i></i></div><button type="button" data-prox aria-label="Próximo">{I["chev-r"]}</button></div>'


def lista_check(itens, classe="lista-check"):
    return f'<ul class="{classe}">' + "".join(f"<li>{ic('check')}<span>{e(i)}</span></li>" for i in itens) + "</ul>"


def trilha(itens):
    """Breadcrumb simples."""
    partes = []
    for i, (r, s) in enumerate(itens):
        if s:
            partes.append(f'<a href="{url(s)}">{e(r)}</a>')
        else:
            partes.append(f'<span aria-current="page">{e(r)}</span>')
    return '<nav class="trilha" aria-label="Você está em"><ol>' + "".join(f"<li>{p}</li>" for p in partes) + "</ol></nav>"


def hero_interno(eyebrow, titulo, lead, foto_nome, alt, crumbs, botoes="", pos=None, acento=None):
    ac = f'<span class="acento acento-sub">{e(acento)}</span>' if acento else ""
    return f'''<section class="hero-int">
  <div class="wrap hero-int-in">
    <div class="hero-int-txt">
      {trilha(crumbs)}
      <span class="eyebrow">{e(eyebrow)}</span>
      <h1>{e(titulo)}</h1>{ac}
      <p class="lead">{e(lead)}</p>
      <div class="btns">{botoes}</div>
    </div>
    <div class="hero-int-foto">{foto(foto_nome, alt, prioridade=True, pos=pos)}<span class="hero-int-forma" aria-hidden="true"></span></div>
  </div>
</section>'''


def card_curso(c, compacto=False):
    return f'''<article class="card-curso">
  <a class="card-curso-foto" href="{url('cursos/' + c['slug'])}" aria-label="{e(c['nome'])}">{foto('curso-' + c['slug'], f"Curso de {c['nome']} na Farvalle", pos="center 30%")}<span class="tag">{e(c['grau'])}</span></a>
  <div class="card-curso-in">
    <h3><a href="{url('cursos/' + c['slug'])}">{e(c['nome'])}</a></h3>
    <p>{e(c['tagline'])}</p>
    <ul class="card-curso-meta"><li>{ic('clock','ic-s')}{e(c['duracao'])}</li><li>{ic('building','ic-s')}{e(c['modalidade'])}</li><li>{ic('calendar','ic-s')}{e(c['turno'])}</li></ul>
    <div class="card-curso-acoes"><a class="link-mais" href="{url('cursos/' + c['slug'])}">Conhecer o curso {I['arrow']}</a><a class="btn btn-verde btn-p" href="{url('inscreva-se')}?curso={c['slug']}"><span>Inscreva-se</span></a></div>
  </div>
</article>'''


def cta_faixa(titulo="Seu futuro começa aqui.", texto="Dê o próximo passo com uma formação que transforma realidades e abre novos caminhos. Inscrições abertas para Enfermagem, Fisioterapia e Pedagogia.", foto_nome="cta"):
    return f'''<section class="cta-faixa">
  <div class="wrap cta-faixa-in">
    <div class="cta-faixa-foto">{foto(foto_nome, "Estudante da Farvalle", pos="center 25%")}</div>
    <div class="cta-faixa-txt">
      <span class="eyebrow eyebrow-claro">{EDICAO}</span>
      <h2>{e(titulo)}</h2>
      <p>{e(texto)}</p>
      {lista_check(["Cursos presenciais de qualidade", "Professores experientes", "Estrutura moderna no Valle Shopping", "Conexão com o mercado"], "lista-check lista-check-claro")}
      <div class="btns">{btn("Inscreva-se agora", url("inscreva-se"), "btn btn-laranja", grande=True)}{btn_whats("Falar no WhatsApp", "btn btn-claro", grande=True)}</div>
    </div>
  </div>
</section>'''


def faq_html(itens, classe=""):
    return f'<div class="faq {classe}">' + "".join(f'<details class="faq-item"><summary><span>{e(q)}</span>{I["chev"]}</summary><div class="faq-r"><p>{e(a)}</p></div></details>' for q, a in itens) + "</div>"


def faq_curso(c):
    return [
        (f"Qual é a duração do curso de {c['nome']}?", f"O curso de {c['nome']} ({c['grau']}) tem duração de {c['duracao']}, em modalidade {c['modalidade'].lower()}, com aulas no turno {c['turno'].lower()} no campus Valle Shopping, em Amargosa/BA."),
        (f"Como faço para me inscrever em {c['nome']}?", "Pelo formulário de inscrição do site, escolhendo o curso e a forma de ingresso: Vestibular Online (com redação), Nota do ENEM, Transferência Externa ou Segunda Graduação. A secretaria entra em contato para concluir a matrícula."),
        ("A Farvalle é reconhecida pelo MEC?", "Sim. A Faculdade Regional do Valle está cadastrada no sistema e-MEC do Ministério da Educação. O link para consulta pública está no rodapé do site."),
    ]


FAQ_SELETIVO = [
    ("Quais cursos estão com inscrições abertas?", "Enfermagem (Bacharelado), Fisioterapia (Bacharelado) e Pedagogia (Licenciatura), todos presenciais e no turno noturno."),
    ("Como funciona o Vestibular Online?", "Você preenche o formulário de inscrição e escreve a redação dissertativo-argumentativa sobre o tema proposto no próprio site. Depois, a secretaria acadêmica entra em contato com o resultado e as orientações de matrícula."),
    ("Posso usar a nota do ENEM?", "Sim. Escolha a opção “Nota do ENEM” no formulário; a secretaria vai solicitar o boletim de uma edição anterior do exame para a análise."),
    ("Quais documentos são necessários para a matrícula?", "Documento de identidade, CPF, certificado e histórico do ensino médio, comprovante de residência e foto 3x4. Para transferência e segunda graduação, também o histórico e as ementas da instituição de origem. A secretaria confirma a lista completa no contato."),
    ("Onde ficam as aulas?", f"No campus da Farvalle no Valle Shopping — {ENDERECO}, {CIDADE.split(' ·')[0]}. Aulas 100% presenciais."),
    ("Tenho dúvidas. Com quem falo?", f"Pelo WhatsApp {TELEFONE}, pelo e-mail {EMAIL} ou pessoalmente na secretaria acadêmica."),
]


def mapa_bloco():
    return f'''<div class="mapa">
  <div class="mapa-frame" id="mapa-interativo" data-lat="{LAT}" data-lon="{LON}" data-nome="{NOME}" data-end="{e(ENDERECO)} · Amargosa/BA" role="application" aria-label="Mapa interativo com a localização da Faculdade Farvalle"></div>
  <div class="mapa-etiqueta">{ic("pin")}<span><strong>{NOME} · Valle Shopping</strong>{e(ENDERECO)} — {e(CIDADE)}</span></div>
</div>'''


# ───────────── Páginas ─────────────
def home():
    slides = [
        dict(eyebrow=EDICAO + " · Inscrições abertas", t1="Educação de hoje para um amanhã", ac="com mais oportunidades.", txt="Na Farvalle, você encontra formação de qualidade, professores experientes e um ambiente que valoriza pessoas, histórias e novos caminhos.", foto="hero-estudantes", alt="Estudantes da Farvalle", b1=("Inscreva-se", "inscreva-se"), b2=("Conheça os cursos", "cursos"), pos="center 25%"),
        dict(eyebrow="Enfermagem · Fisioterapia · Pedagogia", t1="Três graduações presenciais", ac="no coração de Amargosa.", txt="Cursos noturnos, com base científica, prática qualificada e professores que conhecem a realidade da região.", foto="curso-enfermagem-hero", alt="Estudante de Enfermagem da Farvalle", b1=("Ver os cursos", "cursos"), b2=("Formas de ingresso", "processo-seletivo"), pos="center 30%"),
        dict(eyebrow="Campus Valle Shopping", t1="Uma faculdade pertinho", ac="de você.", txt="Infraestrutura completa no Valle Shopping, fácil acesso e um ambiente acolhedor para estudar e crescer.", foto="predio", alt="Campus da Farvalle no Valle Shopping", b1=("Conheça a Farvalle", "a-farvalle"), b2=("Como chegar", "contato#mapa"), pos="center 60%"),
    ]
    sl = ""
    for i, s in enumerate(slides):
        sl += f'''<div class="hero-slide{" ativo" if i == 0 else ""}" role="group" aria-roledescription="slide" aria-label="{i+1} de {len(slides)}">
      <div class="hero-txt">
        <span class="eyebrow">{e(s["eyebrow"])}</span>
        <h{1 if i == 0 else 2} class="hero-h">{e(s["t1"])}</h{1 if i == 0 else 2}><span class="acento acento-sub acento-hero">{e(s["ac"])}</span>
        <p class="lead">{e(s["txt"])}</p>
        <div class="btns">{btn(s["b1"][0], url(s["b1"][1]), "btn btn-laranja", grande=True)}{btn(s["b2"][0], url(s["b2"][1]), "btn btn-contorno", grande=True)}</div>
      </div>
      <div class="hero-foto">{foto(s["foto"], s["alt"], prioridade=(i == 0), pos=s["pos"])}</div>
    </div>'''
    pontos = "".join(f'<button type="button" aria-label="Destaque {i+1}"{" aria-current=\"true\"" if i == 0 else ""}></button>' for i in range(len(slides)))
    hero = f'''<section class="hero" data-hero>
  <div class="wrap hero-in">{sl}
    <div class="hero-ctl"><button type="button" class="hero-seta" data-hero-ant aria-label="Destaque anterior">{I["chev-r"]}</button><div class="hero-pontos">{pontos}</div><button type="button" class="hero-seta" data-hero-prox aria-label="Próximo destaque">{I["chev-r"]}</button></div>
  </div>
</section>'''

    # fileira de acesso rápido (estilo Mackenzie: cartões de entrada)
    entradas = [
        ("grad", "Graduação", "Vestibular " + EDICAO.split()[-1], [("Enfermagem", "cursos/enfermagem"), ("Fisioterapia", "cursos/fisioterapia"), ("Pedagogia", "cursos/pedagogia")], "cursos"),
        ("laptop", "Processo Seletivo", "4 formas de ingresso", [(i["nome"], "processo-seletivo#" + i["slug"]) for i in INGRESSO], "processo-seletivo"),
        ("calendar", "Vida Acadêmica", "Calendário e regulamentos", [("Calendário Acadêmico", "publicacoes-institucionais#calendario"), ("Regulamentos", "publicacoes-institucionais#regulamentos"), ("Notícias", "noticias")], "publicacoes-institucionais"),
        ("portal", "Portal do Aluno", "Acesso do estudante", [("Portal do Aluno", PORTAL), ("Acesse o Portal", JASMIN), ("Secretaria acadêmica", "contato")], PORTAL),
    ]
    ent = ""
    for icone, t, sub, links, href in entradas:
        lis = "".join(f'<li><a href="{url(s)}"{" target=\"_blank\" rel=\"noopener\"" if s.startswith("http") else ""}>{e(r)}</a></li>' for r, s in links)
        ent += f'<article class="entrada"><div class="entrada-cab">{ic(icone, "ic-circ")}<div><h3>{e(t)}</h3><span>{e(sub)}</span></div></div><ul>{lis}</ul><a class="link-mais" href="{url(href)}"{" target=\"_blank\" rel=\"noopener\"" if href.startswith("http") else ""}>Acessar {I["arrow"]}</a></article>'
    entradas_html = f'<section class="entradas"><div class="wrap"><div class="entradas-grade" data-trilho>{ent}</div>{trilho_nav()}</div></section>'

    cursos_html = f'''<section class="sec sec-cursos" id="cursos">
  <div class="wrap">
    <div class="sec-cab-linha">{secao_titulo("Graduação", "Escolha o seu curso", acento="e comece a sua história.")}{btn("Todos os Cursos", url("cursos"), "btn btn-contorno sec-cab-btn")}</div>
    <div class="cursos-trilho" data-trilho>{"".join(card_curso(c) for c in CURSOS)}</div>{trilho_nav()}
  </div>
</section>'''

    porque = f'''<section class="sec sec-porque">
  <div class="wrap porque-in">
    <div class="porque-txt">
      {secao_titulo("Por que escolher a Farvalle", "Pessoas hoje.", acento="Grandes histórias amanhã.")}
      <p>A Farvalle – Faculdade Regional do Valle é uma instituição de ensino superior próxima da comunidade, que acredita no poder da educação para transformar vidas. Com foco na formação de profissionais qualificados e no desenvolvimento regional, oferecemos um ambiente acolhedor, inovador e cheio de oportunidades.</p>
      <ul class="porque-lista">
        <li>{ic("grad","ic-circ")}<div><strong>Educação de qualidade</strong><span>Base científica, prática qualificada e professores experientes.</span></div></li>
        <li>{ic("growth","ic-circ")}<div><strong>Desenvolvimento pessoal e profissional</strong><span>Formação que prepara para o mercado e para a vida.</span></div></li>
        <li>{ic("community","ic-circ")}<div><strong>Conexão com a comunidade</strong><span>Projetos, parcerias e extensão no Vale do Jiquiriçá.</span></div></li>
        <li>{ic("idea","ic-circ")}<div><strong>Mais oportunidades para o seu futuro</strong><span>Estágios e vivências que aproximam você da profissão.</span></div></li>
      </ul>
      <div class="btns">{btn("Conheça a Farvalle", url("a-farvalle"), "btn btn-verde")}</div>
    </div>
    <div class="porque-fotos">
      {foto("insc-cta", "Estudante da Farvalle", "porque-f1", pos="center 15%")}
      {foto("news-3", "Estudantes conversando no campus", "porque-f2", pos="center 40%")}
      <div class="porque-selo">{ic("shield")}<span><strong>Cadastrada no e-MEC</strong>Instituição de ensino superior reconhecida pelo MEC</span></div>
    </div>
  </div>
</section>'''

    numeros = f'''<section class="sec sec-numeros">
  <div class="wrap">
    {secao_titulo("Farvalle em números", "Mais pessoas, mais histórias,", acento="mais futuro.", centro=True)}
    <div class="numeros" data-trilho>
      <div class="numero">{ic("grad","ic-circ")}<strong>3</strong><span>cursos de graduação presencial</span></div>
      <div class="numero">{ic("laptop","ic-circ")}<strong>4</strong><span>formas de ingresso, com vestibular online</span></div>
      <div class="numero">{ic("building","ic-circ")}<strong>1</strong><span>campus no Valle Shopping, no coração de Amargosa</span></div>
      <div class="numero">{ic("region","ic-circ")}<strong>100%</strong><span>presencial, com turmas no turno noturno</span></div>
    </div>{trilho_nav()}
  </div>
</section>'''

    ingresso = "".join(f'''<a class="ingresso" href="{url("processo-seletivo#" + i["slug"])}">{ic(i["icone"], "ic-circ")}<h3>{e(i["nome"])}</h3><span class="tag tag-claro">{e(i["curto"])}</span><p>{e(i["texto"])}</p><span class="link-mais">Saiba mais {I["arrow"]}</span></a>''' for i in INGRESSO)
    ingresso_html = f'''<section class="sec sec-ingresso">
  <div class="wrap">
    <div class="sec-cab-linha">{secao_titulo("Processo Seletivo", "Quatro formas de entrar", acento="na Farvalle.")}{btn("Inscreva-se", url("inscreva-se"), "btn btn-laranja sec-cab-btn")}</div>
    <div class="ingresso-grade" data-trilho>{ingresso}</div>{trilho_nav()}
  </div>
</section>'''

    not_cards = "".join(card_noticia(n) for n in NOTICIAS)
    noticias_html = f'''<section class="sec sec-noticias" id="noticias">
  <div class="wrap">
    <div class="sec-cab-linha">{secao_titulo("Destaques", "Notícias e eventos", acento="da Farvalle.")}{btn("Todas as Notícias", url("noticias"), "btn btn-contorno sec-cab-btn")}</div>
    <div class="noticias-grade" data-trilho>{not_cards}</div>{trilho_nav()}
  </div>
</section>'''

    servicos = [
        ("portal", "Portal do Aluno", "Notas, frequência, documentos e comunicados do estudante.", PORTAL, True),
        ("calendar", "Calendário Acadêmico", "Datas, períodos letivos e prazos importantes do semestre.", "publicacoes-institucionais#calendario", False),
        ("book", "Regulamentos", "Documentos e orientações institucionais da faculdade.", "publicacoes-institucionais#regulamentos", False),
        ("chat", "Secretaria Acadêmica", "Atendimento ao candidato e ao aluno, presencial e pelo WhatsApp.", "contato", False),
    ]
    serv = "".join(f'<a class="servico" href="{url(h)}"{" target=\"_blank\" rel=\"noopener\"" if ext else ""}>{ic(i, "ic-circ ic-circ-claro")}<h3>{e(t)}</h3><p>{e(d)}</p><span class="link-mais link-mais-claro">Acessar {I["arrow"]}</span></a>' for i, t, d, h, ext in servicos)
    servicos_html = f'''<section class="sec sec-servicos">
  <div class="wrap">
    {secao_titulo("Serviços e acesso", "Tudo o que o estudante precisa,", acento="em um só lugar.", centro=True)}
    <div class="servicos-grade" data-trilho>{serv}</div>{trilho_nav()}
  </div>
</section>'''

    campus = f'''<section class="sec sec-campus" id="campus">
  <div class="wrap campus-in">
    <div class="campus-foto">{foto("predio", "Campus da Farvalle no Valle Shopping", pos="center 55%")}</div>
    <div class="campus-txt">
      {secao_titulo("Campus Valle Shopping", "No coração de Amargosa", acento="e do Recôncavo Baiano.")}
      <p>Na Farvalle você encontra aulas 100% presenciais, em um campus bem localizado no Valle Shopping, com infraestrutura completa e um corpo docente qualificado que permite explorar o máximo do seu potencial.</p>
      <ul class="campus-lista">
        <li>{ic("pin")}<span>{e(ENDERECO)}<br>{e(CIDADE)}</span></li>
        <li>{ic("clock")}<span>{e(HORARIO)}</span></li>
        <li>{ic("phone")}<a href="{tel(TELEFONE)}">{TELEFONE}</a></li>
      </ul>
      <div class="btns">{btn("Como chegar", url("contato#mapa"), "btn btn-verde", "map")}{btn("Traçar rota no Maps", MAPS_ROTA, "btn btn-contorno", "arrow", externo=True)}</div>
    </div>
  </div>
</section>'''

    insta = f'''<section class="sec sec-insta">
  <div class="wrap insta-in">
    {ic("insta", "ic-circ ic-circ-g")}
    <div><span class="eyebrow">Acompanhe a Farvalle</span><h2>Siga {INSTA_USER} no Instagram</h2><p>Bastidores das aulas, eventos, avisos e a rotina de quem já faz parte da nossa história.</p></div>
    {btn("Seguir no Instagram", INSTAGRAM, "btn btn-verde", "insta", externo=True)}
  </div>
</section>'''

    return hero + entradas_html + cursos_html + porque + numeros + ingresso_html + noticias_html + servicos_html + campus + cta_faixa() + insta


def card_noticia(n):
    return f'''<article class="card-not">
  <a class="card-not-foto" href="{url('noticias/' + n['slug'])}" aria-label="{e(n['titulo'])}">{foto(n['foto'], "", pos="center 35%")}</a>
  <div class="card-not-in">
    <div class="card-not-meta"><span class="tag">{e(n['categoria'])}</span><time datetime="{n['data']}">{e(n['data_txt'])}</time></div>
    <h3><a href="{url('noticias/' + n['slug'])}">{e(n['titulo'])}</a></h3>
    <p>{e(n['resumo'])}</p>
    <a class="link-mais" href="{url('noticias/' + n['slug'])}">Ler mais {I['arrow']}</a>
  </div>
</article>'''


def a_farvalle():
    valores = [
        ("grad", "Formação de qualidade", "Cursos presenciais com base científica, prática qualificada e compromisso com o cuidado integral."),
        ("user", "Professores experientes", "Corpo docente com vivência de mercado e dedicação ao desenvolvimento de cada estudante."),
        ("building", "Estrutura completa", "Laboratórios, salas modernas e um campus pertinho de você, no Valle Shopping."),
        ("handshake", "Conexão com o mercado", "Parcerias, estágios e projetos que aproximam o estudante da realidade profissional."),
        ("care", "Acolhimento e oportunidades", "Um ambiente próximo da comunidade, que valoriza pessoas, histórias e novos caminhos."),
    ]
    val = "".join(f'<div class="valor">{ic(i, "ic-circ")}<h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in valores)
    corpo = hero_interno("A Farvalle", "Mais que uma faculdade,", "A Farvalle acredita no potencial das pessoas e no desenvolvimento da nossa região. No coração de Amargosa e do Recôncavo Baiano, oferecemos educação que gera oportunidades para a nossa gente e para o território.",
                         "hero-estudantes", "Estudantes da Farvalle", [("Início", "index"), ("A Farvalle", None)],
                         btn("Conheça os cursos", url("cursos"), "btn btn-verde") + btn_whats("Fale com a gente"), pos="center 25%", acento="parte da nossa história.")
    corpo += f'''<section class="sec sec-historia">
  <div class="wrap historia-in">
    <div class="historia-txt">
      {secao_titulo("Nossa história", "Uma faculdade nascida", acento="no Vale do Jiquiriçá.")}
      <p>A história da Faculdade Regional do Valle, FARVALLE, está intimamente ligada ao percurso profissional e à vida de sua idealizadora, a professora Vera Lúcia Suzart de Almeida Bellato Maciel. Diante de sua experiência na gestão, no ensino, na pesquisa e na extensão, pautados na capacidade inovadora e empreendedora, surgiu o interesse na criação da FARVALLE com o objetivo de contribuir para o desenvolvimento socioeconômico, cultural e ambiental da sociedade baiana.</p>
      <p>Na FARVALLE você encontra aulas 100% presenciais, em um campus bem localizado no Valle Shopping, com infraestrutura completa e um corpo docente qualificado que permite explorar o máximo do seu potencial.</p>
      <div class="historia-marcos" data-trilho>
        <div class="marco"><strong>2024.1</strong><span>A Farvalle chega a todo o Vale e região, com Enfermagem, Fisioterapia e Pedagogia.</span></div>
        <div class="marco"><strong>2024.2</strong><span>Semana de Acolhimento e primeiro dia letivo no campus Valle Shopping.</span></div>
        <div class="marco"><strong>2026.2</strong><span>Novo vestibular com quatro formas de ingresso e inscrição online.</span></div>
      </div>{trilho_nav()}
    </div>
    <aside class="historia-card" id="campus">
      {foto("predio", "Campus da Farvalle no Valle Shopping", pos="center 55%")}
      <div>{ic("pin","ic-circ")}<strong>Campus Valle Shopping</strong><p>{e(ENDERECO)} — {e(CIDADE)}. Aulas 100% presenciais, pertinho de você.</p>{btn("Como chegar", url("contato#mapa"), "btn btn-verde btn-p", "map")}</div>
    </aside>
  </div>
</section>
<section class="sec sec-valores" id="valores">
  <div class="wrap">
    {secao_titulo("Por que escolher a Farvalle", "Educação que gera oportunidades", acento="para a nossa gente e para o território.", centro=True)}
    <div class="valores-grade" data-trilho>{val}</div>{trilho_nav()}
  </div>
</section>
<section class="sec sec-missao">
  <div class="wrap missao-grade">
    <div class="missao"><span class="eyebrow">Missão</span><p>Formar profissionais qualificados, éticos e comprometidos com o desenvolvimento socioeconômico, cultural e ambiental do Vale do Jiquiriçá e da Bahia.</p></div>
    <div class="missao"><span class="eyebrow">Visão</span><p>Ser referência regional em ensino superior presencial, reconhecida pela qualidade acadêmica e pela proximidade com a comunidade.</p></div>
    <div class="missao"><span class="eyebrow">Valores</span><p>Compromisso, ética e responsabilidade — valores que utilizamos na formação de cada estudante, retribuindo à sociedade e contribuindo para melhorar a vida das pessoas.</p></div>
  </div>
</section>
<section class="sec sec-emec">
  <div class="wrap emec-in">
    <img src="assets/img/e-mec.webp" alt="e-MEC — Ministério da Educação" width="1024" height="362" loading="lazy">
    <div><h2>Instituição cadastrada no e-MEC</h2><p>A Faculdade Regional do Valle consta no cadastro nacional de instituições de ensino superior do Ministério da Educação. Consulte os dados públicos da instituição.</p></div>
    {btn("Consultar no e-MEC", EMEC, "btn btn-contorno", externo=True)}
  </div>
</section>'''
    corpo += cta_faixa()
    return corpo


def cursos_pg():
    cards = "".join(card_curso(c) for c in CURSOS)
    comp = "".join(f'<tr><th scope="row"><a href="{url("cursos/" + c["slug"])}">{e(c["nome"])}</a></th><td>{e(c["grau"])}</td><td>{e(c["duracao"])}</td><td>{e(c["turno"])}</td><td>{e(c["modalidade"])}</td><td><a class="btn btn-verde btn-p" href="{url("inscreva-se")}?curso={c["slug"]}"><span>Inscreva-se</span></a></td></tr>' for c in CURSOS)
    corpo = hero_interno("Graduação", "Três cursos presenciais", "Enfermagem, Fisioterapia e Pedagogia: graduações noturnas, com base científica, prática qualificada e professores que conhecem a realidade da região.",
                         "curso-fisioterapia-hero", "Estudante de Fisioterapia da Farvalle", [("Início", "index"), ("Cursos", None)],
                         btn("Inscreva-se", url("inscreva-se"), "btn btn-laranja") + btn("Formas de ingresso", url("processo-seletivo"), "btn btn-contorno"), pos="center 30%", acento="para transformar o seu futuro.")
    corpo += f'''<section class="sec">
  <div class="wrap">
    {secao_titulo("Cursos", "Escolha o seu curso", acento="e comece a sua história.")}
    <div class="cursos-trilho" data-trilho>{cards}</div>{trilho_nav()}
  </div>
</section>
<section class="sec sec-cinza">
  <div class="wrap">
    {secao_titulo("Visão geral", "Compare os cursos", centro=True)}
    <div class="tabela-wrap"><table class="tabela">
      <thead><tr><th>Curso</th><th>Grau</th><th>Duração</th><th>Turno</th><th>Modalidade</th><th></th></tr></thead>
      <tbody>{comp}</tbody>
    </table></div>
    <p class="nota">Turno e coordenação de cada curso: confirmar com a secretaria acadêmica.</p>
  </div>
</section>'''
    corpo += cta_faixa()
    return corpo


def curso_pg(c):
    outros = [o for o in CURSOS if o["slug"] != c["slug"]]
    outros_html = "".join(card_curso(o) for o in outros)
    corpo = hero_interno(f"{c['grau']} · {c['modalidade']}", c["nome"], c["resumo"], "curso-" + c["slug"] + "-hero", f"Estudante de {c['nome']} da Farvalle",
                         [("Início", "index"), ("Cursos", "cursos"), (c["nome"], None)],
                         btn("Inscreva-se", url("inscreva-se") + "?curso=" + c["slug"], "btn btn-laranja") + btn_whats("Tirar dúvidas"), pos="center 30%", acento=c["tagline"])
    corpo += f'''<section class="ficha">
  <div class="wrap ficha-grade" data-trilho>
    <div class="ficha-item">{ic("grad","ic-circ")}<span>Grau</span><strong>{e(c["grau"])}</strong></div>
    <div class="ficha-item">{ic("clock","ic-circ")}<span>Duração</span><strong>{e(c["duracao"])}</strong></div>
    <div class="ficha-item">{ic("calendar","ic-circ")}<span>Turno</span><strong>{e(c["turno"])}</strong></div>
    <div class="ficha-item">{ic("building","ic-circ")}<span>Modalidade</span><strong>{e(c["modalidade"])}</strong></div>
    <div class="ficha-item">{ic("pin","ic-circ")}<span>Campus</span><strong>Valle Shopping</strong></div>
  </div>
</section>
<section class="sec">
  <div class="wrap dupla">
    <div class="dupla-foto">{foto("curso-" + c["slug"] + "-sobre", f"Aula prática do curso de {c['nome']}", pos="center 20%")}</div>
    <div class="dupla-txt">
      {secao_titulo("Sobre o curso", c["nome"] + " na Farvalle")}
      {"".join(f"<p>{e(p)}</p>" for p in c["sobre"])}
      <h3 class="h-sub">Áreas de atuação</h3>
      <ul class="chips">{"".join(f"<li>{e(a)}</li>" for a in c["areas"])}</ul>
    </div>
  </div>
</section>
<section class="sec sec-cinza">
  <div class="wrap dupla dupla-inv">
    <div class="dupla-txt">
      {secao_titulo("Para quem é", "Esse curso é para você", acento="se…")}
      {lista_check(c["para_quem"])}
      <div class="btns">{btn("Inscreva-se em " + c["nome"], url("inscreva-se") + "?curso=" + c["slug"], "btn btn-laranja")}</div>
    </div>
    <div class="dupla-foto">{foto("curso-" + c["slug"], f"Estudantes de {c['nome']}", pos="center 30%")}</div>
  </div>
</section>
<section class="sec">
  <div class="wrap">
    {secao_titulo("Como entrar", "Quatro formas de ingresso", centro=True)}
    <div class="passos" data-trilho>{"".join(f'<a class="passo" href="{url("processo-seletivo#" + i["slug"])}">{ic(i["icone"], "ic-circ")}<strong>{e(i["nome"])}</strong><span>{e(i["curto"])}</span></a>' for i in INGRESSO)}</div>{trilho_nav()}
  </div>
</section>
<section class="sec sec-cinza">
  <div class="wrap faq-wrap">
    {secao_titulo("Dúvidas frequentes", "Sobre " + c["nome"])}
    {faq_html(faq_curso(c))}
  </div>
</section>
<section class="sec">
  <div class="wrap">
    <div class="sec-cab-linha">{secao_titulo("Outros cursos", "Conheça também")}{btn("Todos os Cursos", url("cursos"), "btn btn-contorno sec-cab-btn")}</div>
    <div class="cursos-trilho cursos-trilho-2" data-trilho>{outros_html}</div>{trilho_nav()}
  </div>
</section>'''
    corpo += cta_faixa()
    return corpo


def processo_seletivo_pg():
    blocos = ""
    for i in INGRESSO:
        passos = "".join(f"<li><span>{k+1}</span>{e(p)}</li>" for k, p in enumerate(i["passos"]))
        blocos += f'''<article class="forma" id="{i["slug"]}">
  <div class="forma-cab">{ic(i["icone"], "ic-circ")}<div><span class="tag tag-claro">{e(i["curto"])}</span><h3>{e(i["nome"])}</h3></div></div>
  <p>{e(i["texto"])}</p>
  <ol class="forma-passos">{passos}</ol>
  {btn("Inscrever-se por " + i["nome"], url("inscreva-se") + "?ingresso=" + quote(i["nome"]), "btn btn-verde")}
</article>'''
    corpo = hero_interno("Processo Seletivo", EDICAO, "Escolha a forma de ingresso que combina com a sua história: vestibular online com redação, nota do ENEM, transferência externa ou segunda graduação. A inscrição é feita pelo site, sem sair de casa.",
                         "curso-pedagogia-hero", "Estudante da Farvalle", [("Início", "index"), ("Processo Seletivo", None)],
                         btn("Inscreva-se agora", url("inscreva-se"), "btn btn-laranja") + btn_whats("Tirar dúvidas"), pos="center 30%", acento="inscrições abertas.")
    corpo += f'''<section class="sec">
  <div class="wrap">
    {secao_titulo("Formas de ingresso", "Quatro caminhos", acento="para entrar na Farvalle.")}
    <div class="formas-grade">{blocos}</div>
  </div>
</section>
<section class="sec sec-cinza">
  <div class="wrap">
    {secao_titulo("Passo a passo", "Da inscrição à matrícula", centro=True)}
    <ol class="linha-tempo" data-trilho>
      <li><span>1</span><strong>Inscrição online</strong><p>Preencha o formulário com seus dados, o curso e a forma de ingresso.</p></li>
      <li><span>2</span><strong>Redação ou documentos</strong><p>Escreva a redação (Vestibular Online) ou apresente ENEM, histórico ou diploma.</p></li>
      <li><span>3</span><strong>Contato da secretaria</strong><p>A secretaria acadêmica confirma o resultado e orienta sobre a matrícula.</p></li>
      <li><span>4</span><strong>Matrícula</strong><p>Entrega dos documentos e início das aulas no campus Valle Shopping.</p></li>
    </ol>{trilho_nav()}
  </div>
</section>
<section class="sec">
  <div class="wrap faq-wrap">
    {secao_titulo("Dúvidas frequentes", "Sobre o processo seletivo")}
    {faq_html(FAQ_SELETIVO)}
  </div>
</section>'''
    corpo += cta_faixa()
    return corpo


def inscreva_se_pg():
    conheceu = ["Facebook", "Instagram", "Google", "Whatsapp", "Panfleto", "Site", "Amigo", "Outros"]
    op = lambda xs: "".join(f'<option value="{e(x)}">{e(x)}</option>' for x in xs)
    corpo = hero_interno("Inscrição online", "Inscreva-se no " + EDICAO, "Preencha os dados abaixo. Se escolher o Vestibular Online, escreva a sua redação no próprio formulário. A secretaria acadêmica entra em contato em seguida.",
                         "cta", "Candidata fazendo a inscrição online", [("Início", "index"), ("Processo Seletivo", "processo-seletivo"), ("Inscreva-se", None)], "", pos="center 20%", acento="e comece hoje.")
    corpo += f'''<section class="sec sec-form">
  <div class="wrap form-grade">
    <form class="form" id="form-inscricao" novalidate data-destino="{EMAIL_SECRETARIA}">
      <h2 class="form-h">Dados do candidato</h2>
      <div class="campos">
        <label class="campo campo-2"><span>Nome completo</span><input type="text" name="nome" autocomplete="name" required></label>
        <label class="campo"><span>Celular / WhatsApp</span><input type="tel" name="tel" inputmode="tel" autocomplete="tel" placeholder="(XX) XXXXX-XXXX" required></label>
        <label class="campo"><span>E-mail</span><input type="email" name="email" autocomplete="email" required></label>
        <label class="campo"><span>Cidade</span><input type="text" name="city" autocomplete="address-level2" required></label>
        <label class="campo"><span>Como conheceu a Farvalle?</span><select name="conheceu" required><option value="" disabled selected>Selecione</option>{op(conheceu)}</select></label>
        <label class="campo"><span>Como deseja ingressar?</span><select name="ingresso" id="ingresso" required><option value="" disabled selected>Selecione</option>{op([i["nome"] for i in INGRESSO])}</select></label>
        <label class="campo"><span>Curso desejado</span><select name="course" id="course" required><option value="" disabled selected>Selecione</option>{"".join(f'<option value="{e(c["nome"])}" data-slug="{c["slug"]}">{e(c["nome"])}</option>' for c in CURSOS)}</select></label>
      </div>
      <div class="redacao" id="bloco-redacao" hidden>
        <h2 class="form-h">Redação — Vestibular Online</h2>
        <div class="redacao-tema">
          <div class="redacao-instr">{ic("file","ic-circ")}<div><strong>Instruções</strong><ul><li>Leia com atenção o tema proposto.</li><li>Será anulada a redação redigida fora do tema proposto ou apresentada em forma de verso.</li><li>Mínimo de 20 linhas.</li></ul></div></div>
          <h3>Tema: Exclusão Social</h3>
          <p>A Exclusão Social designa um processo de afastamento e privação de determinados indivíduos ou de grupos sociais em diversos âmbitos da estrutura da sociedade. Trata-se de uma condição inerente ao capitalismo contemporâneo, ou seja, esse problema social foi impulsionado pela estrutura desse sistema econômico e político.</p>
          <p>Com base nos conhecimentos construídos ao longo de sua formação, redija texto dissertativo-argumentativo em modalidade escrita formal da língua portuguesa sobre o tema “Exclusão Social”, apresentando proposta de intervenção que respeite os direitos humanos. Selecione, organize e relacione, de forma coerente e coesa, argumentos e fatos para defesa de seu ponto de vista.</p>
        </div>
        <label class="campo campo-2"><span>Sua redação</span><textarea name="text" id="texto-redacao" rows="14" placeholder="Digite sua redação aqui…"></textarea><small class="contador" id="contador">0 palavras</small></label>
      </div>
      <label class="campo-check"><input type="checkbox" name="lgpd" required><span>Autorizo o uso dos meus dados para o contato da secretaria acadêmica sobre a minha inscrição, conforme a <a href="{url('privacidade')}">política de privacidade</a>.</span></label>
      <p class="form-erro" id="form-erro" hidden role="alert"></p>
      <div class="form-acoes">{btn("Enviar inscrição", "#", "btn btn-laranja btn-g", "arrow").replace('<a ', '<button type="submit" ').replace('href="#"', '').replace('</a>', '</button>')}<span class="form-nota">Suas informações vão para a secretaria acadêmica ({EMAIL_SECRETARIA}).</span></div>
      <div class="form-ok" id="form-ok" hidden tabindex="-1">{ic("check","ic-circ")}<h2>Inscrição enviada!</h2><p>Recebemos os seus dados. A secretaria acadêmica entra em contato pelo WhatsApp ou e-mail informados.</p>{btn_whats("Falar com a secretaria agora", "btn btn-verde")}</div>
    </form>
    <aside class="form-lado">
      <div class="lado-card">
        <h3>Como funciona</h3>
        <ol class="forma-passos">
          <li><span>1</span>Preencha os dados e escolha curso e forma de ingresso.</li>
          <li><span>2</span>No Vestibular Online, escreva a redação no próprio formulário.</li>
          <li><span>3</span>A secretaria entra em contato com o resultado e a matrícula.</li>
        </ol>
      </div>
      <div class="lado-card lado-card-verde">
        <h3>Dúvidas?</h3>
        <p>Fale com a secretaria acadêmica pelo WhatsApp ou e-mail.</p>
        <p>{ic("whats")}<a href="{wa()}" target="_blank" rel="noopener">{TELEFONE}</a></p>
        <p>{ic("mail")}<a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <p>{ic("clock")}<span>{e(HORARIO)}</span></p>
      </div>
      <div class="lado-card lado-foto">{foto("cta", "Estudante da Farvalle", pos="center 20%")}<span>Seu futuro começa aqui.</span></div>
    </aside>
  </div>
</section>'''
    return corpo


def publicacoes_pg():
    corpo = hero_interno("Vida Acadêmica", "Publicações institucionais", "Calendário acadêmico, regulamentos e documentos oficiais da Faculdade Regional do Valle, reunidos em um só lugar.",
                         "news-1", "Estudantes da Farvalle em sala", [("Início", "index"), ("Vida Acadêmica", None)],
                         btn("Portal do Aluno", PORTAL, "btn btn-verde", "portal", externo=True) + btn_whats("Falar com a secretaria"), pos="center 40%", acento="e documentos.")
    corpo += f'''<section class="sec">
  <div class="wrap pub-grade">
    <article class="pub" id="calendario">
      <div class="pub-cab">{ic("calendar","ic-circ")}<h2>Calendário Acadêmico</h2></div>
      <p>Datas de início e fim dos períodos letivos, feriados, prazos de matrícula, rematrícula e avaliações. O calendário vigente é publicado pela secretaria acadêmica a cada semestre.</p>
      <ul class="pub-lista">
        <li>{ic("file")}<span>Calendário Acadêmico 2026.2</span><a class="link-mais" href="{PORTAL}" target="_blank" rel="noopener">Ver no portal {I["arrow"]}</a></li>
        <li>{ic("file")}<span>Calendário de avaliações</span><a class="link-mais" href="{PORTAL}" target="_blank" rel="noopener">Ver no portal {I["arrow"]}</a></li>
      </ul>
    </article>
    <article class="pub" id="regulamentos">
      <div class="pub-cab">{ic("book","ic-circ")}<h2>Regulamentos Institucionais</h2></div>
      <p>Documentos e orientações que organizam a vida acadêmica: regimento, normas de avaliação, estágio, atividades complementares e política de privacidade.</p>
      <ul class="pub-lista">
        <li>{ic("file")}<span>Regimento Geral</span><a class="link-mais" href="mailto:{EMAIL_SECRETARIA}?subject=Solicita%C3%A7%C3%A3o%20de%20documento">Solicitar à secretaria {I["arrow"]}</a></li>
        <li>{ic("file")}<span>Regulamento de estágio e atividades complementares</span><a class="link-mais" href="mailto:{EMAIL_SECRETARIA}?subject=Solicita%C3%A7%C3%A3o%20de%20documento">Solicitar à secretaria {I["arrow"]}</a></li>
        <li>{ic("file")}<span>Política de Privacidade</span><a class="link-mais" href="{url('privacidade')}">Ler {I["arrow"]}</a></li>
      </ul>
    </article>
    <article class="pub" id="editais">
      <div class="pub-cab">{ic("medalha","ic-circ")}<h2>Editais e Processos Seletivos</h2></div>
      <p>Vestibular, seleções e informações institucionais do semestre vigente.</p>
      <ul class="pub-lista">
        <li>{ic("file")}<span>{EDICAO} — formas de ingresso</span><a class="link-mais" href="{url('processo-seletivo')}">Ver {I["arrow"]}</a></li>
        <li>{ic("file")}<span>Inscrição online</span><a class="link-mais" href="{url('inscreva-se')}">Inscrever-se {I["arrow"]}</a></li>
      </ul>
    </article>
    <article class="pub" id="emec">
      <div class="pub-cab">{ic("shield","ic-circ")}<h2>Cadastro no e-MEC</h2></div>
      <p>Consulte os dados públicos da instituição no cadastro nacional do Ministério da Educação.</p>
      <ul class="pub-lista"><li>{ic("file")}<span>Faculdade Regional do Valle — e-MEC</span><a class="link-mais" href="{EMEC}" target="_blank" rel="noopener">Consultar {I["arrow"]}</a></li></ul>
    </article>
  </div>
  <p class="nota wrap">Os documentos listados são disponibilizados pela secretaria acadêmica. Para atualizar um arquivo, envie para {EMAIL_SECRETARIA}.</p>
</section>'''
    corpo += cta_faixa()
    return corpo


def noticias_pg():
    cards = "".join(card_noticia(n) for n in NOTICIAS)
    corpo = hero_interno("Notícias", "Notícias e eventos", "Acompanhe o que acontece na Farvalle: palestras, acolhimento, vestibular e a rotina de quem já faz parte da nossa história.",
                         "news-2", "Evento da Farvalle", [("Início", "index"), ("Notícias", None)],
                         btn("Seguir no Instagram", INSTAGRAM, "btn btn-verde", "insta", externo=True), pos="center 35%", acento="da Farvalle.")
    corpo += f'<section class="sec"><div class="wrap"><div class="noticias-grade noticias-lista">{cards}</div></div></section>'
    corpo += cta_faixa()
    return corpo


def noticia_pg(n):
    corpo_txt = "".join(f"<{t}>{e(x)}</{t}>" for t, x in n["corpo"])
    outras = "".join(card_noticia(o) for o in NOTICIAS if o["slug"] != n["slug"])
    return f'''<article class="artigo">
  <div class="wrap artigo-cab">
    {trilha([("Início", "index"), ("Notícias", "noticias"), (n["titulo"], None)])}
    <div class="card-not-meta"><span class="tag">{e(n["categoria"])}</span><time datetime="{n["data"]}">{e(n["data_txt"])}</time></div>
    <h1>{e(n["titulo"])}</h1>
    <p class="lead">{e(n["resumo"])}</p>
  </div>
  <div class="wrap artigo-foto">{foto(n["foto"], "", prioridade=True, pos="center 35%")}</div>
  <div class="wrap artigo-corpo">{corpo_txt}
    <div class="artigo-share"><span>Compartilhar:</span><a class="btn btn-contorno btn-p" href="https://wa.me/?text={quote(n["titulo"] + " — " + canonica("noticias/" + n["slug"]))}" target="_blank" rel="noopener">{I["whats"]}<span>WhatsApp</span></a><a class="btn btn-contorno btn-p" href="{INSTAGRAM}" target="_blank" rel="noopener">{I["insta"]}<span>Instagram</span></a></div>
  </div>
</article>
<section class="sec sec-cinza">
  <div class="wrap">
    <div class="sec-cab-linha">{secao_titulo("Leia também", "Outras notícias")}{btn("Todas as Notícias", url("noticias"), "btn btn-contorno sec-cab-btn")}</div>
    <div class="noticias-grade" data-trilho>{outras}</div>{trilho_nav()}
  </div>
</section>''' + cta_faixa()


def contato_pg():
    corpo = hero_interno("Contato", "Fale com a Farvalle", "Secretaria acadêmica, informações sobre cursos, vestibular e matrícula. Atendimento pelo WhatsApp, e-mail ou presencialmente no campus Valle Shopping.",
                         "news-3", "Atendimento na Farvalle", [("Início", "index"), ("Contato", None)],
                         btn_whats("Falar no WhatsApp", "btn btn-verde") + btn("Inscreva-se", url("inscreva-se"), "btn btn-laranja"), pos="center 30%", acento="estamos pertinho.")
    corpo += f'''<section class="sec">
  <div class="wrap canais" data-trilho>
    <a class="canal" href="{wa()}" target="_blank" rel="noopener">{ic("whats","ic-circ")}<strong>WhatsApp</strong><span>{TELEFONE}</span><em>Resposta rápida em horário comercial</em></a>
    <a class="canal" href="{tel(TELEFONE)}">{ic("phone","ic-circ")}<strong>Telefone</strong><span>{TELEFONE}</span><em>Secretaria acadêmica</em></a>
    <a class="canal" href="mailto:{EMAIL}">{ic("mail","ic-circ")}<strong>E-mail</strong><span>{EMAIL}</span><em>Informações gerais</em></a>
    <a class="canal" href="mailto:{EMAIL_SECRETARIA}">{ic("file","ic-circ")}<strong>Secretaria</strong><span>{EMAIL_SECRETARIA}</span><em>Inscrições, documentos e matrícula</em></a>
    <a class="canal" href="{INSTAGRAM}" target="_blank" rel="noopener">{ic("insta","ic-circ")}<strong>Instagram</strong><span>{INSTA_USER}</span><em>Novidades e bastidores</em></a>
  </div>{trilho_nav()}
</section>
<section class="sec sec-cinza" id="mapa">
  <div class="wrap local-in">
    <div class="local-txt">
      {secao_titulo("Onde estamos", "Campus Valle Shopping", acento="Amargosa, Bahia.")}
      <ul class="campus-lista">
        <li>{ic("pin")}<span>{e(ENDERECO)}<br>{e(CIDADE)}</span></li>
        <li>{ic("clock")}<span>{e(HORARIO)}</span></li>
        <li>{ic("building")}<span>Estacionamento e acesso pelo Valle Shopping</span></li>
      </ul>
      <div class="btns">{btn("Rota no Google Maps", MAPS_ROTA, "btn btn-verde", "map", externo=True)}{btn("Abrir no Waze", WAZE, "btn btn-contorno", "waze", externo=True)}</div>
    </div>
    {mapa_bloco()}
  </div>
</section>
<section class="sec">
  <div class="wrap faq-wrap">
    {secao_titulo("Antes de ligar", "Perguntas rápidas")}
    {faq_html(FAQ_SELETIVO[:4])}
  </div>
</section>'''
    return corpo


def privacidade_pg():
    return f'''<section class="sec texto-pg">
  <div class="wrap texto-in">
    {trilha([("Início", "index"), ("Política de Privacidade", None)])}
    <h1>Política de Privacidade</h1>
    <p class="lead">Como a {NOME_LONGO} trata os dados pessoais informados neste site, em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).</p>
    <h2>Dados coletados</h2>
    <p>No formulário de inscrição coletamos nome, telefone/WhatsApp, e-mail, cidade, forma de ingresso, curso desejado, como conheceu a instituição e, no Vestibular Online, o texto da redação. Esses dados são usados exclusivamente para o processo seletivo e o contato da secretaria acadêmica.</p>
    <h2>Finalidade e compartilhamento</h2>
    <p>As inscrições são encaminhadas à secretaria acadêmica ({EMAIL_SECRETARIA}). Não vendemos nem compartilhamos dados pessoais com terceiros para fins comerciais. Serviços de envio de e-mail e hospedagem atuam como operadores, apenas para viabilizar o funcionamento do site.</p>
    <h2>Cookies e navegação</h2>
    <p>Este site não utiliza cookies de rastreamento publicitário. Podem ser usados cookies estritamente necessários ao funcionamento das páginas.</p>
    <h2>Seus direitos</h2>
    <p>Você pode solicitar a confirmação, o acesso, a correção ou a exclusão dos seus dados a qualquer momento pelo e-mail {EMAIL} ou pelo WhatsApp {TELEFONE}.</p>
    <h2>Atualizações</h2>
    <p>Esta política pode ser atualizada. A versão vigente é sempre a publicada nesta página.</p>
    <div class="btns">{btn("Voltar ao início", url("index"), "btn btn-verde")}</div>
  </div>
</section>'''


def pagina_404():
    return f'''<section class="sec pg-404">
  <div class="wrap pg-404-in">
    <span class="pg-404-n">404</span>
    <h1>Página não encontrada</h1>
    <p class="lead">O endereço que você acessou não existe ou foi movido. Veja os caminhos mais procurados:</p>
    <div class="btns">{btn("Início", url("index"), "btn btn-verde")}{btn("Cursos", url("cursos"), "btn btn-contorno")}{btn("Inscreva-se", url("inscreva-se"), "btn btn-laranja")}{btn("Contato", url("contato"), "btn btn-contorno")}</div>
  </div>
</section>'''


# ───────────── Tabela de páginas ─────────────
PAGINAS = {
    "index": (f"{NOME_LONGO} · Graduação presencial em Amargosa, BA", "Faculdade presencial em Amargosa/BA com Enfermagem, Fisioterapia e Pedagogia. Vestibular online, nota do ENEM, transferência e segunda graduação. Inscreva-se.", home),
    "a-farvalle": (f"A Farvalle · Faculdade Regional do Valle em Amargosa", "Conheça a Faculdade Regional do Valle: história, valores, campus no Valle Shopping e cadastro no e-MEC.", a_farvalle),
    "cursos": (f"Cursos de graduação presencial · {NOME}", "Enfermagem, Fisioterapia e Pedagogia: graduações presenciais e noturnas em Amargosa, BA. Compare duração, grau e turno e inscreva-se.", cursos_pg),
    "processo-seletivo": (f"{EDICAO} · Formas de ingresso · {NOME}", "Vestibular online com redação, nota do ENEM, transferência externa e segunda graduação. Veja o passo a passo e inscreva-se na Farvalle.", processo_seletivo_pg),
    "inscreva-se": (f"Inscreva-se no {EDICAO} · {NOME}", "Inscrição online para Enfermagem, Fisioterapia e Pedagogia na Faculdade Farvalle, em Amargosa/BA. Redação no próprio formulário.", inscreva_se_pg),
    "publicacoes-institucionais": (f"Vida Acadêmica · Calendário e regulamentos · {NOME}", "Calendário acadêmico, regulamentos institucionais, editais e cadastro e-MEC da Faculdade Regional do Valle.", publicacoes_pg),
    "noticias": (f"Notícias e eventos · {NOME}", "Palestras, acolhimento, vestibular e a rotina da Faculdade Farvalle em Amargosa, BA.", noticias_pg),
    "contato": (f"Contato · {NOME} · Amargosa, BA", f"WhatsApp {TELEFONE}, e-mail e endereço da Faculdade Farvalle no Valle Shopping, Amargosa/BA. Mapa interativo e rota.", contato_pg),
    "privacidade": (f"Política de Privacidade · {NOME}", "Como a Faculdade Farvalle trata os dados pessoais informados no site, conforme a LGPD.", privacidade_pg),
    "404": (f"Página não encontrada · {NOME}", "A página que você procura não existe.", pagina_404),
}
for c in CURSOS:
    PAGINAS["cursos/" + c["slug"]] = (f"{c['nome']} ({c['grau']}) presencial em Amargosa · {NOME}", f"Curso de {c['nome']} na Farvalle: {c['duracao']}, {c['modalidade'].lower()}, turno {c['turno'].lower()}. {c['resumo']}", (lambda cc: (lambda: curso_pg(cc)))(c))
for n in NOTICIAS:
    PAGINAS["noticias/" + n["slug"]] = (f"{n['titulo']} · {NOME}", n["resumo"], (lambda nn: (lambda: noticia_pg(nn)))(n))


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / "assets", DIST / "assets")
    for slug, (titulo, desc, fn) in PAGINAS.items():
        out = pagina(slug, titulo, desc, fn(), mapa=(slug == "contato"))
        if LIMPO:
            out = re.sub(r'((?:src|href|srcset)=")assets/', r'\1' + BASE + '/assets/', out)
        elif "/" in slug:
            pass
        if LIMPO and slug not in ("index", "404"):
            (DIST / slug).mkdir(parents=True, exist_ok=True)
            (DIST / slug / "index.html").write_text(out, encoding="utf-8")
        else:
            (DIST / f"{slug.replace('/', '-')}.html").write_text(out, encoding="utf-8")
    if INDEXNOW_KEY:
        (DIST / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    hoje = datetime.date.today().isoformat()
    prioridade = {"index": "1.0", "cursos": "0.9", "inscreva-se": "0.9", "processo-seletivo": "0.9", "privacidade": "0.3"}
    urls = [(canonica(s), prioridade.get(s, "0.9" if s.startswith("cursos/") else "0.7")) for s in PAGINAS if s != "404"]
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "".join(f"  <url><loc>{u}</loc><lastmod>{hoje}</lastmod><changefreq>monthly</changefreq><priority>{p}</priority></url>\n" for u, p in urls)
                                      + "</urlset>\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /404.html\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"ok → {DIST} ({len(PAGINAS)} páginas, links {'limpos' if LIMPO else '.html'}, sitemap com {len(urls)} URLs)")


if __name__ == "__main__":
    main()
