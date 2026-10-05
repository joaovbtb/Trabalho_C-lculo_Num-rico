"""Resolve o sistema de conservação de voos por Gauss com pivotamento."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class EliminationStep:
    """Registra uma etapa da eliminação de Gauss.

    Args:
        column: Coluna do pivô, em indexação humana.
        pivot_row: Linha escolhida como pivô, em indexação humana.
        swapped: Indica se ocorreu permuta de linhas.
        multipliers: Multiplicadores empregados abaixo do pivô.
        augmented: Matriz aumentada ao término da etapa.
    """

    column: int
    pivot_row: int
    swapped: bool
    multipliers: tuple[float, ...]
    augmented: np.ndarray


def gaussian_elimination_pivoting(matrix: np.ndarray, vector: np.ndarray) -> tuple[np.ndarray, list[EliminationStep]]:
    """Resolve Ax=b por eliminação de Gauss com pivotamento parcial.

    Args:
        matrix: Matriz quadrada dos coeficientes.
        vector: Vetor do lado direito.

    Returns:
        Vetor solução e histórico das etapas de eliminação.

    Raises:
        ValueError: Se for encontrado pivô nulo.
    """

    order = matrix.shape[0]
    augmented = np.column_stack((matrix.astype(float).copy(), vector.astype(float).copy()))
    steps: list[EliminationStep] = []
    for column in range(order - 1):
        pivot_index = column + int(np.argmax(np.abs(augmented[column:, column])))
        if np.isclose(augmented[pivot_index, column], 0.0):
            raise ValueError("O sistema não admite pivô não nulo nesta coluna.")
        swapped = pivot_index != column
        if swapped:
            augmented[[column, pivot_index]] = augmented[[pivot_index, column]]
        multipliers: list[float] = []
        for row in range(column + 1, order):
            multiplier = augmented[row, column] / augmented[column, column]
            multipliers.append(float(multiplier))
            augmented[row, column:] -= multiplier * augmented[column, column:]
        steps.append(EliminationStep(column + 1, pivot_index + 1, swapped, tuple(multipliers), augmented.copy()))
    if np.isclose(augmented[-1, -2], 0.0):
        raise ValueError("O sistema não admite pivô não nulo na última linha.")
    solution = np.zeros(order)
    for row in range(order - 1, -1, -1):
        solution[row] = (augmented[row, -1] - augmented[row, row + 1:order] @ solution[row + 1:order]) / augmented[row, row]
    return solution, steps


def system() -> tuple[np.ndarray, np.ndarray]:
    """Monta a matriz e o vetor do sistema apresentado no enunciado.

    Returns:
        Matriz A e vetor b da forma Ax=b.
    """

    matrix = np.array([
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0],
        [1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, -1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, -1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, -1.0],
    ])
    vector = np.array([0.0, -130.0, 102.0, 22.0, -1.0, 29.0, 38.0])
    return matrix, vector


def save_bar_chart(solution: np.ndarray, output_dir: Path) -> None:
    """Gera o gráfico de barras dos fluxos de voo desconhecidos.

    Args:
        solution: Vetor solução do sistema de voos.
        output_dir: Diretório de destino da figura.
    """

    figure, axis = plt.subplots(figsize=(7.2, 4.1))
    bars = axis.bar([f"$x_{index}$" for index in range(1, 8)], solution, color="0.35", edgecolor="black")
    axis.set_xlabel("Trecho desconhecido")
    axis.set_ylabel("Voos por dia")
    axis.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, solution):
        axis.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 2.0, f"{value:.0f}", ha="center", va="bottom")
    figure.tight_layout()
    figure.savefig(output_dir / "q2_voos_por_dia.png", dpi=220)
    plt.close(figure)


def format_matrix(matrix: np.ndarray) -> str:
    """Formata uma matriz para transcrição direta no relatório.

    Args:
        matrix: Matriz numérica a ser exibida.

    Returns:
        Linhas da matriz formatadas com seis casas decimais.
    """

    return "\n".join(" ".join(f"{value:12.6f}" for value in row) for row in matrix)


def main() -> None:
    """Executa o método, imprime a validação e salva a figura da questão."""

    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)
    matrix, vector = system()
    solution, steps = gaussian_elimination_pivoting(matrix, vector)
    residual = matrix @ solution - vector
    save_bar_chart(solution, output_dir)
    print("Solução:", np.array2string(solution, precision=12))
    print("Residual:", np.array2string(residual, precision=12))
    print(f"Norma 2 do residual: {np.linalg.norm(residual):.12e}")
    print(f"Número de condição 2 de A: {np.linalg.cond(matrix):.12f}")
    for step in steps[:3]:
        print(f"\nEtapa {step.column}: linha de pivô {step.pivot_row}, troca={step.swapped}, multiplicadores={step.multipliers}")
        print(format_matrix(step.augmented))


if __name__ == "__main__":
    main()
