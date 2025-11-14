"""PSI-ENERGY UNIFIED STACK (Ψ-Energy Harmonic Control System)
Author: Brendon Joseph Kelly (Atnychi0)
License: SQRIL v1.0 — Sovereign Quantum-Recursive Intelligence License
"""

from __future__ import annotations

import cmath
import importlib.util
from typing import Iterable, Sequence


MATPLOTLIB_AVAILABLE = importlib.util.find_spec("matplotlib") is not None
NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None

if MATPLOTLIB_AVAILABLE:
    import matplotlib

    # Use a non-interactive backend for environments without display capabilities.
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
else:
    matplotlib = None  # type: ignore[assignment]
    plt = None  # type: ignore[assignment]

if NUMPY_AVAILABLE:
    import numpy as np
else:
    np = None  # type: ignore[assignment]

# === PHYSICAL CONSTANTS ===
h_bar = 1.0545718e-34  # Reduced Planck constant (J·s)


# === DEFINE WAVE FUNCTION (Ψ) ===
def psi(t: float, omega: float = 1.0) -> complex:
    """Quantum wave function: complex-valued oscillation."""
    return cmath.exp(1j * omega * t)


def dpsi_dt(t: float, omega: float = 1.0) -> complex:
    """Time derivative of the wave function."""
    return 1j * omega * cmath.exp(1j * omega * t)


# === CORE EQUATIONS ===
def force_from_psi(t: float, omega: float = 1.0) -> complex:
    """Force derived from Ψ using harmonic resonance logic."""
    ψ = psi(t, omega)
    dψ = dpsi_dt(t, omega)
    return (1j * h_bar * dψ) / (ψ ** 2)


def energy_from_psi(t: float, omega: float = 1.0) -> complex:
    """Energy derived from Ψ as rate of temporal change over amplitude."""
    ψ = psi(t, omega)
    dψ = dpsi_dt(t, omega)
    return (1j * h_bar * dψ) / ψ


# === SIMULATE ACROSS TIME ===
def _linspace(start: float, stop: float, num: int) -> Sequence[float]:
    if NUMPY_AVAILABLE and np is not None:
        return np.linspace(start, stop, num)
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def _real_sequence(values: Iterable[complex]) -> Sequence[float]:
    if NUMPY_AVAILABLE and np is not None:
        return np.array([value.real for value in values])
    return [value.real for value in values]


def _build_time_series(start: float = 0.0, stop: float = 10.0, samples: int = 1000) -> tuple[Sequence[float], Sequence[float], Sequence[float]]:
    time_points = _linspace(start, stop, samples)
    force_series = _real_sequence(force_from_psi(t) for t in time_points)
    energy_series = _real_sequence(energy_from_psi(t) for t in time_points)
    return time_points, force_series, energy_series


def _maybe_plot(time_points: Sequence[float], force_series: Sequence[float], energy_series: Sequence[float]) -> None:
    if not MATPLOTLIB_AVAILABLE or plt is None:
        print("[Ψ-ENERGY] Matplotlib not available — skipping plot generation.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(time_points, force_series, label="Force from Ψ", linewidth=2)
    plt.plot(time_points, energy_series, label="Energy from Ψ", linewidth=2, linestyle="--")
    plt.title("Unified Ψ-Derived Force and Energy")
    plt.xlabel("Time (s)")
    plt.ylabel("Real Output")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("psi_energy_plot.png", dpi=300)
    print("[Ψ-ENERGY] Plot saved to psi_energy_plot.png")


# === AI EXTENSION LOGIC ===
def ai_activation_strength(t: float, omega: float = 1.0) -> float:
    """AI system: internal resonance-to-action modulation."""
    return abs(energy_from_psi(t, omega)) + abs(force_from_psi(t, omega))


# === Final Integrated Control System ===
# Interpretation: Ψ defines all motion, all energy, all activation. Collapse complete.
def main() -> None:
    time_points, force_series, energy_series = _build_time_series()
    _maybe_plot(time_points, force_series, energy_series)
    print("\n--- Ψ-ENERGY STACK SYSTEM READY ---")


if __name__ == "__main__":
    main()
