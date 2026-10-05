"""Gera o PDF do relatório quando um compilador LaTeX não está disponível."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "pdf" / "relatorio_calculo_numerico_joao_victor.pdf"


def register_fonts() -> None:
    """Registra fontes TrueType com suporte aos caracteres do relatório."""

    pdfmetrics.registerFont(TTFont("TimesNewRoman", r"C:\Windows\Fonts\times.ttf"))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", r"C:\Windows\Fonts\timesbd.ttf"))
    pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))


def build_styles() -> dict[str, ParagraphStyle]:
    """Constrói os estilos tipográficos usados no documento.

    Returns:
        Dicionário de estilos para texto, títulos, tabelas e código.
    """

    sample = getSampleStyleSheet()
    return {
        "body": ParagraphStyle("Body", parent=sample["BodyText"], fontName="TimesNewRoman", fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=8),
        "title": ParagraphStyle("Title", parent=sample["Title"], fontName="TimesNewRoman-Bold", fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=14),
        "cover": ParagraphStyle("Cover", parent=sample["BodyText"], fontName="TimesNewRoman", fontSize=13, leading=20, alignment=TA_CENTER),
        "section": ParagraphStyle("Section", parent=sample["Heading1"], fontName="TimesNewRoman-Bold", fontSize=14, leading=18, spaceBefore=12, spaceAfter=10),
        "subsection": ParagraphStyle("Subsection", parent=sample["Heading2"], fontName="TimesNewRoman-Bold", fontSize=12, leading=15, spaceBefore=9, spaceAfter=7),
        "caption": ParagraphStyle("Caption", parent=sample["BodyText"], fontName="TimesNewRoman", fontSize=9, leading=11, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10),
        "table": ParagraphStyle("Table", parent=sample["BodyText"], fontName="TimesNewRoman", fontSize=8.5, leading=10),
        "code": ParagraphStyle("Code", parent=sample["BodyText"], fontName="Consolas", fontSize=5.1, leading=5.9, wordWrap="CJK"),
    }


def paragraph(text: str, styles: dict[str, ParagraphStyle], style: str = "body") -> Paragraph:
    """Cria um parágrafo usando o estilo solicitado.

    Args:
        text: Conteúdo com marcação XML simples do ReportLab.
        styles: Dicionário de estilos do documento.
        style: Chave do estilo desejado.

    Returns:
        Parágrafo pronto para inserção no fluxo do PDF.
    """

    return Paragraph(text, styles[style])


def heading(text: str, styles: dict[str, ParagraphStyle], level: str = "section") -> Paragraph:
    """Cria um cabeçalho numericamente simples.

    Args:
        text: Título da seção ou subseção.
        styles: Dicionário de estilos do documento.
        level: Estilo a usar, section ou subsection.

    Returns:
        Cabeçalho formatado.
    """

    return paragraph(text, styles, level)


def add_figure(story: list[object], image_name: str, caption: str, styles: dict[str, ParagraphStyle], width_cm: float = 15.0) -> None:
    """Adiciona uma figura centralizada com legenda.

    Args:
        story: Lista de elementos do documento.
        image_name: Caminho relativo da imagem na pasta figures.
        caption: Legenda acadêmica da figura.
        styles: Dicionário de estilos do documento.
        width_cm: Largura de apresentação em centímetros.
    """

    source = ROOT / "figures" / image_name
    image = Image(str(source))
    ratio = image.imageHeight / image.imageWidth
    image.drawWidth = width_cm * cm
    image.drawHeight = width_cm * cm * ratio
    image.hAlign = "CENTER"
    story.extend([image, paragraph(caption, styles, "caption")])


def make_table(data: list[list[str]], widths: list[float], caption: str, styles: dict[str, ParagraphStyle]) -> list[object]:
    """Monta uma tabela com cabeçalho e legenda.

    Args:
        data: Células da tabela, incluindo a primeira linha de cabeçalho.
        widths: Larguras das colunas em centímetros.
        caption: Legenda colocada acima da tabela.
        styles: Dicionário de estilos do documento.

    Returns:
        Elementos de legenda, tabela e espaçamento.
    """

    rendered = [[paragraph(escape(cell), styles, "table") for cell in row] for row in data]
    table = Table(rendered, colWidths=[width * cm for width in widths], repeatRows=1, hAlign="CENTER")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "TimesNewRoman-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6E6E6")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#808080")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [paragraph(caption, styles, "caption"), table, Spacer(1, 0.28 * cm)]


def make_matrix(rows: list[list[str]], label: str, styles: dict[str, ParagraphStyle]) -> list[object]:
    """Monta uma matriz aumentada compacta para as etapas manuais.

    Args:
        rows: Linhas da matriz aumentada, com a última coluna após a barra.
        label: Identificação da matriz apresentada.
        styles: Dicionário de estilos do documento.

    Returns:
        Elementos com rótulo e matriz formatada.
    """

    rendered = [[paragraph(escape(cell), styles, "table") for cell in row] for row in rows]
    table = Table(rendered, colWidths=[1.25 * cm] * 7 + [1.45 * cm], hAlign="CENTER")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Consolas"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("GRID", (6, 0), (6, -1), 0.9, colors.black),
        ("LINEBEFORE", (7, 0), (7, -1), 0.9, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return [KeepTogether([paragraph(label, styles), table, Spacer(1, 0.22 * cm)])]


def add_code_appendix(story: list[object], file_name: str, title: str, styles: dict[str, ParagraphStyle]) -> None:
    """Insere um código-fonte em um apêndice paginado.

    Args:
        story: Lista de elementos do documento.
        file_name: Arquivo Python a incorporar.
        title: Título do apêndice.
        styles: Dicionário de estilos do documento.
    """

    story.append(PageBreak())
    story.append(heading(title, styles))
    lines = (ROOT / file_name).read_text(encoding="utf-8").splitlines()
    for line in lines:
        shown = escape(line).replace(" ", "&nbsp;") or "&nbsp;"
        story.append(paragraph(shown, styles, "code"))


def add_iteration_tables(story: list[object], styles: dict[str, ParagraphStyle]) -> None:
    """Inclui históricos completos das execuções numéricas no relatório.

    Args:
        story: Lista de elementos do documento.
        styles: Dicionário de estilos do documento.
    """

    import codigo_q1 as q1
    import codigo_q2 as q2
    import codigo_q3 as q3

    story.append(PageBreak())
    story.append(heading("Apêndice D - Tabelas completas de iteração", styles))
    story.append(paragraph("As tabelas deste apêndice registram todos os iterandos usados para produzir as figuras e os resultados finais. Os valores são gerados diretamente pelas rotinas apresentadas nos apêndices seguintes.", styles))
    methods = {
        "Bisseção": q1.bisection(q1.f, 0.5, 1.5),
        "Falsa posição": q1.false_position(q1.f, 0.5, 1.5),
        "Newton": q1.newton(q1.f, q1.df, 0.8),
        "Secante": q1.secant(q1.f, 0.7, 0.8),
    }
    for name, history in methods.items():
        data = [["k", "theta_k [rad]", "f(theta_k)", "|f(theta_k)|"]]
        data.extend([[str(item.k), f"{item.theta:.9f}", f"{item.residual:.9e}", f"{abs(item.residual):.9e}"] for item in history])
        story.extend(make_table(data, [1.2, 4.0, 4.0, 4.0], f"Tabela D.{list(methods).index(name) + 1} - Histórico completo do método da {name} na Questão 1.", styles))
    story.append(PageBreak())
    story.append(heading("D.5 Questão 2 - etapas da eliminação", styles, "subsection"))
    matrix, vector = q2.system()
    _, steps = q2.gaussian_elimination_pivoting(matrix, vector)
    elimination_data = [["Etapa", "Coluna", "Linha de pivô", "Troca", "Multiplicadores não nulos"]]
    for index, step in enumerate(steps, start=1):
        nonzero = ", ".join(f"m={value:.0f}" for value in step.multipliers if abs(value) > 1e-12) or "nenhum"
        elimination_data.append([str(index), str(step.column), str(step.pivot_row), "sim" if step.swapped else "não", nonzero])
    story.extend(make_table(elimination_data, [1.6, 1.7, 2.4, 1.5, 7.5], "Tabela D.5 - Resumo de todas as etapas de Gauss com pivotamento na Questão 2.", styles))
    story.append(heading("D.6 Questão 3 - histórico do Newton-Raphson", styles, "subsection"))
    cases = {
        "Caso 1": q3.np.array([1.0, 12.0, 10.0, 0.05]),
        "Caso 2": q3.np.array([15.0, 25.0, 10.0, 1.0]),
    }
    for case_name, initial in cases.items():
        history, status = q3.newton_raphson(initial)
        data = [["k", "Delta p [MPa]", "Tin [°C]", "Tout [°C]", "mu_med [Pa.s]", "||F(x_k)||_2"]]
        data.extend([[str(item.k), f"{item.x[0]:.6f}", f"{item.x[1]:.6f}", f"{item.x[2]:.6f}", f"{item.x[3]:.6f}", f"{item.residual_norm:.6e}"] for item in history])
        story.extend(make_table(data, [0.9, 2.5, 2.3, 2.3, 2.8, 3.6], f"Tabela D.{6 if case_name == 'Caso 1' else 7} - Histórico completo do {case_name} ({status}) na Questão 3.", styles))


def add_page_number(canvas: object, document: object) -> None:
    """Desenha o número de página no rodapé.

    Args:
        canvas: Canvas de saída fornecido pelo ReportLab.
        document: Documento em compilação.
    """

    if document.page > 1:
        canvas.setFont("TimesNewRoman", 9)
        canvas.drawCentredString(A4[0] / 2.0, 1.25 * cm, str(document.page - 1))


def build_story(styles: dict[str, ParagraphStyle]) -> list[object]:
    """Compõe o conteúdo completo do relatório.

    Args:
        styles: Dicionário de estilos do documento.

    Returns:
        Lista ordenada de elementos para o PDF.
    """

    story: list[object] = []
    crest = Image(str(ROOT / "figures" / "brasao_ufsc_oficial.png"), width=5.4 * cm, height=5.32 * cm)
    crest.hAlign = "CENTER"
    story.extend([
        Spacer(1, 1.0 * cm), crest, Spacer(1, 0.8 * cm),
        paragraph("UNIVERSIDADE FEDERAL DE SANTA CATARINA", styles, "cover"),
        paragraph("Departamento de Automação e Sistemas", styles, "cover"),
        Spacer(1, 1.9 * cm),
        paragraph("DAS-5103 - Cálculo Numérico para Controle e Automação", styles, "cover"),
        Spacer(1, 1.0 * cm),
        paragraph("<b>Trabalho Prático 1</b>", styles, "title"),
        Spacer(1, 2.1 * cm),
        paragraph("João Victor Barbosa Teixeira Bouças", styles, "cover"),
        paragraph("Matrícula 25103276", styles, "cover"),
        Spacer(1, 2.3 * cm),
        paragraph("Florianópolis", styles, "cover"),
        paragraph("2026", styles, "cover"),
        PageBreak(),
        heading("1. Introdução", styles),
        paragraph("Este relatório trata de três classes de problemas numéricos: a determinação de uma raiz escalar, a solução de um sistema linear e a solução de um sistema não linear. Em cada caso foram implementados em Python os algoritmos especificados no enunciado, sem recorrer a rotinas prontas de busca de raízes ou de solução de sistemas como procedimento principal.", styles),
        paragraph("Além dos valores finais, foram examinados os resíduos, o número de iterações e as trajetórias dos iterandos. Os critérios de parada não foram escolhidos livremente: para a Questão 1, adotou-se |f(theta_k)| &lt; 10^-5; para a Questão 3, ||F(x_k)||_2 &lt;= 10^-5; em ambos os casos o limite foi de 100 iterações.", styles),
        heading("2. Questão 1 - Equação não linear", styles),
        heading("2.1 Formulação e métodos", styles, "subsection"),
        paragraph("Foi resolvida f(theta) = (100²/9,8)[sin(theta) + 0,5 sin(2 theta)] - 1000 = 0, no domínio 0 &lt;= theta &lt;= pi/2. As avaliações iniciais foram f(0,5) = -81,468335706 e f(1,5) = 89,852031259. Assim, o intervalo dos métodos de quebra possui mudança de sinal e está no domínio de interesse.", styles),
        paragraph("Aplicaram-se bisseção, falsa posição, Newton e secante com os pontos prescritos. Bisseção preserva o intervalo de sinais opostos e reduz sua largura pela metade. Falsa posição conserva essa propriedade usando a interseção da secante dos extremos. Newton usou a derivada analítica f'(theta) = (100²/9,8)[cos(theta) + cos(2 theta)], enquanto a secante estimou a inclinação com dois iterandos anteriores.", styles),
    ])
    add_figure(story, "q1_theta_iteracoes.png", "Figura 1 - Trajetória de theta_k para os quatro métodos da Questão 1.", styles)
    add_figure(story, "q1_residuo_iteracoes.png", "Figura 2 - Módulo do resíduo por iteração na Questão 1.", styles)
    story.append(heading("2.2 Resultados e análise", styles, "subsection"))
    story.extend(make_table([
        ["Método", "theta [rad]", "theta [graus]", "Iterações", "|f(theta)|", "Situação"],
        ["Bisseção", "0,559037104", "32,030466665", "26", "3,549 x 10^-6", "Convergiu"],
        ["Falsa posição", "0,559037102", "32,030466544", "8", "7,821 x 10^-7", "Convergiu"],
        ["Newton", "0,559037097", "32,030466245", "4", "6,058 x 10^-6", "Convergiu"],
        ["Secante", "0,559037108", "32,030466902", "5", "8,971 x 10^-6", "Convergiu"],
    ], [2.6, 2.25, 2.5, 1.65, 2.25, 2.0], "Tabela 1 - Comparação final dos métodos para a Questão 1.", styles))
    story.extend([
        paragraph("As quatro aproximações pertencem ao domínio e concordam até as casas apresentadas. A substituição direta em f produz os resíduos da Tabela 1; todas satisfazem o critério determinado no enunciado. A bisseção foi a mais lenta, mas preservou o intervalo válido nas 26 iterações.", styles),
        paragraph("Na falsa posição, não ocorreu o risco de uma extremidade permanecer praticamente fixa: a tolerância foi atingida em oito passos. Newton foi o mais rápido, com quatro passos a partir de theta_0 = 0,8; a derivada não se aproximou de zero na trajetória. A secante convergiu em cinco passos e seu denominador não se aproximou de zero. Os dois últimos foram rápidos porque os pontos prescritos estavam em uma região favorável, sem a proteção global dos métodos de quebra.", styles),
        heading("2.3 Conclusão da questão", styles, "subsection"),
        paragraph("O ângulo de lançamento é aproximadamente 0,5590371 rad, ou 32,03047 graus. Todos os métodos convergiram; a diferença está no custo iterativo: 26 passos para a bisseção, 8 para a falsa posição, 4 para Newton e 5 para a secante. Neste problema, Newton foi o mais rápido e a bisseção forneceu a trajetória mais previsível.", styles),
        heading("3. Questão 2 - Sistema de equações lineares", styles),
        heading("3.1 Sistema e leitura do grafo", styles, "subsection"),
        paragraph("O sistema fornecido no enunciado foi escrito na ordem (x1,...,x7)^T. A figura da malha aérea contém arcos curvos que se cruzam e rótulos próximos de outros trechos. A leitura adotada não foi baseada na geometria ou no cruzamento visual das linhas. Cada arco foi identificado pelo rótulo x_i, e seu sentido foi fixado pela tabela e pelas equações do enunciado, que são a especificação formal do problema.", styles),
    ])
    story.extend(make_table([
        ["Variável", "Rota lida", "Critério de leitura"],
        ["x1", "IGU -> GRU", "Rótulo e tabela do enunciado"],
        ["x2", "GRU -> Outros", "Rótulo e tabela do enunciado"],
        ["x3", "Outros -> GIG", "Rótulo e tabela do enunciado"],
        ["x4", "GIG -> POA", "Rótulo e tabela do enunciado"],
        ["x5", "POA -> CGH", "Rótulo e tabela do enunciado"],
        ["x6", "SDU -> CGH", "Rótulo e tabela do enunciado"],
        ["x7", "CGH -> IGU", "Rótulo e tabela do enunciado"],
    ], [2.1, 4.5, 7.0], "Quadro 1 - Transcrição orientada usada para interpretar a figura da Questão 2.", styles))
    story.extend([
        paragraph("Assim, os cruzamentos no desenho são sobreposições de arcos no plano, e não conexões entre aeroportos. A equação -x1 + 2x7 = 0 foi tratada como a relação adicional do enunciado, isto é, x1 = 2x7; ela não foi deduzida de uma leitura espacial da figura.", styles),
        heading("3.2 Eliminação de Gauss com pivotamento", styles, "subsection"),
        paragraph("Foi implementada eliminação de Gauss com pivotamento parcial e retrosubstituição. Em cada coluna, seleciona-se a maior entrada em módulo dentre as linhas disponíveis. Isso evita divisão por pivôs nulos e reduz a exposição a arredondamentos quando há pivôs pequenos. Nas três primeiras colunas houve empate de módulo igual a um; a primeira linha candidata foi mantida, logo não houve troca de linhas.", styles),
        paragraph("A matriz aumentada inicial é apresentada abaixo. Em cada etapa, a coluna de pivô, a linha escolhida, o multiplicador e a operação elementar são mostrados antes da matriz resultante.", styles),
    ])
    story.extend(make_matrix([
        ["-1", "0", "0", "0", "0", "0", "2", "0"], ["1", "-1", "0", "0", "0", "0", "0", "-130"], ["0", "1", "-1", "0", "0", "0", "0", "102"], ["0", "0", "1", "-1", "0", "0", "0", "22"], ["0", "0", "0", "1", "-1", "0", "0", "-1"], ["0", "0", "0", "0", "0", "1", "0", "29"], ["0", "0", "0", "0", "1", "1", "-1", "38"],
    ], "Matriz aumentada inicial [A | b].", styles))
    story.extend([
        paragraph("Etapa 1. Coluna de pivô: 1. A linha 1 foi escolhida, com a11 = -1; ela empata em módulo com a linha 2, portanto não houve troca. O único multiplicador não nulo é m21 = 1/(-1) = -1 e a operação é L2 <- L2 - m21 L1 = L2 + L1.", styles),
    ])
    story.extend(make_matrix([
        ["-1", "0", "0", "0", "0", "0", "2", "0"], ["0", "-1", "0", "0", "0", "0", "2", "-130"], ["0", "1", "-1", "0", "0", "0", "0", "102"], ["0", "0", "1", "-1", "0", "0", "0", "22"], ["0", "0", "0", "1", "-1", "0", "0", "-1"], ["0", "0", "0", "0", "0", "1", "0", "29"], ["0", "0", "0", "0", "1", "1", "-1", "38"],
    ], "Matriz aumentada após a Etapa 1.", styles))
    story.extend([
        paragraph("Etapa 2. Coluna de pivô: 2. A linha 2 foi escolhida, com a22 = -1; ela empata em módulo com a linha 3, sem troca. O multiplicador não nulo é m32 = 1/(-1) = -1 e a operação é L3 <- L3 + L2.", styles),
    ])
    story.extend(make_matrix([
        ["-1", "0", "0", "0", "0", "0", "2", "0"], ["0", "-1", "0", "0", "0", "0", "2", "-130"], ["0", "0", "-1", "0", "0", "0", "2", "-28"], ["0", "0", "1", "-1", "0", "0", "0", "22"], ["0", "0", "0", "1", "-1", "0", "0", "-1"], ["0", "0", "0", "0", "0", "1", "0", "29"], ["0", "0", "0", "0", "1", "1", "-1", "38"],
    ], "Matriz aumentada após a Etapa 2.", styles))
    story.extend([
        paragraph("Etapa 3. Coluna de pivô: 3. A linha 3 foi escolhida, com a33 = -1; ela empata em módulo com a linha 4, sem troca. O multiplicador não nulo é m43 = 1/(-1) = -1 e a operação é L4 <- L4 + L3.", styles),
    ])
    story.extend(make_matrix([
        ["-1", "0", "0", "0", "0", "0", "2", "0"], ["0", "-1", "0", "0", "0", "0", "2", "-130"], ["0", "0", "-1", "0", "0", "0", "2", "-28"], ["0", "0", "0", "-1", "0", "0", "2", "-6"], ["0", "0", "0", "1", "-1", "0", "0", "-1"], ["0", "0", "0", "0", "0", "1", "0", "29"], ["0", "0", "0", "0", "1", "1", "-1", "38"],
    ], "Matriz aumentada após a Etapa 3. As etapas restantes e a retrosubstituição geram x = (4, 134, 32, 10, 11, 29, 2)^T.", styles))
    story.append(PageBreak())
    story.extend(make_table([
        ["Variável", "Voo", "Voos por dia"],
        ["x1", "IGU -> GRU", "4"], ["x2", "GRU -> Outros", "134"], ["x3", "Outros -> GIG", "32"],
        ["x4", "GIG -> POA", "10"], ["x5", "POA -> CGH", "11"], ["x6", "SDU -> CGH", "29"], ["x7", "CGH -> IGU", "2"],
    ], [2.5, 7.0, 3.5], "Tabela 2 - Quantidade de voos diários nas rotas desconhecidas.", styles))
    add_figure(story, "q2_voos_por_dia.png", "Figura 3 - Fluxos desconhecidos obtidos para a malha aérea.", styles, 14.0)
    story.extend([
        paragraph("A substituição independente forneceu Ax-b = (0,0,0,0,0,0,0)^T e ||Ax-b||_2 = 0 na aritmética de ponto flutuante usada. A relação adicional também é satisfeita: x1 = 4 = 2 x 2 = 2x7. Como diagnóstico, kappa_2(A) = 25,433, valor moderado para esta matriz.", styles),
        heading("3.3 Conclusão da questão", styles, "subsection"),
        paragraph("O sistema é consistente e a solução satisfaz todas as equações de conservação e a relação adicional. O residual nulo confirma a substituição numérica. Embora não tenha havido permuta nas primeiras etapas, o pivotamento continua sendo necessário: em outra ordenação ou com pivôs pequenos, ele reduz o risco de uma divisão numericamente insegura.", styles),
        heading("4. Questão 3 - Sistema de equações não lineares", styles),
        heading("4.1 Formulação e implementação", styles, "subsection"),
        paragraph("O vetor foi mantido na ordem x = [Delta p, Tin, Tout, mu_med]^T. A cada passo de Newton-Raphson, resolveu-se J(x_k) Delta x_k = -F(x_k) por eliminação de Gauss com pivotamento parcial e atualizou-se x_(k+1) = x_k + Delta x_k. A inversa de J não foi formada explicitamente.", styles),
        paragraph("Foram investigados os riscos de Jacobiana singular, crescimento do resíduo, iterados não finitos e sensibilidade ao chute inicial. Não se aplicou amortecimento, retrocesso ou troca de método. Os dois casos convergiram antes do limite de 100 passos.", styles),
    ])
    add_figure(story, "q3_residuo_iteracoes.png", "Figura 4 - Norma do resíduo ao longo das iterações de Newton-Raphson.", styles)
    add_figure(story, "q3_caso_1_temperaturas.png", "Figura 5 - Trajetória das temperaturas para o Caso 1.", styles)
    add_figure(story, "q3_caso_1_pressao_viscosidade.png", "Figura 6 - Trajetória de Delta p e mu_med para o Caso 1.", styles)
    add_figure(story, "q3_caso_2_temperaturas.png", "Figura 7 - Trajetória das temperaturas para o Caso 2.", styles)
    add_figure(story, "q3_caso_2_pressao_viscosidade.png", "Figura 8 - Trajetória de Delta p e mu_med para o Caso 2.", styles)
    story.extend(make_table([
        ["Chute", "Delta p [MPa]", "Tin [°C]", "Tout [°C]", "mu_med [Pa.s]", "Iterações", "Situação"],
        ["Caso 1", "6,423854", "50,417201", "37,168916", "13,787461", "9", "Convergiu"],
        ["Caso 2", "6,423856", "50,417197", "37,168913", "13,787465", "8", "Convergiu"],
    ], [1.65, 2.4, 1.85, 1.85, 2.3, 1.7, 2.0], "Tabela 3 - Resultado de Newton-Raphson para os dois chutes prescritos.", styles))
    story.extend([
        paragraph("No Caso 1, a norma inicial foi 9,772 x 10^5 e decresceu para 5,372 x 10^-8 em nove atualizações. No Caso 2, a norma inicial foi 1,457 x 10^7 e atingiu 1,038 x 10^-6 em oito atualizações. As duas normas atendem à tolerância. O número de condição 2 da Jacobiana no final ficou próximo de 7,49 x 10^6. Esse diagnóstico é elevado pela diferença de escala entre as coordenadas e as equações; ele não substituiu o critério de parada. Os resíduos continuaram decrescendo e não houve Jacobiana singular, oscilação ou iterado não finito.", styles),
        heading("4.2 Análise física e conclusão da questão", styles, "subsection"),
        paragraph("Os dois chutes convergiram para a mesma solução dentro da tolerância. Tin aproximadamente 50,42 °C é maior que Tout aproximadamente 37,17 °C, coerente com a perda térmica ao longo do duto para o ambiente a 4 °C. A relação exponencial produz mu_med aproximadamente 13,79 Pa.s nessa faixa e resulta em Delta p aproximadamente 6,424 MPa. O balanço econômico e as outras equações são satisfeitos pelos resíduos finais, sendo a solução compatível com o custo diário ótimo de US$ 6100 estabelecido no problema.", styles),
        heading("5. Considerações finais", styles),
        paragraph("Na equação escalar, os métodos de quebra foram previsíveis por preservarem um intervalo válido, enquanto Newton e secante foram mais rápidos para os pontos iniciais fornecidos. No sistema linear, a eliminação de Gauss com pivotamento produziu uma solução com residual nulo e tornou explícitas as operações de redução. No sistema não linear, Newton-Raphson convergiu a partir dos dois chutes sem amortecimento. Em todos os casos, o residual exigido pelo enunciado foi o critério principal de aceitação.", styles),
        heading("Referências", styles),
        paragraph("COSTA, Lucas Kuhnen; CAMPONOGARA, Eduardo. <i>Trabalho Prático 1</i>. DAS-5103 - Cálculo Numérico para Controle e Automação, UFSC, setembro de 2026.", styles),
        paragraph("CAMPONOGARA, Eduardo; CASTELAN NETO, Eugênio de Bona. <i>Cálculo Numérico para Controle e Automação</i>. UFSC, versão preliminar, agosto de 2008.", styles),
    ])
    add_iteration_tables(story, styles)
    add_code_appendix(story, "codigo_q1.py", "Apêndice A - Código da Questão 1", styles)
    add_code_appendix(story, "codigo_q2.py", "Apêndice B - Código da Questão 2", styles)
    add_code_appendix(story, "codigo_q3.py", "Apêndice C - Código da Questão 3", styles)
    return story


def main() -> None:
    """Gera o PDF final do relatório em output/pdf."""

    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=2.7 * cm, rightMargin=2.2 * cm, topMargin=2.3 * cm, bottomMargin=2.2 * cm, title="Trabalho Prático 1 - Cálculo Numérico", author="João Victor Barbosa Teixeira Bouças")
    document.build(build_story(build_styles()), onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(OUTPUT)


if __name__ == "__main__":
    main()
