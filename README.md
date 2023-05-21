# dense_EV
**dense_ev** implements expectation value measurements in Qiskit using optimal
dense grouping [arXiv:quant-ph/2305.xxxx](). For an $m$-qubit operator
that includes all Pauli strings in its decomposition, 
it provides a speedup of $2^m$ compared to naive evaluation of all strings,
and $(3/2)^m$ compared to grouping based on qubit-wise commuting (QWC) families.

## Installation
Create a virtual environment to sandbox the installation (optional):
```bash
python3 -m venv test-env && source ./test-env/bin/activate
```
Install from GitHub:
```bash
pip install git+ssh://git@github.com/atlytle/dense-ev-test.git
```

### Qiskit version compatibility
Note that **dense_ev** specifies `qiskit < 0.43.0`, as the `Opflow` and
`QuantumInstance` packages have been deprecated as of `Qiskit 0.43.0`.
We plan to update the code to function with the new `primitives` as this 
migration continues and more documentation becomes available.

## Usage
Functionality for naive and QWC groupings is provided in Qiskit
by the `PauliExpectation` class. `DensePauliExpectation` extends the functionality
to dense optimal grouping, and may be used as a replacement for
`PauliExpectation`:
```python
from dense_EV import DensePauliExpectation

# Simple expectation values:
...

ev_spec = StateFn(H).compose(psi)
expectation = DensePauliExpectation().convert(ev_spec)

...

# VQE example
...

vqe = VQE(ansatz, optimizer=spsa, quantum_instance=qi,
          callback=store_intermediate_result, 
          expectation=DensePauliExpectation())

result = vqe.compute_minimum_eigenvalue(operator=H)

...


```

