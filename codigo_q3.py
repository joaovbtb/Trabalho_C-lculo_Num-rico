"""Resolve o sistema não linear do oleoduto por Newton-Raphson."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


TOLERANCE = 1e-5
MAX_ITERATIONS = 100


@dataclass(frozen=True)
class NewtonIteration:
    """Armazena um iterando de Newton para o sistema do oleoduto.

    Args:
        k: Número da iteração.
        x: Vetor [Delta p, Tin, Tout, mu_med].
        residual_norm: Norma euclidiana de F(x).
        step_norm: Norma do último passo de Newton.
        condition: Número de condição 2 da Jacobiana no iterando.
    """

    k: int
    x: np.ndarray
    residual_norm: float
    step_norm: float
    condition: float


def residual(x: np.ndarray) -> np.ndarray:
    """Calcula o vetor F(x) do modelo de operação do oleoduto.

    Args:
        x: Vetor [Delta p, Tin, Tout, mu_med].

    Returns:
        Vetor de quatro resíduos do sistema não linear.
    """

    delta_p, tin, tout, mu_med = x
    length = 32000.0
    diameter = 0.6
    area_surface = 60319.0
    mass_flow = 44.0
    ambient_temperature = 4.0
    source_temperature = 10.0
    density = 950.0
    velocity = 0.1638
    heat_capacity = 2100.0
    transfer_coefficient = 0.510
    pump_efficiency = 0.75
    electricity_cost = 0.17
    heating_cost = 0.05
    mean_temperature = (tin + tout) / 2.0
    return np.array([
        delta_p * 1e6 - 32.0 * mu_med * length * velocity / diameter**2,
        mass_flow * heat_capacity * (tin - tout) - transfer_coefficient * area_surface * ((tin - ambient_temperature + tout - ambient_temperature) / 2.0),
        6100.0 - delta_p * 1e6 * mass_flow / (pump_efficiency * density) / 1000.0 * electricity_cost * 24.0 - mass_flow * heat_capacity * (tin - source_temperature) / 1000.0 * heating_cost * 24.0,
        mu_med - 1100.0 * np.exp(-0.1 * mean_temperature),
    ])


def jacobian(x: np.ndarray) -> np.ndarray:
    """Calcula a Jacobiana analítica do sistema não linear.

    Args:
        x: Vetor [Delta p, Tin, Tout, mu_med].

    Returns:
        Matriz Jacobiana J(x).
    """

    _, tin, tout, _ = x
    length = 32000.0
    diameter = 0.6
    area_surface = 60319.0
    mass_flow = 44.0
    density = 950.0
    heat_capacity = 2100.0
    transfer_coefficient = 0.510
    pump_efficiency = 0.75
    electricity_cost = 0.17
    heating_cost = 0.05
    velocity = 0.1638
    exponential = np.exp(-0.1 * (tin + tout) / 2.0)
    return np.array([
        [1e6, 0.0, 0.0, -32.0 * length * velocity / diameter**2],
        [0.0, mass_flow * heat_capacity - transfer_coefficient * area_surface / 2.0, -mass_flow * heat_capacity - transfer_coefficient * area_surface / 2.0, 0.0],
        [-1e6 * mass_flow / (pump_efficiency * density) / 1000.0 * electricity_cost * 24.0, -mass_flow * heat_capacity / 1000.0 * heating_cost * 24.0, 0.0, 0.0],
        [0.0, 55.0 * exponential, 55.0 * exponential, 1.0],
    ])


def gaussian_elimination_pivoting(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """Resolve um sistema linear por Gauss com pivotamento parcial.

    Args:
        matrix: Matriz quadrada do sistema linear.
        vector: Vetor do lado direito.

    Returns:
        Solução do sistema linear.

    Raises:
        ValueError: Se um pivô nulo impedir a solução.
    """

    order = matrix.shape[0]
    augmented = np.column_stack((matrix.astype(float).copy(), vector.astype(float).copy()))
    for column in range(order - 1):
        pivot = column + int(np.argmax(np.abs(augmented[column:, column])))
        if np.isclose(augmented[pivot, column], 0.0):
            raise ValueError("Jacobiana singular durante a eliminação.")
        if pivot != column:
            augmented[[column, pivot]] = augmented[[pivot, column]]
        for row in range(column + 1, order):
            multiplier = augmented[row, column] / augmented[column, column]
            augmented[row, column:] -= multiplier * augmented[column, column:]
    solution = np.zeros(order)
    for row in range(order - 1, -1, -1):
        if np.isclose(augmented[row, row], 0.0):
            raise ValueError("Jacobiana singular durante a retrosubstituição.")
        solution[row] = (augmented[row, -1] - augmented[row, row + 1:order] @ solution[row + 1:order]) / augmented[row, row]
    return solution


def newton_raphson(initial: np.ndarray) -> tuple[list[NewtonIteration], str]:
    """Executa Newton-Raphson sem amortecimento para um chute inicial.

    Args:
        initial: Chute inicial para [Delta p, Tin, Tout, mu_med].

    Returns:
        Histórico de iterandos e situação da execução.
    """

    x = initial.astype(float).copy()
    initial_residual = residual(x)
    history = [NewtonIteration(0, x.copy(), float(np.linalg.norm(initial_residual)), 0.0, float(np.linalg.cond(jacobian(x))))]
    for k in range(1, MAX_ITERATIONS + 1):
        try:
            step = gaussian_elimination_pivoting(jacobian(x), -residual(x))
        except (ValueError, FloatingPointError, OverflowError):
            return history, "interrompido por Jacobiana singular ou não finita"
        x = x + step
        if not np.all(np.isfinite(x)):
            return history, "interrompido por iterado não finito"
        current_residual = residual(x)
        if not np.all(np.isfinite(current_residual)):
            return history, "interrompido por resíduo não finito"
        history.append(NewtonIteration(k, x.copy(), float(np.linalg.norm(current_residual)), float(np.linalg.norm(step)), float(np.linalg.cond(jacobian(x)))))
        if history[-1].residual_norm <= TOLERANCE:
            return history, "convergiu"
    return history, "não convergiu segundo o critério estabelecido"


def save_plots(histories: dict[str, list[NewtonIteration]], statuses: dict[str, str], output_dir: Path) -> None:
    """Gera os gráficos de trajetória somente para casos convergentes.

    Args:
        histories: Históricos indexados pelo nome de cada caso.
        statuses: Situações finais indexadas pelo nome de cada caso.
        output_dir: Diretório de destino das figuras.
    """

    converged = {name: history for name, history in histories.items() if statuses[name] == "convergiu"}
    for name, history in converged.items():
        indices = [item.k for item in history]
        vectors = np.array([item.x for item in history])
        figure, axis = plt.subplots(figsize=(7.2, 4.1))
        axis.plot(indices, vectors[:, 1], "-o", color="0.15", label=r"$T_{in}$")
        axis.plot(indices, vectors[:, 2], "--s", color="0.55", label=r"$T_{out}$")
        axis.set_xlabel("Iteração k")
        axis.set_ylabel("Temperatura [°C]")
        axis.grid(alpha=0.25)
        axis.legend()
        figure.tight_layout()
        figure.savefig(output_dir / f"q3_{name}_temperaturas.png", dpi=220)
        plt.close(figure)
        figure, axes = plt.subplots(2, 1, figsize=(7.2, 5.5), sharex=True)
        axes[0].plot(indices, vectors[:, 0], "-o", color="0.15")
        axes[0].set_ylabel(r"$\Delta p$ [MPa]")
        axes[0].grid(alpha=0.25)
        axes[1].plot(indices, vectors[:, 3], "--s", color="0.45")
        axes[1].set_xlabel("Iteração k")
        axes[1].set_ylabel(r"$\mu_{med}$ [Pa·s]")
        axes[1].grid(alpha=0.25)
        figure.tight_layout()
        figure.savefig(output_dir / f"q3_{name}_pressao_viscosidade.png", dpi=220)
        plt.close(figure)
    figure, axis = plt.subplots(figsize=(7.2, 4.1))
    for name, history in histories.items():
        axis.semilogy([item.k for item in history], [max(item.residual_norm, np.finfo(float).tiny) for item in history], "-o", markersize=3, label=name)
    axis.set_xlabel("Iteração k")
    axis.set_ylabel(r"$\|F(x_k)\|_2$")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "q3_residuo_iteracoes.png", dpi=220)
    plt.close(figure)


def main() -> None:
    """Executa os dois casos, salva os gráficos e imprime as validações."""

    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)
    cases = {
        "caso_1": np.array([1.0, 12.0, 10.0, 0.05]),
        "caso_2": np.array([15.0, 25.0, 10.0, 1.0]),
    }
    results = {name: newton_raphson(initial) for name, initial in cases.items()}
    histories = {name: result[0] for name, result in results.items()}
    statuses = {name: result[1] for name, result in results.items()}
    save_plots(histories, statuses, output_dir)
    for name, history in histories.items():
        final = history[-1]
        print(f"{name}: {statuses[name]}")
        print("x final:", np.array2string(final.x, precision=12))
        print("F(x final):", np.array2string(residual(final.x), precision=12))
        print(f"norma final: {final.residual_norm:.12e}, iteracoes: {final.k}, condicao J: {final.condition:.12e}")


if __name__ == "__main__":
    main()
