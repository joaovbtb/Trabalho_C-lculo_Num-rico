"""Resolve a equação de alcance do foguete pelos quatro métodos solicitados."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


TOLERANCE = 1e-5
MAX_ITERATIONS = 100


@dataclass(frozen=True)
class Iteration:
    """Representa um iterando e seu resíduo.

    Args:
        k: Número da iteração.
        theta: Aproximação do ângulo em radianos.
        residual: Valor de f(theta).
    """

    k: int
    theta: float
    residual: float


def f(theta: float) -> float:
    """Calcula a diferença entre o alcance e o alvo.

    Args:
        theta: Ângulo de lançamento em radianos.

    Returns:
        Resíduo do problema de raiz.
    """

    return 100.0**2 / 9.8 * (np.sin(theta) + 0.5 * np.sin(2.0 * theta)) - 1000.0


def df(theta: float) -> float:
    """Calcula a derivada analítica da função de alcance.

    Args:
        theta: Ângulo de lançamento em radianos.

    Returns:
        Derivada de f no ângulo informado.
    """

    return 100.0**2 / 9.8 * (np.cos(theta) + np.cos(2.0 * theta))


def bisection(function: Callable[[float], float], a: float, b: float) -> list[Iteration]:
    """Aplica bisseção a um intervalo com mudança de sinal.

    Args:
        function: Função escalar cujo zero será aproximado.
        a: Extremidade esquerda do intervalo inicial.
        b: Extremidade direita do intervalo inicial.

    Returns:
        Histórico de iterandos até a parada solicitada.

    Raises:
        ValueError: Se o intervalo inicial não tiver mudança de sinal.
    """

    fa = function(a)
    fb = function(b)
    if fa * fb >= 0.0:
        raise ValueError("O intervalo inicial não contém mudança de sinal.")
    history: list[Iteration] = []
    for k in range(1, MAX_ITERATIONS + 1):
        midpoint = (a + b) / 2.0
        fm = function(midpoint)
        history.append(Iteration(k, midpoint, fm))
        if abs(fm) < TOLERANCE:
            return history
        if fa * fm < 0.0:
            b, fb = midpoint, fm
        else:
            a, fa = midpoint, fm
    return history


def false_position(function: Callable[[float], float], a: float, b: float) -> list[Iteration]:
    """Aplica falsa posição, preservando um intervalo com mudança de sinal.

    Args:
        function: Função escalar cujo zero será aproximado.
        a: Extremidade esquerda do intervalo inicial.
        b: Extremidade direita do intervalo inicial.

    Returns:
        Histórico de iterandos até a parada solicitada.

    Raises:
        ValueError: Se o intervalo inicial não tiver mudança de sinal.
    """

    fa = function(a)
    fb = function(b)
    if fa * fb >= 0.0:
        raise ValueError("O intervalo inicial não contém mudança de sinal.")
    history: list[Iteration] = []
    for k in range(1, MAX_ITERATIONS + 1):
        estimate = a - fa * (b - a) / (fb - fa)
        fe = function(estimate)
        history.append(Iteration(k, estimate, fe))
        if abs(fe) < TOLERANCE:
            return history
        if fa * fe < 0.0:
            b, fb = estimate, fe
        else:
            a, fa = estimate, fe
    return history


def newton(function: Callable[[float], float], derivative: Callable[[float], float], x0: float) -> list[Iteration]:
    """Aplica o método de Newton com derivada analítica.

    Args:
        function: Função escalar cujo zero será aproximado.
        derivative: Derivada da função escalar.
        x0: Chute inicial.

    Returns:
        Histórico de iterandos até a parada solicitada.

    Raises:
        ZeroDivisionError: Se a derivada se anular em uma iteração.
    """

    x = x0
    history: list[Iteration] = []
    for k in range(1, MAX_ITERATIONS + 1):
        slope = derivative(x)
        if slope == 0.0:
            raise ZeroDivisionError("A derivada anulou durante a iteração de Newton.")
        x = x - function(x) / slope
        fx = function(x)
        history.append(Iteration(k, x, fx))
        if abs(fx) < TOLERANCE:
            return history
    return history


def secant(function: Callable[[float], float], x0: float, x1: float) -> list[Iteration]:
    """Aplica o método da secante com dois iterandos iniciais.

    Args:
        function: Função escalar cujo zero será aproximado.
        x0: Primeiro ponto inicial.
        x1: Segundo ponto inicial.

    Returns:
        Histórico de iterandos até a parada solicitada.

    Raises:
        ZeroDivisionError: Se a diferença de resíduos se anular.
    """

    previous, current = x0, x1
    history: list[Iteration] = []
    for k in range(1, MAX_ITERATIONS + 1):
        f_previous = function(previous)
        f_current = function(current)
        denominator = f_current - f_previous
        if denominator == 0.0:
            raise ZeroDivisionError("A diferença de resíduos anulou durante a secante.")
        following = current - f_current * (current - previous) / denominator
        f_following = function(following)
        history.append(Iteration(k, following, f_following))
        if abs(f_following) < TOLERANCE:
            return history
        previous, current = current, following
    return history


def save_plots(histories: dict[str, list[Iteration]], output_dir: Path) -> None:
    """Gera os dois gráficos de convergência solicitados.

    Args:
        histories: Históricos indexados pelo nome de cada método.
        output_dir: Diretório de destino das figuras.
    """

    styles = {
        "Bisseção": ("-", "o"),
        "Falsa posição": ("--", "s"),
        "Newton": ("-.", "^"),
        "Secante": (":", "D"),
    }
    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.25})
    figure, axis = plt.subplots(figsize=(7.2, 4.2))
    for name, history in histories.items():
        line, marker = styles[name]
        axis.plot([item.k for item in history], [item.theta for item in history], linestyle=line, marker=marker, markersize=4, label=name)
    axis.set_xlabel("Iteração k")
    axis.set_ylabel(r"$\theta_k$ [rad]")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "q1_theta_iteracoes.png", dpi=220)
    plt.close(figure)
    figure, axis = plt.subplots(figsize=(7.2, 4.2))
    for name, history in histories.items():
        line, marker = styles[name]
        axis.semilogy([item.k for item in history], [abs(item.residual) for item in history], linestyle=line, marker=marker, markersize=4, label=name)
    axis.set_xlabel("Iteração k")
    axis.set_ylabel(r"$|f(\theta_k)|$ [m]")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "q1_residuo_iteracoes.png", dpi=220)
    plt.close(figure)


def main() -> None:
    """Executa os métodos, salva as figuras e imprime o resumo numérico."""

    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)
    histories = {
        "Bisseção": bisection(f, 0.5, 1.5),
        "Falsa posição": false_position(f, 0.5, 1.5),
        "Newton": newton(f, df, 0.8),
        "Secante": secant(f, 0.7, 0.8),
    }
    save_plots(histories, output_dir)
    print(f"f(0.5) = {f(0.5):.12f}")
    print(f"f(1.5) = {f(1.5):.12f}")
    for name, history in histories.items():
        final = history[-1]
        status = "convergiu" if abs(final.residual) < TOLERANCE else "não convergiu"
        print(f"{name}: theta={final.theta:.12f} rad, graus={np.degrees(final.theta):.12f}, iteracoes={final.k}, residuo={final.residual:.12e}, {status}")


if __name__ == "__main__":
    main()
