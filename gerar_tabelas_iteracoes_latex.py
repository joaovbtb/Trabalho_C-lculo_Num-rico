"""Gera as tabelas completas de iteração incluídas no fonte LaTeX."""

from __future__ import annotations

from pathlib import Path

import codigo_q1 as q1
import codigo_q2 as q2
import codigo_q3 as q3


OUTPUT = Path(__file__).resolve().parent / "tabelas_iteracoes.tex"


def longtable(header: list[str], rows: list[list[str]], caption: str, label: str) -> str:
    """Monta uma tabela longa compatível com LaTeX.

    Args:
        header: Cabeçalhos das colunas.
        rows: Linhas de valores já formatados.
        caption: Legenda da tabela.
        label: Identificador de referência no documento.

    Returns:
        Código LaTeX para uma tabela longa.
    """

    columns = "r" * len(header)
    line_break = r" \\"
    parts = [rf"\begin{{longtable}}{{{columns}}}", rf"\caption{{{caption}}}\label{{{label}}}{line_break}", r"\toprule", " & ".join(header) + line_break, r"\midrule", r"\endfirsthead", r"\toprule", " & ".join(header) + line_break, r"\midrule", r"\endhead"]
    parts.extend([" & ".join(row) + line_break for row in rows])
    parts.extend([r"\bottomrule", r"\end{longtable}", ""])
    return "\n".join(parts)


def question_one_tables() -> list[str]:
    """Gera as quatro tabelas dos métodos de raiz da Questão 1.

    Returns:
        Blocos LaTeX com os históricos completos.
    """

    methods = {
        "Bisseção": q1.bisection(q1.f, 0.5, 1.5),
        "Falsa posição": q1.false_position(q1.f, 0.5, 1.5),
        "Newton": q1.newton(q1.f, q1.df, 0.8),
        "Secante": q1.secant(q1.f, 0.7, 0.8),
    }
    tables = [r"\subsection*{Questão 1}"]
    for index, (name, history) in enumerate(methods.items(), start=1):
        rows = [[str(item.k), f"{item.theta:.9f}", f"{item.residual:.9e}", f"{abs(item.residual):.9e}"] for item in history]
        tables.append(longtable(["$k$", "$\\theta_k$ [rad]", "$f(\\theta_k)$", "$|f(\\theta_k)|$"], rows, f"Histórico completo do método da {name} na Questão 1.", f"tab:iter-q1-{index}"))
    return tables


def question_two_table() -> str:
    """Gera a tabela das etapas da eliminação de Gauss.

    Returns:
        Bloco LaTeX com o resumo de todas as etapas.
    """

    matrix, vector = q2.system()
    _, steps = q2.gaussian_elimination_pivoting(matrix, vector)
    rows = []
    for index, step in enumerate(steps, start=1):
        multipliers = ", ".join(f"{value:.0f}" for value in step.multipliers if abs(value) > 1e-12) or "nenhum"
        rows.append([str(index), str(step.column), str(step.pivot_row), "sim" if step.swapped else "não", multipliers])
    return "\n".join([r"\subsection*{Questão 2}", longtable(["Etapa", "Coluna", "Linha de pivô", "Troca", "Multiplicadores não nulos"], rows, "Resumo de todas as etapas de Gauss com pivotamento na Questão 2.", "tab:iter-q2")])


def question_three_tables() -> list[str]:
    """Gera as tabelas dos dois históricos de Newton-Raphson.

    Returns:
        Blocos LaTeX com os históricos completos.
    """

    cases = {
        "Caso 1": q3.np.array([1.0, 12.0, 10.0, 0.05]),
        "Caso 2": q3.np.array([15.0, 25.0, 10.0, 1.0]),
    }
    tables = [r"\subsection*{Questão 3}"]
    for index, (name, initial) in enumerate(cases.items(), start=1):
        history, status = q3.newton_raphson(initial)
        rows = [[str(item.k), f"{item.x[0]:.6f}", f"{item.x[1]:.6f}", f"{item.x[2]:.6f}", f"{item.x[3]:.6f}", f"{item.residual_norm:.6e}"] for item in history]
        tables.append(longtable(["$k$", "$\\Delta p$ [MPa]", "$T_{in}$ [°C]", "$T_{out}$ [°C]", "$\\mu_{med}$ [Pa.s]", "$\\lVert F(x_k)\\rVert_2$"], rows, f"Histórico completo do {name} ({status}) na Questão 3.", f"tab:iter-q3-{index}"))
    return tables


def main() -> None:
    """Escreve as tabelas completas no arquivo auxiliar LaTeX."""

    content = "\n".join(question_one_tables() + [question_two_table()] + question_three_tables())
    OUTPUT.write_text(content, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
