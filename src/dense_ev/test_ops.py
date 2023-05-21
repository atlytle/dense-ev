#!/usr/bin/env python3
# Author: Andrew Lytle
# Dec 2022

# Copyright 2023 University of Illinois at Urbana-Champaign
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

import numpy as np

from qiskit import Aer
from qiskit.opflow import StateFn, DictStateFn, PauliExpectation, CircuitSampler
from qiskit.quantum_info import random_statevector
from qiskit.utils import QuantumInstance

from dense_ev.rmatrix import random_H, get_Op
from dense_ev.dense_pauli_expectation import DensePauliExpectation
    
def main(m, optype, name, nshots):
    seed = 42
    np.random.seed(seed)
    N = 2**m
    Hmat = random_H(N)

    logger.debug(Hmat)

    H = get_Op(Hmat, 'naive')

    sf = StateFn(H)
    sf = sf.adjoint()

    state = DictStateFn(random_statevector(2**m).to_dict())
    _eval = sf.eval(state)
    logger.info(f"Direct evaluation: {_eval}")

    logger.debug("Building PauliExpectation")
    if optype == 'naive':
        expectation = PauliExpectation(group_paulis=False).convert(sf.compose(state))
    if optype == 'abelian':
        expectation = PauliExpectation(group_paulis=True).convert(sf.compose(state))
    if optype == 'dense':
        expectation = DensePauliExpectation(group_paulis=True).convert(sf.compose(state))
    
    logger.debug(f"Using backend {name}")
    backend = get_backend(name)
    qi = QuantumInstance(backend, shots=nshots, optimization_level=3)
    sampler = CircuitSampler(qi, attach_results=True).convert(expectation)

    logger.info(f"Direct evaluation: {_eval}")
    logger.info('RESULT:', sampler.eval())

def unit_test(m):
    N = 2**m
    Hmat = random_H(N)
    H = get_Op(Hmat, 'naive')
    sf = StateFn(H)
    sf = sf.adjoint()
    state = DictStateFn(random_statevector(2**m).to_dict())
    direct_eval = sf.eval(state)
    
    expectation = DensePauliExpectation(group_paulis=True).convert(sf.compose(state))
    backend = Aer.get_backend('statevector_simulator')
    qi = QuantumInstance(backend)
    sampler = CircuitSampler(qi, attach_results=True).convert(expectation)
    new_eval = sampler.eval()
    print(f"{direct_eval = }")
    print(f"{new_eval = }")
    return np.isclose(new_eval, direct_eval.real)

def run_unit_tests():
    results = []
    for m in range(1,4):
        for test in range(1, 11):
            print(f"{m = } , {test = }")
            passed = unit_test(m)
            results.append(passed)
            if passed:
                continue
            else:
                print(f"Test failed with {m = }")
                break
        if not passed:
            break
    print(f"Performed {len(results)} tests, "
        f"all tests passed = {np.array(results).all()==True}")
   
if __name__ == "__main__":
    run_unit_tests()
    
