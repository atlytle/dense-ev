[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=plastic)](https://opensource.org/licenses/Apache-2.0) [![arXiv](https://img.shields.io/badge/arXiv-2305.11847-b31b1b.svg?style=plastic)](https://arxiv.org/abs/2305.11847)
# dense_ev
**dense_ev** implements expectation value measurements in Qiskit using optimal
dense grouping [arXiv:quant-ph/2305.11847](https://arxiv.org/abs/2305.11847). 
For an $m$-qubit operator
that includes all Pauli strings in its decomposition, 
it provides a speedup of $2^m$ compared to naive evaluation of all strings,
and $(3/2)^m$ compared to grouping based on qubit-wise commuting (QWC) families.

## Installation
Create a virtual environment to sandbox the installation (optional):
```bash
python3 -m venv test-env && source ./test-env/bin/activate
```
<!--To install,
```bash
pip install dense-ev-->
```
Install from GitHub:
```bash
pip install git+ssh://git@github.com/atlytle/dense-ev.git
```
A test function comparing results using abelian and dense grouping
with exact results is available:
```python
from dense_ev.test_estimator import test_random

m = 3  # n_qubits
run_unit_tests(m)
```

### Qiskit version compatibility
**2024-01-07**: Support for dense Pauli grouping 
in the Aer `Estimator` primitive merged to `main` branch. 
See usage example below.  
**2024-05-30**: Functionality using `Opflow` and other deprecated classes
has been removed. Package requirements changed from `qiskit < 0.43.0` 
to `qiskit` (v1.0). Added `qiskit_aer` requirement.

## Usage
### Estimator support
The Aer implementation of `Estimator` is extended to incorporate
dense Pauli grouping, and can be invoked using the keyword
argument `abelian_grouping="DENSE"`. See `test_estimator.py`
for a more complete listing. <!--comparing no and abelian grouping.-->
```python
from dense_ev.estimator_from_aer import Estimator

...

# Dense result.
nshots = 200000
approx = False
grouping = "DENSE"
run_options = {"shots": nshots, "seed": seed}
estimator = Estimator(
    run_options=run_options, abelian_grouping=grouping, approximation=approx)
result_dense = estimator.run(state, H, shots=nshots).result().values

...

```
