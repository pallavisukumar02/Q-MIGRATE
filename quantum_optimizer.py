import numpy as np


def run_qaoa_demo(df, budget=3):
    """
    Small transparent QAOA-style statevector simulation.

    This is a prototype quantum simulation for migration prioritization.
    It does NOT claim quantum advantage.
    """

    vulnerable = df[df["quantum_vulnerable"] == True].head(3).copy()

    if len(vulnerable) == 0:
        return {
            "selection": "No quantum-vulnerable assets found.",
            "circuit": "No circuit."
        }

    assets = vulnerable["asset"].tolist()
    scores = vulnerable["risk_score"].astype(float).tolist()

    n = len(assets)
    budget = min(int(budget), n)

    # Normalize risk scores
    max_score = max(scores) if scores else 1
    values = np.array(scores) / max_score

    # ---------------------------------------------------------
    # Tiny quantum statevector simulation
    # ---------------------------------------------------------

    # Start in |000...0>
    state = np.zeros(2 ** n, dtype=complex)
    state[0] = 1.0

    # Hadamard layer
    H = np.array([
        [1, 1],
        [1, -1]
    ], dtype=complex) / np.sqrt(2)

    for qubit in range(n):
        state = apply_single_qubit_gate(state, H, qubit, n)

    # Cost phase:
    # High-risk assets receive stronger phase weighting.
    for index in range(len(state)):
        bits = [(index >> q) & 1 for q in range(n)]
        selected = sum(bits)

        if selected <= budget:
            reward = sum(
                values[q] * bits[q]
                for q in range(n)
            )
            phase = np.exp(1j * np.pi * reward)
            state[index] *= phase
        else:
            # Penalize selections exceeding migration budget
            state[index] *= np.exp(-1j * np.pi)

    # Simple mixer layer
    theta = np.pi / 4

    RX = np.array([
        [np.cos(theta / 2), -1j * np.sin(theta / 2)],
        [-1j * np.sin(theta / 2), np.cos(theta / 2)]
    ], dtype=complex)

    for qubit in range(n):
        state = apply_single_qubit_gate(state, RX, qubit, n)

    # Measurement probabilities
    probabilities = np.abs(state) ** 2
    probabilities = probabilities / probabilities.sum()

    # Only consider bitstrings within migration budget
    valid_states = []

    for index, probability in enumerate(probabilities):
        bits = [(index >> q) & 1 for q in range(n)]

        if sum(bits) <= budget:
            valid_states.append((probability, bits))

    best_probability, best_bits = max(
        valid_states,
        key=lambda x: x[0]
    )

    selected_assets = [
        assets[i]
        for i, bit in enumerate(best_bits)
        if bit == 1
    ]

    if not selected_assets:
        # Always provide a useful migration candidate
        best_index = int(np.argmax(scores))
        selected_assets = [assets[best_index]]

    circuit = f"""
QAOA-STYLE MIGRATION OPTIMIZATION

Qubits: {n}
Migration budget: {budget}

Circuit:

|0> ──H──Phase──RX── Measure
|0> ──H──Phase──RX── Measure
|0> ──H──Phase──RX── Measure

Objective:
Maximize migration priority while respecting the migration budget.

Candidate assets:
{chr(10).join(f"q{i}: {asset} | risk={scores[i]}" for i, asset in enumerate(assets))}

Selected:
{chr(10).join(f"✓ {asset}" for asset in selected_assets)}

Simulation probability:
{best_probability:.4f}

Note:
This is a small local statevector simulation demonstrating the
quantum-optimization formulation. It is not a claim of quantum advantage.
"""

    return {
        "selection": selected_assets,
        "circuit": circuit
    }


def apply_single_qubit_gate(state, gate, qubit, n):
    """
    Apply a 2x2 gate to one qubit of an n-qubit statevector.
    """
    new_state = np.zeros_like(state)

    for index in range(2 ** n):
        bit = (index >> qubit) & 1

        if bit == 0:
            paired = index | (1 << qubit)

            new_state[index] += (
                gate[0, 0] * state[index]
                + gate[0, 1] * state[paired]
            )

            new_state[paired] += (
                gate[1, 0] * state[index]
                + gate[1, 1] * state[paired]
            )

    return new_state