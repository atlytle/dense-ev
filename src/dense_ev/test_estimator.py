#!/usr/bin/env python
# Andrew Lytle
# Sep 2023

from __future__ import annotations

import sys

import numpy as np

from qiskit.circuit.random import random_circuit
from qiskit.quantum_info import SparsePauliOp, PauliList
from qiskit import QuantumCircuit

# from qiskit_aer.primitives import Estimator

from dense_ev.estimator_from_aer import Estimator
from dense_ev.rmatrix import random_H, array_to_SparsePauliOp


def test_random(m):
    "Check different grouping methods with random Hamiltonians."
    N = 2**m
    seed = 42
    np.random.seed(seed)
    Hmat = random_H(N)
    H = array_to_SparsePauliOp(Hmat)

    # state = QuantumCircuit(2)
    # state.x(0)
    # state.h(0)
    state = random_circuit(m, 8, measure=True, seed=seed)

    # Get exact result.
    nshots = None
    approx = True
    grouping = False  # This flag doesn't matter here.
    run_options = {"shots": nshots, "seed": seed}
    estimator = Estimator(
        run_options=run_options, abelian_grouping=grouping, approximation=approx
    )
    result_exact = estimator.run(state, H, shots=nshots).result().values

    # Abelian result.
    nshots = 200000
    approx = False
    grouping = True
    run_options = {"shots": nshots, "seed": seed}
    estimator = Estimator(
        run_options=run_options, abelian_grouping=grouping, approximation=approx
    )
    result_abelian = estimator.run(state, H, shots=nshots).result().values

    # Dense result.
    nshots = 200000
    approx = False
    grouping = "DENSE"
    run_options = {"shots": nshots, "seed": seed}
    estimator = Estimator(
        run_options=run_options, abelian_grouping=grouping, approximation=approx
    )
    result_dense = estimator.run(state, H, shots=nshots).result().values

    print(f"{result_exact = }")
    print(f"{result_abelian = }")
    print(f"{result_dense = }")


if __name__ == "__main__":
    test_random(3)
